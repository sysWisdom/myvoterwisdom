import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
import numpy as np
import json
import sys
import os
from preprocess import load_data, add_filter_columns, compare_votes_and_ballots, update_wisdom, prepare_features_and_target

def laplace_law_of_succession(wins, total_elections):
    return (wins + 1) / (total_elections + 2)

def main(county_name, state_name):
    # Load the dataset
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'voting_pres_data.csv')
    df = load_data(data_path)
    if df is None:
        return {"message": "Failed to load data"}

    # Filter for the selected county and state
    county_data = df[(df['County'] == county_name) & (df['State'] == state_name)].copy()

    # Check if the necessary columns are present
    required_columns = ['Democratic Votes', 'Republican Votes', 'Total Voted', 'Total Ballots Cast']
    for col in required_columns:
        if col not in county_data.columns:
            return {"message": f"Missing column: {col} in the data for {county_name}, {state_name}"}

    # Check if the filtered data is empty
    if county_data.empty:
        return {"message": f"No data found for {county_name}, {state_name}"}

    # Apply preprocessing functions
    county_data = add_filter_columns(county_data)
    county_data = compare_votes_and_ballots(county_data)
    county_data = update_wisdom(county_data)

    # Feature Engineering
    county_data.loc[:, 'Democratic Vote Share'] = county_data['Democratic Votes'] / county_data['Total Voted']
    county_data.loc[:, 'Republican Vote Share'] = county_data['Republican Votes'] / county_data['Total Voted']
    county_data.loc[:, 'Turnout'] = county_data['Total Ballots Cast'] / county_data['Total Registered Voters']

    # Predict outcome based on past voting behavior (1 = Democratic wins, 0 = Republican wins)
    county_data.loc[:, 'Democratic Wins'] = np.where(county_data['Democratic Vote Share'] > county_data['Republican Vote Share'], 1, 0)

    # Check if the data contains at least two classes
    if len(county_data['Democratic Wins'].unique()) < 2:
        # Determine the likely winner
        likely_winner = "Democratic" if county_data['Democratic Wins'].iloc[0] == 1 else "Republican"
        return {
            "message": f"The data contains only one class, indicating high accuracy for {county_name}, {state_name}. A {likely_winner} candidate is 100% likely to win the county.",
            "classification_reports": {},
            "predictions": {}
        }

    # Prepare the features (X) and target (y)
    X = county_data[['Democratic Vote Share', 'Republican Vote Share', 'Turnout']]
    y = county_data['Democratic Wins']

    # Check if the dataset is imbalanced
    class_counts = y.value_counts()
    print(f"Class distribution before SMOTE: {class_counts}")

    # Ensure there are enough samples in each class for train-test split and SMOTE
    if class_counts.min() < 2:
        # Apply Laplace Law of Succession
        total_elections = len(y)
        democratic_wins = class_counts.get(1, 0)
        republican_wins = class_counts.get(0, 0)
        democratic_prob = laplace_law_of_succession(democratic_wins, total_elections)
        republican_prob = laplace_law_of_succession(republican_wins, total_elections)
        
        # Debugging information
        print(f"Democratic Wins: {democratic_wins}, Republican Wins: {republican_wins}")
        print(f"Democratic Probability: {democratic_prob}, Republican Probability: {republican_prob}")
        
        likely_winner = "Democratic" if democratic_prob > republican_prob else "Republican"
        likely_winner_prob = max(democratic_prob, republican_prob) * 100
        
        # Debugging information
        print(f"Likely Winner: {likely_winner}, Likely Winner Probability: {likely_winner_prob}")
        
        return {
            "message": f"The least populated class in the data for {county_name}, {state_name} has only {class_counts.min()} member(s), which is too few. Using Laplace Law of Succession: Winner {likely_winner} with probability {likely_winner_prob:.2f}%",
            "likely_winner": likely_winner,
            "likely_winner_prob": likely_winner_prob,
            "classification_reports": {},
            "predictions": {}
        }

    # Apply SMOTE only if there are enough samples
    if class_counts.min() > 1:
        print("Applying SMOTE to balance the dataset...")
        smote = SMOTE(random_state=42, k_neighbors=min(5, class_counts.min() - 1))
        X, y = smote.fit_resample(X, y)
        print(f"Class distribution after SMOTE: {y.value_counts()}")
    else:
        print("Not enough samples to apply SMOTE. Skipping SMOTE step.")

    # Train-test split using stratified sampling
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Initialize models
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Logistic Regression': LogisticRegression(),
        'SVM': SVC(),
        'Gradient Boosting': GradientBoostingClassifier()
    }

    # Train and evaluate models
    results = {
        "classification_reports": {},
        "predictions": {}
    }

    for model_name, model in models.items():
        try:
            print(f"Training {model_name} model...")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
            print(f"Classification Report for {model_name}:")
            print(report)

            # Convert any np.int64 in the report to int
            for key, value in report.items():
                if isinstance(value, dict):
                    report[key] = {k: (int(v) if isinstance(v, np.integer) else v) for k, v in value.items()}
                else:
                    report[key] = int(value) if isinstance(value, np.integer) else value

            # Exclude "Group 0" if it has zero values for precision, recall, and f1-score
            if '0' in report and report['0']['precision'] == 0.0 and report['0']['recall'] == 0.0 and report['0']['f1-score'] == 0.0:
                del report['0']

            results["classification_reports"][model_name] = report
            results["predictions"][model_name] = y_pred.tolist()
        except Exception as e:
            print(f"Error training {model_name} model: {e}")

    return results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main_vote2028.py <county_name> <state_name>")
        sys.exit(1)
    county_name = sys.argv[1]
    state_name = sys.argv[2]
    output = main(county_name, state_name)
    if output:
        with open('results.json', 'w') as f:
            json.dump(output, f, indent=4)
        print("Results written to results.json")