from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()  # reads .env if present; no-op in production where env vars are set directly

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(32))

# Allow requests from the GitHub Pages frontend
CORS(app, origins=[
    'https://myvoter.syswisdom.ai',
    'http://localhost:5000',
    'http://127.0.0.1:5000',
])

_ROOT = os.path.dirname(os.path.abspath(__file__))


def _ensure_model():
    """Train the RF model if it hasn't been trained yet (first deploy or cold start)."""
    model_path = os.path.join(_ROOT, 'model', 'rf_vote_model.pkl')
    if not os.path.exists(model_path):
        print('Model not found — training now...')
        os.makedirs(os.path.join(_ROOT, 'model'), exist_ok=True)
        from train_model import train_and_save_model
        train_and_save_model(
            os.path.join(_ROOT, 'data', 'voting_pres_data.csv'),
            model_path,
        )
        print('Model trained and saved.')


_ensure_model()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/data/<path:filename>')
def data_files(filename):
    return send_from_directory('data', filename)

@app.route('/predict', methods=['GET'])
def predict():
    state = request.args.get('state')
    county = request.args.get('county')

    if not state or not county:
        return jsonify({"error": "state and county are required"}), 400

    print(f"Received state: {state}, county: {county}")

    try:
        from main_vote2028 import main as run_prediction
        output = run_prediction(county, state)
        if output is None:
            return jsonify({"error": "Prediction returned no results"}), 500
        return jsonify(output)
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)