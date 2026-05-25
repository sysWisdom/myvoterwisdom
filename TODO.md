# WisdomAI_2020 — Responsible Open-Source Release TODO

> **Mission**: Share this election-data research project as a free, non-partisan,
> educational resource. No monetization. No political agenda.

## Google Cloud — myvoterwisdom Project

> Status as of 2026-05-25
>
> | Setting | Value |
> |---|---|
> | **Project ID** | `myvoterwisdom-497415` |
> | **Project Name** | myvoterwisdom |
> | **Project Number** | 291816933732 |
> | **Account** | `[redacted — see .env]` |
> | **gcloud config** | ✅ Set and confirmed active |
> | **ADC quota project** | ⚠️ Needs `gcloud auth application-default login` |

### GCloud Next Steps
- [ ] Run `gcloud auth application-default login` to refresh ADC tokens
- [ ] Enable required APIs:
  - `gcloud services enable run.googleapis.com`
  - `gcloud services enable storage.googleapis.com`
  - `gcloud services enable firebasehosting.googleapis.com`
- [ ] Create Cloud Storage bucket for data: `gsutil mb gs://myvoterwisdom-data`
- [ ] Upload `data/voting_pres_data.csv` to bucket
- [ ] Decide on database: **Cloud Firestore** (free tier, NoSQL) vs **Cloud SQL** (PostgreSQL, small cost)

---

## Test Results — 2026-05-25

| Test File | Type | Result | Notes |
|---|---|---|---|
| `tests/testMain2028.py` | `unittest` | ✅ PASSED | Orange County, CA prediction ran; `results.json` valid |
| `tests/verify_wisdom.py` | script | ✅ PASSED | `Wisdom=False` for all 233 records |
| `tests/verify_preprocessing.py` | script | ✅ PASSED | Same result — confirms preprocess pipeline |
| `tests/incompletness.py` | script | ✅ PASSED | ~500/1000 True values (random simulation) |
| `tests/simulate_ai_2020_new.py` | script | ⚠️ NOT RUN | Requires CWD=project root, uses `data/` relative path |

### Test Fixes Applied
- `tests/verify_wisdom.py` — fixed hardcoded path + `sys.path.append` → `sys.path.insert(0,...)`
- `tests/verify_preprocessing.py` — added `sys.path.insert`, fixed hardcoded path
- `tests/testMain2028.py` — fixed `'../main_vote2028.py'` subprocess path + `'../results.json'` path using `__file__`-relative `_ROOT`

### Wisdom Model Observation
> All 233 county records evaluate to `Wisdom=False`. This means no county in the dataset
> meets 2 of 3 conditions (2020 votes > 2024, 2020 votes > 2016, 2020 ballots > 2024 ballots).
> This may be expected given 2024 turnout data — worth reviewing the `update_wisdom` logic
> in `preprocess.py` if the model yields 100% accuracy warnings.

---



### 1.1 Remove Hardcoded Personal Paths
- [x] `main_vote2028.py` — replaced absolute path with `os.path.join(os.path.dirname(os.path.abspath(__file__)), ...)`
- [x] `post_predictions_2028.py` — same fix applied to `DATA_DIR`
- [x] `data/vectorStore/voterQuestions.py` — fixed `csv_path`, `index_path`, `csv_output_path`

### 1.2 Security & Privacy
- [x] Confirm `data/voting_pres_data.csv` contains only **public** election data (no PII) — 233 records, county-level aggregates only
- [x] Confirm `data/reasoning/` files contain no personally identifiable information — simulated Q&A + public turnout stats
- [x] Remove any API keys, credentials, or tokens — `Fetch_County_Data.py` uses `YOUR_APP_TOKEN_HERE` placeholder only
- [x] Updated `.gitignore`: added `*.pkl`, `model/`, `.env`, `.env.*`, `*.pem`, `*.key`, `*.joblib`
- [x] Untracked `model/rf_vote_model.pkl` (pickle deserialization risk), `results.json`, `data/reasoning/voter_questions.index` via `git rm --cached`

### 1.3 Dependencies
- [x] Fix `requirements.txt` — re-created as clean UTF-8 with all 9 project dependencies
- [x] Pin versions for reproducibility — exact versions set: Flask 3.0.0, pandas 2.2.3, scikit-learn 1.5.2, imbalanced-learn 0.13.0, numpy 2.1.3, joblib 1.4.2, faiss-cpu 1.10.0, sentence-transformers 3.4.1, requests 2.32.5

---

## Phase 2 — Responsible Framing & Documentation

### 2.1 Rewrite README.md
- [x] Add a **Disclaimer** section at the top
- [x] Clarify the BSD 3-Clause license and what it permits (plain-language table)
- [x] Replace scaffold `<repository-url>` with `https://github.com/sysWisdom/myvoterwisdom`
- [x] Fix project structure tree to match actual files
- [x] Add a "Why We Built This" section explaining the educational intent

