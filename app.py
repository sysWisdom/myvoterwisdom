from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys
import requests as http_client
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

# Simple process-level cache so we don't hammer the paid API on every page load.
# Reset by restarting the server.
_dq_cache = {}


def _ensure_model():
    """Pre-warm the global model cache so the first predict request is fast."""
    from main_vote2028 import preload_models
    preload_models()


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


@app.route('/predict-ec', methods=['GET'])
def predict_ec():
    """
    Run the global model over every county in the dataset and return
    state-by-state Electoral College projections.
    Heavy on first call (~15-30 s cold start); subsequent calls use the
    module-level cache and return in < 1 s.
    """
    try:
        from main_vote2028 import predict_all_counties
        output = predict_all_counties()
        return jsonify(output)
    except Exception as e:
        print(f"EC projection error: {e}")
        return jsonify({"error": "EC projection failed", "details": str(e)}), 500


@app.route('/data-quality', methods=['GET'])
def data_quality():
    """Proxy to the SysWisdom Data Quality API. Key never leaves the server."""
    if 'result' in _dq_cache:
        result = dict(_dq_cache['result'])
        result['cached'] = True
        return jsonify(result)

    api_key = os.environ.get('DATA_QUALITY_API_KEY')
    if not api_key:
        return jsonify({'error': 'Data Quality API not configured on this server'}), 503

    csv_path = os.path.join(_ROOT, 'data', 'prediction_pres_data.csv')
    if not os.path.exists(csv_path):
        return jsonify({'error': 'Prediction data file not found'}), 404

    try:
        with open(csv_path, 'rb') as f:
            resp = http_client.post(
                'https://data-quality-api-u2mjys756a-uc.a.run.app/analyze',
                headers={'X-API-Key': api_key},
                files={'file': ('prediction_pres_data.csv', f, 'text/csv')},
                timeout=30,
            )
        resp.raise_for_status()
        result = resp.json()
        _dq_cache['result'] = result
        return jsonify(result)
    except http_client.RequestException as e:
        return jsonify({'error': 'Data Quality API unreachable', 'details': str(e)}), 502
    except Exception as e:
        return jsonify({'error': 'Unexpected error', 'details': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)