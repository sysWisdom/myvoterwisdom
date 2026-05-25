from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
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

    # Debugging: Log the received parameters
    print(f"Received state: {state}, county: {county}")

    try:
        # Run the main_vote2028.py script with the provided state and county
        result = subprocess.run(
            [sys.executable, os.path.join(_ROOT, 'main_vote2028.py'), county, state],
            capture_output=True,
            text=True,
            cwd=_ROOT,
        )

        # Debugging: Log the script output
        print(f"Script output: {result.stdout}")
        print(f"Script error (if any): {result.stderr}")

        # Check if the script ran successfully
        if result.returncode != 0:
            return jsonify({"error": "Script execution failed", "details": result.stderr}), 500

        # Read the results from results.json
        with open(os.path.join(_ROOT, 'results.json'), 'r') as f:
            output = json.load(f)

        return jsonify(output)

    except Exception as e:
        # Debugging: Log the exception
        print(f"Exception occurred: {e}")
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)