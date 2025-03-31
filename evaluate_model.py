import pandas as pd
import joblib
from sklearn.metrics import classification_report
from preprocess import add_filter_columns, compare_votes_and_ballots, update_wisdom, prepare_features_and_target
from sklearn.preprocessing import OneHotEncoder

def evaluate_model(model_path, data_path):
    """
    Evaluate the model by loading it from the model_path and evaluating on data from data_path.
    model_path: Path to the trained model.
    data_path: Path to the dataset CSV file.
    """
    # Load the model
    model = joblib.load(model_path)

    # Load the dataset
    df = pd.read_csv(data_path)

    # Apply preprocessing functions
    df = add_filter_columns(df)
    df = compare_votes_and_ballots(df)
    df = update_wisdom(df)

    # Prepare features and target
    X, y = prepare_features_and_target(df)

    # Identify categorical columns
    categorical_columns = X.select_dtypes(include=['object']).columns

    # Apply one-hot encoding to categorical columns
    encoder = OneHotEncoder(sparse_output=False, drop='first')
    X_encoded = pd.DataFrame(encoder.fit_transform(X[categorical_columns]), columns=encoder.get_feature_names_out(categorical_columns))

    # Drop original categorical columns and concatenate encoded columns
    X = X.drop(columns=categorical_columns)
    X = pd.concat([X, X_encoded], axis=1)

    # Evaluate the model
    y_pred = model.predict(X)
    report = classification_report(y, y_pred, output_dict=True, zero_division=0)
    print("Classification Report:")
    print(report)