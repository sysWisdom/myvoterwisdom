import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import os

# Define file paths
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
csv_path = os.path.join(_BASE_DIR, 'data', 'reasoning', 'simulated_questions.csv')
index_path = os.path.join(_BASE_DIR, 'data', 'reasoning', 'voter_questions.index')
csv_output_path = os.path.join(_BASE_DIR, 'data', 'reasoning', 'voter_questions_data.csv')

# Check if CSV file exists
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV file not found at {csv_path}")

# Load the CSV file
df = pd.read_csv(csv_path)

# Ensure column exists
if 'Prompt Text' not in df.columns:
    raise KeyError("Column 'Prompt Text:' not found in the CSV file. Check column headers.")

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode input questions into vectors
input_questions = df['Prompt Text'].tolist()
question_vectors = model.encode(input_questions)

# Create a FAISS index
dimension = question_vectors.shape[1]
index = faiss.IndexFlatL2(dimension)

# Add vectors to the index
index.add(question_vectors)

# Save the index to a file
faiss.write_index(index, index_path)

# Save DataFrame for reference
df.to_csv(csv_output_path, index=False)

print(f"Vector store 'Voter Questions' created successfully. Saved at '{index_path}'.")