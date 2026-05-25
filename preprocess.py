import pandas as pd

def load_data(file_path):
    """Loads data from the given file path into a pandas DataFrame."""
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')  # utf-8-sig strips BOM
        df['Election Year'] = df['Election Year'].astype(int)
        if df['Wisdom'].dtype == object:
            df['Wisdom'] = df['Wisdom'].map({'True': True, 'False': False}).astype(bool)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def add_filter_columns(df):
    """Adds filter columns based on some conditions."""
    df['Filter'] = df['Total Ballots Cast'] > 1000000
    return df

def compare_votes_and_ballots(df):
    """Compares votes and ballots across election years at the county level.

    The previous row-by-row lambda approach always produced False because it
    compared each row against itself (None > value == False). The correct
    approach pivots to county level, computes cross-year comparisons once per
    county, then merges the result back to every row for that county.
    """
    # Build county-level pivot for Democratic Votes (need 2016, 2020, 2024)
    years_dem = [y for y in [2016, 2020, 2024] if y in df['Election Year'].values]
    pdem = (
        df[df['Election Year'].isin(years_dem)]
        .pivot_table(index='County', columns='Election Year',
                     values='Democratic Votes', aggfunc='sum')
    )

    # Build county-level pivot for Total Ballots Cast (need 2020, 2024)
    years_bal = [y for y in [2020, 2024] if y in df['Election Year'].values]
    pbal = (
        df[df['Election Year'].isin(years_bal)]
        .pivot_table(index='County', columns='Election Year',
                     values='Total Ballots Cast', aggfunc='sum')
    )

    cond = pd.DataFrame(index=pdem.index)
    cond['Votes 2020 > Votes 2024'] = (
        pdem[2020] > pdem[2024]
        if (2020 in pdem.columns and 2024 in pdem.columns)
        else False
    )
    cond['Votes 2020 > Votes 2016'] = (
        pdem[2020] > pdem[2016]
        if (2020 in pdem.columns and 2016 in pdem.columns)
        else False
    )
    cond['Ballots 2020 > Ballots 2024'] = (
        pbal[2020] > pbal[2024]
        if (2020 in pbal.columns and 2024 in pbal.columns)
        else False
    )

    # Merge county-level conditions back to every row (all election years)
    cond = cond.reset_index()
    # Drop old comparison columns if they already exist (re-run safe)
    old_cols = ['Votes 2020 > Votes 2024', 'Votes 2020 > Votes 2016',
                'Ballots 2020 > Ballots 2024']
    df = df.drop(columns=[c for c in old_cols if c in df.columns])
    df = df.merge(cond, on='County', how='left')
    # Fill False for counties missing 2016/2020/2024 data
    for col in old_cols:
        df[col] = df[col].fillna(False)
    return df

def update_wisdom(df):
    """Updates the Wisdom column based on the filter conditions."""
    df['Wisdom'] = df[['Votes 2020 > Votes 2024', 'Votes 2020 > Votes 2016', 'Ballots 2020 > Ballots 2024']].sum(axis=1) >= 2
    return df

def prepare_features_and_target(df):
    """Prepares features (X) and target variable (y) for model training."""
    X = df[['Total Registered Voters', 'Total Ballots Cast', 'Democratic Votes', 'Republican Votes']]
    y = df['Wisdom']
    return X, y