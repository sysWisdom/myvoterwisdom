# MyVoterWisdom

> **This project is a non-partisan, educational research tool.**
> It is not intended to influence elections, predict future outcomes,
> or be used for political campaigning. Data reflects public historical
> records only. This project is free, open-source, and will never be monetized.
>
> See [DISCLAIMER.md](DISCLAIMER.md) for full data sources, model limitations, and use restrictions.

---

## Why We Built This

In 2020, a small team at SysWisdom set out to understand a simple question: *what does
historical county-level voting data actually tell us?* We built a machine learning
pipeline on top of publicly available presidential election records to explore turnout
patterns, vote share trends, and the "wisdom" hidden in aggregated civic participation.

The project was shelved when the political climate made any election-adjacent work feel
polarizing — even purely analytical, non-partisan work. We are now sharing it openly
because we believe civic data education belongs to everyone. There is no commercial angle.
There is no agenda. The code is here so researchers, educators, and curious citizens can
learn from it, improve it, or build something better.

If you find it useful, we only ask that you keep that same spirit of openness.

---

## Features

- Predict county-level election outcomes using historical presidential voting data (2016–2024)
- Multiple ML models: Random Forest, Gradient Boosting, Logistic Regression, SVM
- Voter turnout trend analysis across election cycles
- AI-powered simulated Q&A on election-related queries (FAISS vector store)
- Flask web app with county/state selector and visual results
- Supports adding new counties and states dynamically

---

## Project Structure

```
myvoterwisdom/
├── app.py                     # Flask web server — main entry point
├── main.py                    # Train + evaluate pipeline runner
├── main_vote2028.py           # County prediction script (called by app.py)
├── main_all_county.py         # Batch prediction across all counties
├── preprocess.py              # Data cleaning & feature engineering
├── train_model.py             # Random Forest model training
├── evaluate_model.py          # Model evaluation & classification report
├── post_predictions_2028.py   # Linear regression projections for 2028
├── getStateCounty.py          # Builds county.json & state.json from CSV
├── Fetch_County_Data.py       # Utility to fetch county data
├── requirements.txt           # Python dependencies
│
├── data/
│   ├── voting_pres_data.csv   # Historical presidential voting data (source of truth)
│   ├── prediction_pres_data.csv
│   ├── county.json            # Generated county lookup
│   ├── state.json             # Generated state lookup
│   ├── reasoning/             # AI simulation & Q&A training data
│   │   ├── simulated_questions.csv
│   │   ├── voter_questions.index  # FAISS index
│   │   └── county_turnout_analysis.csv
│   └── vectorStore/
│       └── voterQuestions.py  # Builds FAISS vector store from Q&A CSV
│
├── static/
│   ├── index.html             # Web app frontend
│   └── styles.css
│
├── image/                     # Screenshots and visualizations
├── model/                     # Saved trained models (joblib)
├── tests/                     # Test suite
│   ├── testMain2028.py        # unittest for county prediction
│   ├── verify_wisdom.py       # Wisdom column distribution check
│   ├── verify_preprocessing.py
│   ├── simulate_ai_2020_new.py
│   └── incompletness.py
└── results.json               # Latest prediction output
```

---

## Run in Google Colab (Free)

No local install required. Click a badge to open the notebook directly in Colab
using the `myvoterwisdom-497415` project environment.

| Notebook | Purpose | Open |
|---|---|---|
| 01 — Explore Data | Load & visualize `voting_pres_data.csv` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sysWisdom/myvoterwisdom/blob/main/notebooks/01_explore_data.ipynb) |
| 02 — Train Model | Step-by-step preprocessing & Random Forest training | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sysWisdom/myvoterwisdom/blob/main/notebooks/02_train_model.ipynb) |
| 03 — Predict County | Interactive county/state prediction with 4 models | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sysWisdom/myvoterwisdom/blob/main/notebooks/03_predict_county.ipynb) |

> Each notebook auto-clones this repo and installs dependencies on first run.
> Runtime → Change runtime type → T4 GPU is available on the free tier.

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- pip

### 1. Clone the repository
```bash
git clone https://github.com/sysWisdom/myvoterwisdom.git
cd myvoterwisdom
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the web app
```bash
python app.py
```
Open your browser to `http://127.0.0.1:5000`, select a state and county, and click **Predict**.

---

## Runbook

1. **`data/voting_pres_data.csv`** is the source of truth — update it when new county records
   are available (columns: `Election Year`, `State`, `County`, `Total Registered Voters`,
   `Total Ballots Cast`, `Democratic Votes`, `Republican Votes`, `Total Voted`).

2. **To get county predictions:**
   ```bash
   python app.py          # starts the web server
   # OR run directly:
   python main_vote2028.py "Orange County" CA
   # Results are written to results.json
   ```
   > If only one data record exists for a county, the model cannot train — you will get
   > a 100% accuracy message, which means insufficient data, not a real result.

3. **When a new county is added to the CSV:**
   ```bash
   python getStateCounty.py    # rebuilds county.json and state.json
   python main_all_county.py   # runs predictions for all counties
   ```

4. **AI simulation files** (`data/reasoning/`, `data/vectorStore/`) contain training data
   for the FAISS-based Q&A layer. Run `data/vectorStore/voterQuestions.py` to rebuild the
   index after updating `simulated_questions.csv`.

5. **Tests:**
   ```bash
   python -m pytest tests/testMain2028.py -v
   python tests/verify_wisdom.py
   python tests/verify_preprocessing.py
   ```

---

## License

Copyright © 2024 SysWisdom.AI LLC. Licensed under the **BSD 3-Clause License**.

**What this means in plain language:**

| You CAN | You CANNOT |
|---|---|
| Use this code freely, including in your own projects | Use the SysWisdom name to endorse your product without permission |
| Modify and redistribute the code | Remove the copyright notice from redistributed copies |
| Use it commercially (though we ask you don't monetize election data irresponsibly) | Hold SysWisdom liable for any outcomes |
| Publish research or educational material based on this work | |

See the [LICENSE](LICENSE) file for the full legal text.

---

## Contributing

We welcome contributions that advance civic education and data transparency.
Please read our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.
Open an issue before submitting a pull request so we can discuss the change.

**We will not merge contributions that:**
- Add predictive features intended for use in active political campaigns
- Introduce any form of monetization or user tracking
- Include personally identifiable voter information

---

## Screenshots

### Web App
![Voter Trends](image/voter-trends.svg)

![Logo](image/LogoMyvoterWisdom.png)