"""
Fetch_County_Data.py — MEDSL Presidential County Returns Importer
=================================================================
Downloads and merges MIT Election Data and Science Lab (MEDSL)
county-level presidential returns into voting_pres_data.csv.

Data source (CC BY 4.0):
  MIT Election Data and Science Lab, "County Presidential Election Returns
  2000-2024", Harvard Dataverse, doi:10.7910/DVN/VOQCHQ

Usage:
  1. Download countypres_2000-2024.tab from Harvard Dataverse:
       https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VOQCHQ
     Click "Access Dataset" → fill guestbook (name/email/institution) → download .tab file
  2. Place the file at:  data/medsl/countypres_2000-2024.tab
  3. Run:  python Fetch_County_Data.py

Output:
  - Appends MEDSL rows to data/voting_pres_data.csv
  - Skips counties already present in manual data (our 39 curated counties)
  - Computes Wisdom flag for all new rows via preprocess.py logic
  - Adds Source column: 'manual' for existing rows, 'medsl' for new rows

MEDSL schema (tab-delimited):
  state, county_name, year, state_po, county_fips, office,
  candidate, party, candidatevotes, totalvotes, version, mode

Our target schema:
  Election Year, State, County, Total Registered Voters,
  Total Ballots Cast, Vote by Mail Ballots, Vote Center Ballots,
  Democratic Votes, Republican Votes, Total Voted, Wisdom, Source
"""

import os
import sys
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.abspath(__file__))
MEDSL_PATH = os.path.join(_ROOT, 'data', 'medsl', 'countypres_2000-2024.tab')
OUTPUT_PATH = os.path.join(_ROOT, 'data', 'voting_pres_data.csv')

# Election years to import (presidential elections within our mandate scope)
TARGET_YEARS = [2004, 2008, 2012, 2016, 2020, 2024]


def load_medsl(path: str) -> pd.DataFrame:
    """Load and validate the MEDSL tab-delimited file."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"\nMEDSL file not found: {path}\n\n"
            "Download instructions:\n"
            "  1. Go to https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VOQCHQ\n"
            "  2. Click 'Access Dataset' → fill guestbook form\n"
            "  3. Download 'countypres_2000-2024.tab'\n"
            f"  4. Place it at: {path}\n"
        )
    print(f"Loading MEDSL file: {path}")
    df = pd.read_csv(path, sep='\t', low_memory=False)
    print(f"  Raw rows: {len(df):,} | Columns: {list(df.columns)}")
    return df


def filter_and_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter to presidential races in target years, handle voting modes,
    and pivot from long (one row per candidate) to wide (one row per county-year).
    """
    # Step 1: presidential only, target years only
    df = df[
        (df['office'].str.upper() == 'PRESIDENT') &
        (df['year'].isin(TARGET_YEARS))
    ].copy()
    print(f"  After office+year filter: {len(df):,} rows")

    # Step 2: handle mode column
    # MEDSL uses mode='TOTAL' for the aggregated row in most years.
    # If TOTAL exists for a county-year, use only that; otherwise sum all modes.
    has_total = df[df['mode'].str.upper() == 'TOTAL'].groupby(
        ['year', 'state_po', 'county_name']
    ).ngroups
    total_groups = df.groupby(['year', 'state_po', 'county_name']).ngroups
    print(f"  County-year groups: {total_groups:,} | Groups with TOTAL mode: {has_total:,}")

    total_rows = df[df['mode'].str.upper() == 'TOTAL']
    non_total_rows = df[df['mode'].str.upper() != 'TOTAL']

    # Non-total county-years (need to be summed across modes)
    total_keys = set(zip(total_rows['year'], total_rows['state_po'], total_rows['county_name']))
    non_total_only = non_total_rows[~non_total_rows.apply(
        lambda r: (r['year'], r['state_po'], r['county_name']) in total_keys, axis=1
    )]
    if len(non_total_only) > 0:
        print(f"  Summing {len(non_total_only):,} rows from counties without TOTAL mode")
    df = pd.concat([total_rows, non_total_only], ignore_index=True)

    # Step 3: standardise party labels → DEMOCRAT / REPUBLICAN / OTHER
    df['party_std'] = df['party'].str.upper().str.strip()
    df['party_std'] = df['party_std'].apply(
        lambda p: 'DEMOCRAT' if 'DEMOCRAT' in p else ('REPUBLICAN' if 'REPUBLICAN' in p else 'OTHER')
    )

    # Step 4: aggregate votes by (year, state_po, county_name, county_fips, party_std, totalvotes)
    agg = df.groupby(
        ['year', 'state_po', 'county_name', 'county_fips', 'party_std'],
        as_index=False
    ).agg(candidatevotes=('candidatevotes', 'sum'), totalvotes=('totalvotes', 'first'))

    # Step 5: pivot party columns to wide format
    wide = agg.pivot_table(
        index=['year', 'state_po', 'county_name', 'county_fips', 'totalvotes'],
        columns='party_std',
        values='candidatevotes',
        aggfunc='sum'
    ).reset_index()
    wide.columns.name = None

    # Ensure both party columns exist even if a party has no votes in some county-year
    for col in ['DEMOCRAT', 'REPUBLICAN']:
        if col not in wide.columns:
            wide[col] = 0
    wide['DEMOCRAT'] = wide['DEMOCRAT'].fillna(0).astype(int)
    wide['REPUBLICAN'] = wide['REPUBLICAN'].fillna(0).astype(int)
    wide['totalvotes'] = wide['totalvotes'].fillna(0).astype(int)

    print(f"  Wide-format rows (county-years): {len(wide):,}")
    return wide


