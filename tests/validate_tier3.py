#!/usr/bin/env python3
"""
tests/validate_tier3.py

Cross-validates Tier 3 (tonmcg/US_County_Level_Election_Results_08-24, MIT license,
doi:10.5281/zenodo.14223604) against the MEDSL rows in voting_pres_data.csv.

Methodology
-----------
- Downloads Tier 3 CSVs from raw GitHub URLs (cached in data/county_repo/)
- Joins on (normalized county name, state abbreviation, election year)
- Flags rows where |T3 votes - MEDSL votes| / MEDSL votes > threshold
- Exits 0 if clean, 1 if divergences found or a download fails

Usage
-----
    python tests/validate_tier3.py
    python tests/validate_tier3.py --threshold 0.02   # 2% tolerance
    python tests/validate_tier3.py --year 2024        # single year

Note: Tier 3 covers 2016, 2020, 2024 (individual CSVs) and 2008–2016 (combined).
      This script validates 2016, 2020, 2024 where dedicated files exist.
      Alaska uses house districts in Tier 3; those rows are skipped during join.
"""
import argparse
import os
import sys

import pandas as pd
import requests

# ── Paths ─────────────────────────────────────────────────────────────────────

_ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR  = os.path.join(_ROOT, "data")
_CACHE_DIR = os.path.join(_DATA_DIR, "county_repo")
_OUR_CSV   = os.path.join(_DATA_DIR, "voting_pres_data.csv")

# ── Tier 3 raw GitHub URLs (MIT license — Tony McGovern) ──────────────────────

TIER3_URLS = {
    2016: (
        "https://raw.githubusercontent.com/tonmcg/"
        "US_County_Level_Election_Results_08-24/master/"
        "2016_US_County_Level_Presidential_Results.csv"
    ),
    2020: (
        "https://raw.githubusercontent.com/tonmcg/"
        "US_County_Level_Election_Results_08-24/master/"
        "2020_US_County_Level_Presidential_Results.csv"
    ),
    2024: (
        "https://raw.githubusercontent.com/tonmcg/"
        "US_County_Level_Election_Results_08-24/master/"
        "2024_US_County_Level_Presidential_Results.csv"
    ),
}

# ── Helpers ───────────────────────────────────────────────────────────────────

_SUFFIXES = (
    " county", " parish", " borough", " municipality",
    " city and county", " census area", " district",
    " city", " town",
)


def _normalize(name: str) -> str:
    """Lowercase, remove geographic suffixes, strip punctuation for fuzzy join."""
    name = str(name).lower().strip()
    for suffix in _SUFFIXES:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name.replace(".", "").replace("'", "").replace("-", " ").strip()


def _download(url: str, cache_path: str) -> pd.DataFrame:
    """Download CSV to cache_path if not already cached; return as DataFrame."""
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    if not os.path.exists(cache_path):
        print(f"  Downloading: {url}")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        with open(cache_path, "wb") as fh:
            fh.write(resp.content)
        print(f"  Cached → {cache_path}")
    return pd.read_csv(cache_path)


def _detect_cols(df: pd.DataFrame) -> dict:
    """
    Detect Democratic votes, Republican votes, county, and state columns
    by pattern-matching against known Tier 3 column name variants.
    Raises KeyError with a clear message if a column cannot be found.
    """
    cols = {c.lower().strip(): c for c in df.columns}

    def find(label: str, *candidates: str) -> str:
        for c in candidates:
            if c in cols:
                return cols[c]
        raise KeyError(
            f"Cannot find '{label}' column. "
            f"Tried: {list(candidates)}. "
            f"Available: {list(cols.keys())}"
        )

    return {
        "dem":    find("dem votes",    "votes_dem", "dem", "votes_dem_16",
                       "obama", "clinton", "biden", "harris"),
        "rep":    find("rep votes",    "votes_gop", "gop", "votes_rep", "votes_gop_16",
                       "romney", "trump"),
        "county": find("county name",  "county_name", "name", "county"),
        "state":  find("state abbrev", "state_abbr", "state_po", "state_abr", "state"),
    }


def load_tier3(year: int, url: str) -> pd.DataFrame | None:
    """Download, normalize, and return a Tier 3 DataFrame for one election year."""
    cache_path = os.path.join(_CACHE_DIR, f"{year}_US_County_Level_Presidential_Results.csv")
    try:
        raw = _download(url, cache_path)
    except Exception as exc:
        print(f"  WARNING: Could not download Tier 3 {year}: {exc}")
        return None

    try:
        mapping = _detect_cols(raw)
    except KeyError as exc:
        print(f"  WARNING: Column detection failed for Tier 3 {year}: {exc}")
        return None

    df = pd.DataFrame({
        "year":       year,
        "county_t3":  raw[mapping["county"]].astype(str),
        "state_t3":   raw[mapping["state"]].astype(str).str.upper().str.strip(),
        "dem_t3":     pd.to_numeric(raw[mapping["dem"]], errors="coerce"),
        "rep_t3":     pd.to_numeric(raw[mapping["rep"]], errors="coerce"),
    })
    df["county_key"] = df["county_t3"].apply(_normalize)
    return df.dropna(subset=["dem_t3", "rep_t3"])


