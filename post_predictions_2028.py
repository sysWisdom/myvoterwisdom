import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import os

# Define the paths to the data files
DATA_DIR = 'c:/Users/macki/Documents/VS Studio Code/WisdomAI_2020/data'
HISTORICAL_DATA_PATH = os.path.join(DATA_DIR, 'voting_pres_data.csv')
PREDICTION_DATA_PATH = os.path.join(DATA_DIR, 'prediction_pres_data.csv')

def load_data(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
    return pd.read_csv(filepath)

def make_projections(df, state, county):
    # Filter data for the specified state and county, excluding the year 2020
    county_data = df[(df['State'] == state) & (df['County'] == county) & (df['Election Year'] != 2020)]
    
    # Ensure there is enough data to make projections
    if len(county_data) < 2:
        print(f"Not enough data to make projections for {county}, {state}. Using synthetic data.")
        return make_synthetic_projections(df, state, county)
    
    # Prepare the data for linear regression
    X = county_data['Election Year'].values.reshape(-1, 1)
    y_total_voted = county_data['Total Voted'].values
    y_total_registered = county_data['Total Registered Voters'].values
    
    # Create and fit the linear regression model
    model_total_voted = LinearRegression().fit(X, y_total_voted)
    model_total_registered = LinearRegression().fit(X, y_total_registered)
    
    # Make projections for 2028
    year_2028 = np.array([[2028]])
    projected_total_voted = model_total_voted.predict(year_2028)[0]
    projected_total_registered = model_total_registered.predict(year_2028)[0]
    
    return {
        'Election Year': 2028,
        'State': state,
        'County': county,
        'Total Registered Voters': int(projected_total_registered),
        'Total Voted': int(projected_total_voted)
    }

def make_synthetic_projections(df, state, county):
    # Filter data for the specified state and county, excluding the year 2020
    county_data = df[(df['State'] == state) & (df['County'] == county) & (df['Election Year'] != 2020)]
    
    # Ensure there is data to work with
    if county_data.empty:
        print(f"No data available for {county}, {state}. Cannot make synthetic projections.")
        return None
    
    # Calculate the average annual growth rate of total registered voters
    county_data = county_data.sort_values(by='Election Year')
    county_data['Growth Rate'] = county_data['Total Registered Voters'].pct_change()
    avg_growth_rate = county_data['Growth Rate'].mean()
    
    # Use the last known value to project future values
    last_known_year = county_data['Election Year'].max()
    last_known_registered_voters = county_data[county_data['Election Year'] == last_known_year]['Total Registered Voters'].values
    last_known_voted = county_data[county_data['Election Year'] == last_known_year]['Total Voted'].values
    
    if len(last_known_registered_voters) == 0 or len(last_known_voted) == 0:
        print(f"Insufficient data to make synthetic projections for {county}, {state}.")
        return None
    
    last_known_registered_voters = last_known_registered_voters[0]
    last_known_voted = last_known_voted[0]
    
    # Project the values for 2028
    years_to_project = 2028 - last_known_year
    projected_total_registered = last_known_registered_voters * ((1 + avg_growth_rate) ** years_to_project)
    projected_total_voted = last_known_voted * ((1 + avg_growth_rate) ** years_to_project)
    
    return {
        'Election Year': 2028,
        'State': state,
        'County': county,
        'Total Registered Voters': int(projected_total_registered),
        'Total Voted': int(projected_total_voted)
    }

def update_csv(filepath, projection):
    # Load the existing data
    df = pd.read_csv(filepath)
    
    # Check if the projection already exists
    existing_projection = df[(df['Election Year'] == projection['Election Year']) & 
                             (df['State'] == projection['State']) & 
                             (df['County'] == projection['County'])]
    
    if not existing_projection.empty:
        # Update the existing projection
        df.loc[existing_projection.index, 'Total Registered Voters'] = projection['Total Registered Voters']
        df.loc[existing_projection.index, 'Total Voted'] = projection['Total Voted']
    else:
        # Append the new projection
        df = df.append(projection, ignore_index=True)
    
    # Save the updated data
    df.to_csv(filepath, index=False)
    print(f"Updated {filepath} with projections for {projection['County']}, {projection['State']} for 2028.")

def update_records(prediction_filepath, historical_filepath):
    # Load the prediction and historical data
    prediction_df = load_data(prediction_filepath)
    historical_df = load_data(historical_filepath)
    
    if prediction_df is None or historical_df is None:
        return
    
    # Filter historical data for the year 2024
    historical_2024 = historical_df[historical_df['Election Year'] == 2024]
    
    # Update the prediction data
    for index, row in prediction_df.iterrows():
        if row['Total Registered Voters'] == 0 or row['Total Voted'] == 0:
            state = row['State']
            county = row['County']
            
            # Find the corresponding record in the historical data
            historical_record = historical_2024[(historical_2024['State'] == state) & (historical_2024['County'] == county)]
            
            if not historical_record.empty:
                total_registered_voters = historical_record['Total Registered Voters'].values[0]
                total_voted = historical_record['Total Voted'].values[0]
                
                # Update the prediction record
                prediction_df.at[index, 'Total Registered Voters'] = total_registered_voters
                prediction_df.at[index, 'Total Voted'] = total_voted
    
    # Save the updated prediction data
    prediction_df.to_csv(prediction_filepath, index=False)
    print(f"Updated {prediction_filepath} with data from 2024.")

if __name__ == "__main__":
    state = "YourState"  # Replace with your state
    county = "YourCounty"  # Replace with your county
    
    # Load historical data
    historical_data = load_data(HISTORICAL_DATA_PATH)
    
    if historical_data is not None:
        # Make projections
        projection = make_projections(historical_data, state, county)
        
        if projection:
            # Update the CSV with the projections
            update_csv(PREDICTION_DATA_PATH, projection)
        
        # Update records with data from 2024
        update_records(PREDICTION_DATA_PATH, HISTORICAL_DATA_PATH)