def map_to_schema(wide: pd.DataFrame) -> pd.DataFrame:
    """Map MEDSL wide-format columns to voting_pres_data.csv schema."""
    out = pd.DataFrame()
    out['Election Year'] = wide['year'].astype(int)
    out['State'] = wide['state_po'].str.upper()
    out['County'] = wide['county_name'].str.title()
    out['Total Registered Voters'] = 0       # not in MEDSL
    out['Total Ballots Cast'] = wide['totalvotes']
    out['Vote by Mail Ballots'] = 0           # not in MEDSL
    out['Vote Center Ballots'] = 0            # not in MEDSL
    out['Democratic Votes'] = wide['DEMOCRAT']
    out['Republican Votes'] = wide['REPUBLICAN']
    out['Total Voted'] = wide['totalvotes']
    out['Wisdom'] = 0                         # recomputed below
    out['Source'] = 'medsl'
    return out


def compute_wisdom(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recompute Wisdom flag for all rows using the county-level pivot logic
    from preprocess.py: Wisdom = True when county meets >= 2 of 3 conditions:
      - 2020 Dem votes > 2024 Dem votes
      - 2020 Dem votes > 2016 Dem votes
      - 2020 Total Ballots > 2024 Total Ballots
    """
    years_dem = [y for y in [2016, 2020, 2024] if y in df['Election Year'].values]
    years_bal = [y for y in [2020, 2024] if y in df['Election Year'].values]

    pdem = (
        df[df['Election Year'].isin(years_dem)]
        .pivot_table(index=['State', 'County'], columns='Election Year',
                     values='Democratic Votes', aggfunc='sum')
    )
    pbal = (
        df[df['Election Year'].isin(years_bal)]
        .pivot_table(index=['State', 'County'], columns='Election Year',
                     values='Total Ballots Cast', aggfunc='sum')
    )

    cond = pd.DataFrame(index=pdem.index)
    cond['c1'] = pdem[2020] > pdem[2024] if (2020 in pdem.columns and 2024 in pdem.columns) else False
    cond['c2'] = pdem[2020] > pdem[2016] if (2020 in pdem.columns and 2016 in pdem.columns) else False
    cond['c3'] = pbal[2020] > pbal[2024] if (2020 in pbal.columns and 2024 in pbal.columns) else False
    cond['Wisdom'] = (cond[['c1', 'c2', 'c3']].sum(axis=1) >= 2).astype(int)
    cond = cond[['Wisdom']].reset_index()

    df = df.drop(columns=['Wisdom'])
    df = df.merge(cond, on=['State', 'County'], how='left')
    df['Wisdom'] = df['Wisdom'].fillna(0).astype(int)
    return df


def merge_with_existing(existing: pd.DataFrame, new_rows: pd.DataFrame) -> pd.DataFrame:
    """
    Append MEDSL rows, skipping counties already in the manual dataset.
    The manual dataset takes precedence for any matching (County, State) pair.
    """
    # Tag existing rows as manual if not already tagged
    if 'Source' not in existing.columns:
        existing = existing.copy()
        existing['Source'] = 'manual'

    # Build set of (State, County) already covered by manual data
    manual_keys = set(zip(existing['State'].str.upper(), existing['County'].str.title()))

    new_rows_filtered = new_rows[~new_rows.apply(
        lambda r: (r['State'].upper(), r['County'].title()) in manual_keys, axis=1
    )].copy()
    skipped = len(new_rows) - len(new_rows_filtered)
    print(f"  Skipped {skipped:,} MEDSL rows covered by manual data")
    print(f"  Adding {len(new_rows_filtered):,} new MEDSL rows")

    combined = pd.concat([existing, new_rows_filtered], ignore_index=True)
    combined = combined.sort_values(['State', 'County', 'Election Year']).reset_index(drop=True)
    return combined


def main():
    print("=" * 60)
    print("MEDSL Presidential County Returns Importer")
    print("=" * 60)

    # 1. Load MEDSL source
    medsl_raw = load_medsl(MEDSL_PATH)

    # 2. Filter, handle modes, pivot to wide
    wide = filter_and_pivot(medsl_raw)

    # 3. Map to our schema
    new_rows = map_to_schema(wide)

    # 4. Load existing data
    print(f"\nLoading existing data: {OUTPUT_PATH}")
    existing = pd.read_csv(OUTPUT_PATH, encoding='utf-8-sig')
    print(f"  Existing rows: {len(existing):,} | Counties: {existing['County'].nunique()}")

    # 5. Merge (skip existing counties)
    print("\nMerging datasets...")
    combined = merge_with_existing(existing, new_rows)

    # 6. Recompute Wisdom for all rows
    print("\nRecomputing Wisdom flags...")
    combined = compute_wisdom(combined)

    # 7. Save
    combined.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved: {OUTPUT_PATH}")
    print(f"  Total rows: {len(combined):,}")
    print(f"  Total counties: {combined['County'].nunique():,}")
    print(f"  States: {combined['State'].nunique()}")
    print(f"  Years: {sorted(combined['Election Year'].unique())}")
    print(f"  Wisdom distribution: {combined['Wisdom'].value_counts().to_dict()}")

    by_source = combined['Source'].value_counts()
    print(f"\n  Source breakdown:")
    for src, cnt in by_source.items():
        print(f"    {src}: {cnt:,} rows")

    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"\n  File size: {size_kb:.0f} KB")
    print("\nDone. ✓")


if __name__ == '__main__':
    main()

    def __init__(self, app_token: str):
        """
        Initialize the King County Voter API client
        
        Args:
            app_token (str): Your Socrata API token
        """
        self.base_url = "https://data.kingcounty.gov"
        self.headers = {
            'X-App-Token': app_token,
            'Content-Type': 'application/json'
        }
    
    def get_election_results(self, dataset_id: str, params: Optional[Dict] = None) -> Dict:
        """
        Get election results from a specific dataset
        
        Args:
            dataset_id (str): The Socrata dataset identifier
            params (dict): Query parameters for filtering results
            
        Returns:
            dict: JSON response from the API
        """
        url = f"{self.base_url}/resource/{dataset_id}.json"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
    
    def get_voter_info(self, precinct: str) -> Dict:
        """
        Get voter information for a specific precinct
        
        Args:
            precinct (str): Precinct identifier
            
        Returns:
            dict: Voter information for the precinct
        """
        params = {
            '$where': f"precinct='{precinct}'",
            '$limit': 1000
        }
        # Note: You'll need to replace with the correct dataset ID
        return self.get_election_results('dataset-id-here', params)
    
    def get_presidential_results(self, year: int) -> Dict:
        """
        Get presidential election results for a specific year
        
        Args:
            year (int): Election year
            
        Returns:
            dict: Presidential election results
        """
        # Map of known dataset IDs for presidential elections
        dataset_map = {
            2008: 'av7y-ibxs',  # Example ID - replace with actual
            # Add more years as needed
        }
        
        if year not in dataset_map:
            raise ValueError(f"No dataset available for year {year}")
            
        return self.get_election_results(dataset_map[year])

# Example usage
def main():
    # Initialize the API client — token loaded from .env (SOCRATA_APP_TOKEN)
    app_token = os.environ.get('SOCRATA_APP_TOKEN', '')
    if not app_token or app_token == 'YOUR_APP_TOKEN_HERE':
        raise EnvironmentError(
            'SOCRATA_APP_TOKEN is not set. '
            'Register at https://dev.socrata.com/register and add it to .env'
        )
    api = KingCountyVoterAPI(app_token)
    
    # Example: Get 2008 presidential results
    results = api.get_presidential_results(2008)
    
    if results:
        # Process and format the results
        formatted_results = {
            "Election Year": 2008,
            "State": "Washington",
            "County": "King",
            "Democratic Votes": sum(int(r['votes']) for r in results if 'Obama' in r.get('candidate', '')),
            "Republican Votes": sum(int(r['votes']) for r in results if 'McCain' in r.get('candidate', '')),
        }
        print(json.dumps(formatted_results, indent=2))

if __name__ == "__main__":
    main()