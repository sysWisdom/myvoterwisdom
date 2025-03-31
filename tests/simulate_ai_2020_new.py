import pandas as pd

# Load the CSV file containing the voting data
file_path = 'data/voting_pres_data.csv'
df = pd.read_csv(file_path)

# Check if the file has been loaded correctly by displaying the first few rows
print(df.head())

# Ensure the necessary columns exist in the dataset
required_columns = ['Election Year', 'State', 'County', 'Total Registered Voters', 'Total Ballots Cast']
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"Missing required columns. Found columns: {df.columns}")

# Basic analysis: Calculate the voter turnout ratio (Total Ballots Cast / Total Registered Voters)
df['Voter Turnout Ratio'] = df['Total Ballots Cast'] / df['Total Registered Voters']

# Group by County and State to compare total ballots cast across years
county_turnout = df.groupby(['County', 'State'])[['Election Year', 'Total Ballots Cast', 'Voter Turnout Ratio']].agg({
    'Total Ballots Cast': ['min', 'max', 'mean'],
    'Voter Turnout Ratio': 'mean'
}).reset_index()

# Save the results into a new CSV file
county_turnout.to_csv('data/reasoning/county_turnout_analysis.csv', index=False)

# Display a preview of the results
print(county_turnout.head())
