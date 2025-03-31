import pandas as pd
from preprocess import compare_votes_and_ballots, update_wisdom, prepare_features_and_target

# Load the dataset
file_path = r'C:\Users\macki\Documents\VS Studio Code\WisdomAI_2020\data\voting_pres_data.csv'
df = pd.read_csv(file_path)

# Apply preprocessing functions
df = compare_votes_and_ballots(df)
df = update_wisdom(df)

# Check the distribution of the Wisdom column
print(df['Wisdom'].value_counts())

# Prepare features and target
X, y = prepare_features_and_target(df)