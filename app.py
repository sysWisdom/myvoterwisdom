from flask import Flask, request, jsonify, send_from_directory
import subprocess
import json
import os

app = Flask(__name__, static_folder='static')

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
            ['python', 'main_vote2028.py', county, state],
            capture_output=True,
            text=True
        )

        # Debugging: Log the script output
        print(f"Script output: {result.stdout}")
        print(f"Script error (if any): {result.stderr}")

        # Check if the script ran successfully
        if result.returncode != 0:
            return jsonify({"error": "Script execution failed", "details": result.stderr}), 500

        # Read the results from results.json
        with open('results.json', 'r') as f:
            output = json.load(f)

        return jsonify(output)

    except Exception as e:
        # Debugging: Log the exception
        print(f"Exception occurred: {e}")
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)