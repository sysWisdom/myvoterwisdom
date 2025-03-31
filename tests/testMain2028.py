import unittest
import subprocess
import json
import os

class TestMain2028(unittest.TestCase):
    def test_main_vote2028(self):
        state = "CA"
        county = "Orange County"

        # Run the main_vote2028.py script with the provided state and county
        result = subprocess.run(
            ['python', '../main_vote2028.py', county, state],
            capture_output=True,
            text=True
        )

        # Print the output and error messages for debugging
        print(f"Script output: {result.stdout}")
        print(f"Script error (if any): {result.stderr}")

        # Check if the script ran successfully
        self.assertEqual(result.returncode, 0, f"Script failed with error: {result.stderr}")

        # Verify that results.json was created
        self.assertTrue(os.path.exists('../results.json'), "results.json file was not created")

        # Load the results.json file
        with open('../results.json', 'r') as f:
            output = json.load(f)

        # Verify the structure of the output
        self.assertIn("classification_reports", output, "Output missing 'classification_reports'")
        self.assertIn("predictions", output, "Output missing 'predictions'")

        # Verify the models in the output
        models = ['Random Forest', 'Logistic Regression', 'SVM', 'Gradient Boosting']
        for model in models:
            self.assertIn(model, output["classification_reports"], f"Missing classification report for {model}")
            self.assertIn(model, output["predictions"], f"Missing predictions for {model}")

        # Verify the content of the classification reports
        for model in models:
            report = output["classification_reports"][model]
            self.assertIn("accuracy", report, f"Missing accuracy in classification report for {model}")
            self.assertIn("macro avg", report, f"Missing macro avg in classification report for {model}")

        # Verify the predictions
        for model in models:
            predictions = output["predictions"][model]
            self.assertIsInstance(predictions, list, f"Predictions for {model} should be a list")

if __name__ == '__main__':
    unittest.main()