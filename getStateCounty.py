import pandas as pd
import json

def main():
    # Load the dataset
    df = pd.read_csv('data/voting_pres_data.csv')

    # Extract unique states
    states = df['State'].unique().tolist()

    # Extract unique counties for each state
    counties_by_state = df.groupby('State')['County'].unique().apply(list).to_dict()

    # Write states to state.json
    with open('data/state.json', 'w') as state_file:
        json.dump(states, state_file, indent=4)

    # Write counties to county.json
    with open('data/county.json', 'w') as county_file:
        json.dump(counties_by_state, county_file, indent=4)

    print("state.json and county.json have been created successfully.")

if __name__ == "__main__":
    main()