import pandas as pd

def load_data(file_path):
    """Loads data from the given file path into a pandas DataFrame."""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def add_filter_columns(df):
    """Adds filter columns based on some conditions."""
    df['Filter'] = df['Total Ballots Cast'] > 1000000
    return df

def compare_votes_and_ballots(df):
    """Compares votes and ballots for different years and returns a DataFrame with comparison columns."""
    df['Votes 2020 > Votes 2024'] = df.apply(
        lambda row: row['Democratic Votes'] if row['Election Year'] == 2020 else None,
        axis=1
    ) > df.apply(
        lambda row: row['Democratic Votes'] if row['Election Year'] == 2024 else None,
        axis=1
    )

    df['Votes 2020 > Votes 2016'] = df.apply(
        lambda row: row['Democratic Votes'] if row['Election Year'] == 2020 else None,
        axis=1
    ) > df.apply(
        lambda row: row['Democratic Votes'] if row['Election Year'] == 2016 else None,
        axis=1
    )

    df['Ballots 2020 > Ballots 2024'] = df.apply(
        lambda row: row['Total Ballots Cast'] if row['Election Year'] == 2020 else None,
        axis=1
    ) > df.apply(
        lambda row: row['Total Ballots Cast'] if row['Election Year'] == 2024 else None,
        axis=1
    )
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