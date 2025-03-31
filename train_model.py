import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import joblib
from sklearn.metrics import classification_report
from preprocess import add_filter_columns, compare_votes_and_ballots, update_wisdom, prepare_features_and_target

def train_and_save_model(data_path, model_path):
    """
    Train a Random Forest model and save it to the specified path.
    data_path: Path to the dataset CSV file.
    model_path: Path to save the trained model.
    """
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

    # Split the dataset into training and testing sets using stratified sampling
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Train the Random Forest model
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Save the trained model
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

    # Evaluate the model
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    print("Classification Report:")
    print(report)