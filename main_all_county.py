import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import joblib
from preprocess import load_data, add_filter_columns, compare_votes_and_ballots, update_wisdom, prepare_features_and_target

def train_and_save_model(data_path, model_path):
    """
    Train a Random Forest model and save it to the specified path.
    data_path: Path to the dataset CSV file.
    model_path: Path to save the trained model.
    """
    df = load_data(data_path)
    if df is None:
        return

    df = add_filter_columns(df)
    df = compare_votes_and_ballots(df)
    df = update_wisdom(df)

    X, y = prepare_features_and_target(df)

    categorical_columns = X.select_dtypes(include=['object']).columns
    encoder = OneHotEncoder(sparse_output=False, drop='first')
    X_encoded = pd.DataFrame(encoder.fit_transform(X[categorical_columns]), columns=encoder.get_feature_names_out(categorical_columns))

    X = X.drop(columns=categorical_columns)
    X = pd.concat([X, X_encoded], axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    print("Classification Report:")
    print(report)

def evaluate_model(model_path, data_path):
    """
    Evaluate the model by loading it from the model_path and evaluating on data from data_path.
    model_path: Path to the trained model.
    data_path: Path to the dataset CSV file.
    """
    model = joblib.load(model_path)

    df = load_data(data_path)
    if df is None:
        return

    df = add_filter_columns(df)
    df = compare_votes_and_ballots(df)
    df = update_wisdom(df)

    X, y = prepare_features_and_target(df)

    categorical_columns = X.select_dtypes(include=['object']).columns
    encoder = OneHotEncoder(sparse_output=False, drop='first')
    X_encoded = pd.DataFrame(encoder.fit_transform(X[categorical_columns]), columns=encoder.get_feature_names_out(categorical_columns))

    X = X.drop(columns=categorical_columns)
    X = pd.concat([X, X_encoded], axis=1)

    y_pred = model.predict(X)
    report = classification_report(y, y_pred, output_dict=True, zero_division=0)
    print("Classification Report:")
    print(report)

def run_pipeline():
    # Train and save model
    train_and_save_model('data/voting_pres_data.csv', 'model/rf_vote_model.pkl')
    
    # Evaluate the model
    evaluate_model('model/rf_vote_model.pkl', 'data/voting_pres_data.csv')

if __name__ == "__main__":
    run_pipeline()