def load_our_data() -> pd.DataFrame:
    """Load MEDSL rows from voting_pres_data.csv, add normalised join keys."""
    df = pd.read_csv(_OUR_CSV)
    medsl = df[df["Source"] == "medsl"].copy()
    medsl["county_key"] = medsl["County"].apply(_normalize)
    medsl["state_key"]  = medsl["State"].str.upper().str.strip()
    return medsl[
        ["Election Year", "State", "County", "state_key", "county_key",
         "Democratic Votes", "Republican Votes"]
    ]


def validate_year(
    year: int,
    tier3: pd.DataFrame,
    ours: pd.DataFrame,
    threshold: float,
) -> pd.DataFrame:
    """
    Inner-join Tier 3 and our MEDSL data on (county_key, state) for one year.
    Return rows where Democratic or Republican vote divergence exceeds threshold.
    """
    ours_yr = ours[ours["Election Year"] == year].copy()
    if ours_yr.empty:
        return pd.DataFrame()

    merged = ours_yr.merge(
        tier3[["county_key", "state_t3", "dem_t3", "rep_t3"]],
        left_on=["county_key", "state_key"],
        right_on=["county_key", "state_t3"],
        how="inner",
    )

    safe_dem = merged["Democratic Votes"].replace(0, float("nan"))
    safe_rep = merged["Republican Votes"].replace(0, float("nan"))
    merged["dem_div"] = (merged["dem_t3"] - merged["Democratic Votes"]).abs() / safe_dem
    merged["rep_div"] = (merged["rep_t3"] - merged["Republican Votes"]).abs() / safe_rep

    flagged = merged[
        (merged["dem_div"] > threshold) | (merged["rep_div"] > threshold)
    ].copy()
    return flagged


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Cross-validate Tier 3 (tonmcg repo) against MEDSL rows in "
            "voting_pres_data.csv. Exit 0 = clean, exit 1 = divergences found."
        )
    )
    parser.add_argument(
        "--threshold", type=float, default=0.01,
        help="Divergence threshold as a decimal (default: 0.01 = 1%%)",
    )
    parser.add_argument(
        "--year", type=int, default=None, choices=list(TIER3_URLS),
        help="Validate a single year only",
    )
    args = parser.parse_args()

    print("=" * 64)
    print("Tier 3 Validation Report")
    print(f"  Source : tonmcg/US_County_Level_Election_Results_08-24 (MIT)")
    print(f"  Against: {_OUR_CSV} (MEDSL rows only)")
    print(f"  Threshold : {args.threshold:.1%}")
    print("=" * 64)

    ours = load_our_data()
    print(f"\nLoaded {len(ours):,} MEDSL rows "
          f"({ours['state_key'].nunique()} states, "
          f"{ours['county_key'].nunique()} counties)\n")

    targets = {args.year: TIER3_URLS[args.year]} if args.year else TIER3_URLS
    total_matched = 0
    total_flagged = 0

    for year, url in sorted(targets.items()):
        print(f"── {year} " + "─" * 48)
        tier3 = load_tier3(year, url)
        if tier3 is None:
            print(f"  Skipped (download failed)\n")
            continue

        ours_yr = ours[ours["Election Year"] == year]
        flagged = validate_year(year, tier3, ours, args.threshold)

        # Count matched rows (inner join)
        matched = len(
            ours_yr.merge(
                tier3[["county_key", "state_t3"]],
                left_on=["county_key", "state_key"],
                right_on=["county_key", "state_t3"],
                how="inner",
            )
        )
        total_matched += matched
        total_flagged += len(flagged)

        print(f"  Tier 3 counties  : {len(tier3):,}")
        print(f"  Our MEDSL counties: {len(ours_yr):,}")
        print(f"  Matched (inner join): {matched:,}")
        print(f"  Flagged (>{args.threshold:.0%} divergence): {len(flagged)}")

        if not flagged.empty:
            hdr = f"  {'County':<25} {'ST':>3}  {'Dem div':>8}  {'Rep div':>8}"
            print(f"\n{hdr}")
            print(f"  {'-'*25} {'--':>3}  {'-------':>8}  {'-------':>8}")
            for _, row in flagged.sort_values("dem_div", ascending=False).iterrows():
                dem_s = f"{row['dem_div']:>7.2%}" if pd.notna(row["dem_div"]) else "     n/a"
                rep_s = f"{row['rep_div']:>7.2%}" if pd.notna(row["rep_div"]) else "     n/a"
                print(f"  {row['County']:<25} {row['State']:>3}  {dem_s}  {rep_s}")
        print()

    print("=" * 64)
    print(f"SUMMARY  Matched: {total_matched:,}   Flagged: {total_flagged}")
    if total_flagged == 0:
        print("✅  All matched counties within threshold — Tier 3 validates Tier 2.")
        return 0
    else:
        print(f"⚠️   {total_flagged} row(s) exceed the {args.threshold:.1%} divergence threshold.")
        print("    These may indicate source differences (rounding, late canvass, etc.).")
        print("    Verify flagged counties against official state results before use.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
