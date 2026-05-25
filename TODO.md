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

### 4.1 Architecture Decision ✅
- [x] Scope: **public educational dashboard** — free, open-source, no billing required
- [x] Chosen stack:
  ```
  Frontend  → GitHub Pages (free, myvoter.syswisdom.ai) ✅ LIVE
  Backend   → Render.com free tier (Flask /predict API, when needed)
  Data/ML   → Colab notebooks + GitHub repo (git clone, no GCS needed)
  Domain    → syswisdom.ai already owned — using myvoter subdomain ✅
  ```

> **End-to-end test confirmed ✅ 2026-05-25:** Orange County, CA prediction returned all 4 model
> results via https://myvoter.syswisdom.ai — Wisdom Analysis card, model grid, Dem/Rep badges
> all rendering correctly. RF + Gradient Boosting → Democratic; LR + SVM → Republican (2/4);
> "Models disagree" consistency flag shown as expected for a genuinely contested county.
>
> **Render build fixes applied (2026-05-25):**
> 1. `sentence-transformers` pulls PyTorch (~1.5 GB) → created `requirements-server.txt` without it
> 2. `faiss-cpu==1.10.0` doesn't exist → updated to `1.14.2` in `requirements.txt`
> 3. Python 3.14 default has no pre-built wheels → pinned `3.11.9` via `.python-version`
> 4. subprocess + `results.json` was fragile on ephemeral filesystem → `main()` now returns dict directly

### 4.2 Domain & Hosting ✅
- [x] `syswisdom.ai` domain already owned — using subdomain `myvoter.syswisdom.ai`
- [x] Wix DNS CNAME: `myvoter` → `syswisdom.github.io` (1hr TTL)
- [x] GitHub Actions deploy: `.github/workflows/deploy-pages.yml` (auto-deploys `static/` on push)
- [x] **Live at https://myvoter.syswisdom.ai** — HTTPS enforced ✅ (2026-05-25)
- [x] Render.com backend: ✅ **LIVE** at https://myvoterwisdom.onrender.com (2026-05-25)
  - Fixed: `requirements-server.txt` (no PyTorch/faiss)
  - Fixed: `.python-version` → 3.11.9 (pre-built wheels, 15s build)
  - Fixed: direct `main()` import instead of subprocess + results.json
- ~~Set up Firebase Hosting~~ — superseded by GitHub Pages

### 4.3 Containerize the Flask App for Cloud Run
> ⏭️ **Superseded by Render.com** — free tier is live and working. Dockerfile/Cloud Run
> only needed if traffic grows beyond Render free limits or GCloud billing is resolved.
- [ ] (Optional) Create `Dockerfile` using `python:3.11-slim` + `requirements-server.txt`
- [ ] (Optional) Deploy to Cloud Run: `gcloud run deploy wisdomai --source .`

### 4.4 Data Quality Score — ✅ LIVE 2026-05-25
- [x] `/data-quality` proxy route added to `app.py` — API key never reaches browser
- [x] Dataset Quality Score card added to `static/index.html` — green button, score circle, dimension bars, issue list
- [x] `DATA_QUALITY_API_KEY` set in Render environment (confirmed working)
- [x] **Confirmed live result** — `prediction_pres_data.csv` (38 rows × 11 columns):

  | Dimension    | Score | Interpretation |
  |---|---|---|
  | Completeness | 100%  | No missing values — all fields present |
  | Consistency  | 100%  | No conflicting records across rows |
  | Validity     | 25%   | 5 columns flagged for outliers (see below) |
  | **Overall**  | **73.8%** | Above 70% Wisdom threshold ✅ |

  > **Validity outliers are expected** — projected vote totals span from small rural counties
  > (e.g. Glacier County MT: 5,370 ballots) to large urban ones (Harris County TX: 1.7M ballots).
  > Statistical outlier detection flags this spread as anomalous, but it reflects real geographic
  > diversity in the data, not errors. The 73.8% score is appropriate for this dataset.

### 4.5 Responsible AI Statement & About Page — ✅ DONE
- [x] Created `static/about.html` — full origin story, DQ score explanation, Responsible AI section, tech stack table
  - Project origin: October 2024, SysWisdom Wisdom model validation experiment
  - Alpha launch: February 2025 (link to syswisdom.ai announcement article)
  - Why 73.8% is the honest score — geographic diversity, not bad data
  - Built as civic education, not for campaigns
  - Open-source and free forever (BSD 3-Clause)
  - How to contribute data via PR + Wisdom gate
- [x] Added "About & Help" and "Our Story" backlinks to `static/index.html` footer

---

## Phase 5 — GitHub Open-Source Release

- [x] Make the GitHub repo **public**: `sysWisdom/myvoterwisdom` ✅ Done
- [x] Add GitHub Topics: `election-data`, `open-data`, `civic-tech`, `machine-learning`, `education`
- [x] Enable GitHub Discussions
- [x] Add GitHub Actions CI — `.github/workflows/ci.yml` runs 3 tests on every push/PR
- [x] Add GitHub Actions **Data Quality Gate** — `.github/workflows/data-quality-check.yml`
  - Triggers on any PR or push that touches `data/`
  - Calls SysWisdom Data Quality API (`prediction_pres_data.csv`)
  - Fails merge if overall score < 70% (Completeness + Consistency + Validity)
  - API key stored as GitHub Actions secret `DATA_QUALITY_API_KEY` (never in code)
  - ⚠️ **Action required**: add `DATA_QUALITY_API_KEY` to repo Settings → Secrets → Actions
  - ⚠️ Known: `voting_pres_data.csv` returns HTTP 500 from DQ API (boolean Wisdom column) — gate covers `prediction_pres_data.csv` only until resolved
- [x] Updated `.gitignore` — `data/*.csv` and `data/reasoning/*.csv` explicitly allowed so contributors can submit new data via PR
- [ ] Consider adding to [Code for America Brigade](https://brigade.codeforamerica.org/) or similar civic tech networks

---

## Quick Wins (Do These First)

- [x] Fix `requirements.txt` encoding (Phase 1.3)
- [x] Fix hardcoded path in `main_vote2028.py` (Phase 1.1)
- [x] Add Disclaimer section to README (Phase 2.1)
- [x] Upload data to Google Drive and open first notebook in Colab (Phase 3.2) — N/A, git clone approach is better
- [x] GitHub public release complete — repo live at https://github.com/sysWisdom/myvoterwisdom