### 2.2 Add a CODE_OF_CONDUCT.md
- [x] Use the [Contributor Covenant](https://www.contributor-covenant.org/) template
- [x] Explicitly state the project will not be used for targeted political advertising

### 2.3 Add a DISCLAIMER.md
- [x] Data sources cited (public election records — 39 counties, 25 states, 2004–2024)
- [x] Model limitations clearly stated (7 documented limitations including single-class Wisdom issue)
- [x] "Not for use in active campaigns" statement

---

## Phase 3 — Google Colab Migration

> **Recommendation: Use Google Colab (free) — not Jupyter Labs locally**
>
> You already have a Google Cloud account. Here is the free-tier path:
>
> | Option | Cost | Notes |
> |---|---|---|
> | **Google Colab** | **Free** | Best starting point. Runs notebooks in browser, GPU available on free tier |
> | Colab Pro | ~$10/mo | More RAM, longer sessions — only if needed |
> | Vertex AI Workbench | Free tier limited | Better for production; 1 notebook instance free for ~1hr/day |
> | Cloud Run (Flask app) | **Free tier** | 2 million requests/month free — good for deploying `app.py` |
> | Cloud Storage | Free 5GB | Store CSVs, model files |

### 3.1 Convert Core Scripts to Notebooks
- [x] Created `notebooks/01_explore_data.ipynb` — loads, inspects & visualizes `voting_pres_data.csv` (turnout by year, Wisdom flag, county comparison 2016/2020/2024)
- [x] Created `notebooks/02_train_model.ipynb` — full preprocessing pipeline, feature prep, RF training with single-class guard, feature importance chart
- [x] Created `notebooks/03_predict_county.ipynb` — interactive county/state selector, all 4 models (RF, LR, SVM, GB), Laplace fallback, accuracy chart
- [x] Added "Open in Colab" badge table to README (all 3 notebooks, auto-clone on first run)

### 3.2 Data Access in Colab
> ✅ **Superseded** — all 3 notebooks use `git clone https://github.com/sysWisdom/myvoterwisdom.git`
> which pulls data directly from the public GitHub repo. Free for all users, no GCS/Drive quota consumed.
> Google Drive mount is only needed if the repo is private or data exceeds GitHub's file size limits.
- ~~Upload `data/` folder to Google Drive~~
- ~~Update all data paths to use the Drive mount pattern above~~

### 3.3 How to Run for Free (Step-by-Step) ✅
1. Go to [colab.research.google.com](https://colab.research.google.com)
2. File → Open notebook → GitHub → paste the repo URL
3. Runtime → Change runtime type → T4 GPU (free)
4. Run notebooks top-to-bottom

> **Confirmed working 2026-05-25** — all 3 notebooks open and execute end-to-end in Colab.

---

## Phase 4 — syswisdom.ai Vision

### 4.1 Architecture Decision
- [ ] Decide on scope: **public educational dashboard** vs. full API platform
- [ ] Recommended free-tier stack on Google Cloud:
  ```
  Frontend  → Firebase Hosting (free tier, custom domain syswisdom.ai)
  Backend   → Cloud Run (containerized Flask app, free 2M req/month)
  Data/ML   → Colab notebooks + Cloud Storage (5GB free)
  Domain    → Purchase syswisdom.ai via Google Domains (~$12/yr)
  ```

### 4.2 Domain & Hosting
- [ ] Check availability of `syswisdom.ai` domain
- [ ] Set up Firebase Hosting project
- [ ] Deploy `static/index.html` + `static/styles.css` to Firebase

### 4.3 Containerize the Flask App for Cloud Run
- [ ] Create a `Dockerfile`:
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  CMD ["python", "app.py"]
  ```
- [ ] Test locally with Docker
- [ ] Deploy to Cloud Run: `gcloud run deploy wisdomai --source .`

### 4.4 Responsible AI Statement for syswisdom.ai
- [ ] Write a one-page "About this project" page explaining:
  - Built as civic education, not for campaigns
  - Open-source and free forever
  - Data is historical public record only
  - How to contribute or report concerns

---

## Phase 5 — GitHub Open-Source Release

- [x] Make the GitHub repo **public**: `sysWisdom/myvoterwisdom` ✅ Done
- [x] Add GitHub Topics: `election-data`, `open-data`, `civic-tech`, `machine-learning`, `education`
- [x] Enable GitHub Discussions
- [x] Add GitHub Actions CI — `.github/workflows/ci.yml` runs 3 tests on every push/PR
- [ ] Consider adding to [Code for America Brigade](https://brigade.codeforamerica.org/) or similar civic tech networks

---

## Quick Wins (Do These First)

- [x] Fix `requirements.txt` encoding (Phase 1.3)
- [x] Fix hardcoded path in `main_vote2028.py` (Phase 1.1)
- [x] Add Disclaimer section to README (Phase 2.1)
- [x] Upload data to Google Drive and open first notebook in Colab (Phase 3.2) — N/A, git clone approach is better
- [x] GitHub public release complete — repo live at https://github.com/sysWisdom/myvoterwisdom
