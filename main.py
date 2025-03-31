from train_model import train_and_save_model
from evaluate_model import evaluate_model

def run_pipeline():
    # Train and save model
    train_and_save_model('data/voting_pres_data.csv', 'model/rf_vote_model.pkl')
    
    # Evaluate the model
    evaluate_model('model/rf_vote_model.pkl', 'data/voting_pres_data.csv')

if __name__ == "__main__":
    run_pipeline()
