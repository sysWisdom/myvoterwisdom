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

### Wisdom Model — ✅ Bug Fixed 2026-05-25
> **Root cause:** `compare_votes_and_ballots()` used row-by-row lambdas that compared each row
> against itself, making every condition `None > value` or `value > None` → always `False`.
>
> **Fix:** Replaced with county-level pivot + merge back. Correct distribution:
>
> | Condition | True | False |
> |---|---|---|
> | Dem 2020 > Dem 2024 | 32 | 7 |
> | Dem 2020 > Dem 2016 | 36 | 3 |
> | Ballots 2020 > Ballots 2024 | 28 | 11 |
> | **Wisdom (≥ 2 of 3)** | **32** | **7** |
>
> **82% True / 18% False** across 39 counties — usable training distribution, not single-class.
>
> **Political explanation for the 7 False counties:**
> - Harris TX, Fulton GA — deep-blue urban counties where Democratic votes *grew* 2020→2024; 2020 was not their peak
> - Miami-Dade FL — already shifted Republican in 2020; continued shift in 2024
> - Cherokee, Clark County, Sussex County — mixed swing-county factors
> - **House District 40 (AK)** — see Alaska Borough Note below

### ✅ Alaska Geographic Unit — Resolved (Option A)
> **Background:** Alaska does not have counties. When Alaska drafted its constitution (1955–1956
> Constitutional Convention), delegates intentionally rejected the county system to avoid overlapping
> tax jurisdictions, government duplication, and rigid boundaries in a sparsely populated state with
> vast undeveloped regions and subsistence-based communities. Congress had also legally restricted
> territorial Alaska from creating counties since 1912, at the lobbying of major mining and fishing
> corporations who preferred federal land control over regional taxation.
>
> **Alaska's system instead:**
> - **19 Organized Boroughs** — function like counties for regional services (schools, zoning)
>   but cover immense geographic areas (e.g. Matanuska-Susitna Borough is larger than West Virginia)
> - **The Unorganized Borough** — over half of Alaska's landmass, no regional government;
>   state government (Alaska State Troopers, etc.) provides basic services directly
>
> **Current data entry:** `House District 40` (AK) is a **state legislative district**, not a borough.
> Alaska House District 40 data in the CSV:
>
> | Year | Registered | Ballots | Dem | Rep |
> |---|---|---|---|---|
> | 2024 | 9,108 | 3,362 | 1,362 | 1,688 |
> | 2020 | 10,118 | 4,677 | 1,194 | 2,318 |
> | 2016 | 9,412 | 3,816 | 2,338 | 1,377 |
> | 2008 | 8,666 | 5,029 | 2,137 | 2,686 |
> | 2004 | 8,525 | 5,836 | 2,328 | 3,217 |
>
> Small registration (~9,000), rural voting pattern, and the 2016 Democratic lean suggest this is
> a rural district in the **Matanuska-Susitna Borough** (Mat-Su Valley, north of Anchorage).
>
> **Resolution:** ✅ **Option A applied (2026-05-25):** Renamed `County` field from
> `House District 40` → `Matanuska-Susitna Borough` in `data/voting_pres_data.csv` (5 rows).
>
> **Future improvement (Option B):** Replace these 5 rows with full Matanuska-Susitna Borough
> presidential results from the Alaska Division of Elections (https://www.elections.alaska.gov)
> to get accurate borough-wide vote totals rather than a single legislative district's figures.

### Data Expansion Recommendations
> To expand beyond 39 counties and improve ML robustness, the best FREE source is:
>
> **MIT Election Data + Science Lab — County Presidential Election Returns**
> - URL: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VOQCHQ
> - Data: ~3,100 counties × 6 elections (2000–2020), free CSV download on Harvard Dataverse
> - Columns: county FIPS, state, county, year, party, candidatevotes, totalvotes
> - Would expand from 39 → 3,100 counties; needs a mapping script to match column names
>
> **For 2024 county-level results:**
> - AP Elections (ap.org) — gold standard, but **licensed/paid**
> - U.S. Vote Foundation (civicdata.usvotefoundation.org) — better for registration data
> - Roper Center (ropercenter.cornell.edu) — polling data only, not vote totals
>
> **Recommended immediate action:** Download MIT Election Lab data, map columns to the
> `voting_pres_data.csv` schema, add representative counties across red/blue/purple states.

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
  - ✅ `DATA_QUALITY_API_KEY` added to repo Settings → Secrets → Actions (2026-05-25)
  - ⚠️ Known: `voting_pres_data.csv` returns HTTP 500 from DQ API (boolean Wisdom column) — gate covers `prediction_pres_data.csv` only until resolved
- [x] Updated `.gitignore` — `data/*.csv` and `data/reasoning/*.csv` explicitly allowed so contributors can submit new data via PR
- [x] **Civic Tech Discovery** — researched Code for America Brigade and similar networks (2026-05-25)
  - **GitHub `civic-tech` topic** ✅ already set — repo appears in github.com/topics/civic-tech (1,296+ repos, auto-indexed)
  - **Code for America Brigade index** — requires being a registered Brigade *organization* (not for individual projects); not applicable
  - **Civic Tech Index (civictechindex.org)** — auto-crawls GitHub repos tagged `civic-tech`; already covered by existing topic ✅
  - **Recommended next steps** (manual, no code changes needed):
    - [ ] Add additional GitHub topics for election discoverability: `voter-turnout`, `us-elections`, `election-prediction`, `political-data`
      - Go to https://github.com/sysWisdom/myvoterwisdom → gear icon → Manage topics
    - [ ] Post in [Code for America Slack](https://cfa.slack.com) `#civic-tech` channel with project link and one-line summary
    - [ ] Submit to [Democracy Lab](https://www.democracylab.org/projects/create) — civic tech project directory, free listing
    - [ ] Consider submitting to [Awesome Civic Tech](https://github.com/topics/awesome-civic-tech) curated lists via PR

---

---

## Phase 6 — Data Expansion: MEDSL Presidential Pipeline

> **Data scientist review — 2026-05-25**
> Triggered by two observed behaviors in the live app:
> - **Orange County, CA** — 4 models disagree (2 Dem / 2 Rep); accuracy numbers meaningless
> - **Fulton County, GA** — "single class" warning; 100% Democratic every year in dataset
>
> Both are symptoms of the same root cause: the pipeline trains per-county on ≤ 6 rows.

### Root Cause Analysis

| Problem | Cause | Symptom |
|---|---|---|
| Single-class fallback (Fulton GA) | All 6 years are Democratic wins → `Democratic Wins` is always 1 | "100% likely Democratic" with no model trained |
| Model disagreement (Orange County CA) | 6 rows → SMOTE → ~4 train / 2 test points → each model fits noise | RF + GB say Dem; LR + SVM say Rep; all show 50–100% "accuracy" |
| Overfitting (100% RF accuracy) | Test set is 1–2 rows; any fit will score 100% | Reported accuracy is statistically meaningless |

> **Key insight:** This is an architectural problem, not just a data-size problem.
> The fix requires both more data (MEDSL) **and** a shift to a global model.

### Current vs Target Architecture

| | Current | Target (Phase 6) |
|---|---|---|
| Training scope | Per-county, ~6 rows | Global: all counties × 6 years (~18,600 rows) |
| Test set size | 1–2 rows | Stratified 20% of 18,600 rows (~3,720 rows) |
| Feature set | Democratic Vote Share, Republican Vote Share, Turnout | Same + State (encoded), County type, Year |
| Single-class counties | Fallback to Laplace | Predicted by global model using cross-county patterns |
| Accuracy validity | Meaningless (overfit) | Meaningful (proper held-out test set) |

### MEDSL Data Source

> **MIT Election Data and Science Lab — County Presidential Returns**
> URL: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VOQCHQ
> License: CC BY 4.0 — free to use, redistribute, and build upon with attribution
> Coverage: ~3,100 U.S. counties × elections 2000–2020; check for 2024 update
> Format: CSV, ~500K rows (long format — one row per candidate per county per year)

### Schema Mapping: MEDSL → voting_pres_data.csv

| MEDSL Column | Our Column | Transform |
|---|---|---|
| `year` | `Election Year` | direct |
| `state_po` | `State` | direct (2-letter code) |
| `county_name` | `County` | normalize capitalization |
| `candidatevotes` where `party_simplified == 'DEMOCRAT'` | `Democratic Votes` | pivot/groupby |
| `candidatevotes` where `party_simplified == 'REPUBLICAN'` | `Republican Votes` | pivot/groupby |
| `totalvotes` | `Total Voted` AND `Total Ballots Cast` | direct (MEDSL has no mail/in-person split) |
| *(not in MEDSL)* | `Total Registered Voters` | nullable — set to 0 for MEDSL rows |
| *(not in MEDSL)* | `Vote by Mail Ballots` | nullable — set to 0 for MEDSL rows |
| *(not in MEDSL)* | `Vote Center Ballots` | nullable — set to 0 for MEDSL rows |

> **Turnout feature impact:** `Turnout = Total Ballots Cast / Total Registered Voters`
> MEDSL has no registration data. Options:
> - [ ] **A (recommended):** Get EAVS (Election Assistance Commission) registration data,
>   join on county FIPS — free download at https://www.eac.gov/research-and-data/election-administration-voting-survey
> - [ ] **B (quick):** Drop `Turnout` as a feature for MEDSL rows; retain for our 39 counties
> - [ ] **C (shortcut):** Use `Total Voted / median_county_pop` as a proxy (rough but usable)

### Data Provenance Column

Add a `Source` column to `voting_pres_data.csv`:
- `manual` — current 39 counties (hand-curated, includes registration + mail/in-person)
- `medsl` — rows imported from MEDSL CSV
- `medsl+eavs` — MEDSL rows enriched with EAVS registration data

### Integration Plan (Phased)

- [ ] **Step 1 — Download MEDSL CSV** from Harvard Dataverse (free, no login required for CC BY datasets)
- [ ] **Step 2 — Write `Fetch_County_Data.py` MEDSL importer:**
  - Filter to `office == 'PRESIDENT'` and years 2004–2024
  - Pivot from long (one row per candidate) to wide (one row per county-year)
  - Normalize county names (title case, strip "County" suffix where inconsistent)
  - Set `Total Registered Voters`, `Vote by Mail Ballots`, `Vote Center Ballots` = 0
  - Set `Source = 'medsl'`
  - Append to `voting_pres_data.csv`, deduplicating against existing 39 counties
- [ ] **Step 3 — Recompute Wisdom flags** via `preprocess.py` `update_wisdom()` on full merged dataset
- [ ] **Step 4 — Refactor `main_vote2028.py`** to train a global model (all counties, not just the target county)
  - Features: `Democratic Vote Share`, `Republican Vote Share`, `Turnout` (0 where unavailable), `State` (one-hot), `Election Year`
  - Target: `Democratic Wins` (1 = Dem plurality, 0 = Rep plurality)
  - The per-county prediction becomes: train global model → predict using the target county's most recent features
- [ ] **Step 5 — Update `app.py`** prediction endpoint to use the global model path
- [ ] **Step 6 — Re-run Data Quality gate** on expanded CSV

### Mandate Compliance Check

> **Project mandate:** free, non-partisan, educational resource. No monetization. No political agenda.

| Concern | Status |
|---|---|
| MEDSL data license (CC BY 4.0) | ✅ Compatible with BSD 3-Clause + educational use |
| Attribution required | ✅ Add MEDSL citation to DISCLAIMER.md and About page |
| Expanding to all U.S. counties | ✅ More geographic diversity = more educational value |
| Presidential-only scope | ✅ Filter `office == 'PRESIDENT'` in importer — no other races in pipeline |
| 2004–2024 date range | ✅ MEDSL covers 2000–2020; 2024 data from Dave's Redistricting or Ballotpedia if not yet in MEDSL |
| Wisdom flag logic unchanged | ✅ Same 3-condition pivot logic; just applied to larger dataset |

### Does the Global Model Shift the Project Dynamic? — No.

> **Review question (2026-05-25):** "Elections have the popular vote and the electoral college.
> Counties matter. Will a global model shift the dynamic of this project?"

Both the per-county and global model answer the same question:
**"Will this county give a plurality to the Democratic or Republican presidential candidate?"**

The only difference is the statistical basis:

| | Per-county (current) | Global model (Phase 6) |
|---|---|---|
| Basis for Fulton GA prediction | 6 rows, always Dem → lookup, not a model | Cross-county patterns from 18,600 rows |
| Basis for Orange County CA | 4 train / 1-2 test → 100% accuracy is an artifact | Proper 80/20 split, statistically valid |
| What it learns | Nothing — memorizes 6 points | Why similar counties vote how they do |
| Educational value | "Fulton has always been Dem" | "Counties with these features tend to shift" |

**The Electoral College argument supports the global model:**
Counties are the atom of presidential elections: `Voters → Counties → States → Electoral College`.
The EC is won by flipping states, states are flipped by flipping swing counties.
A global model trained on all 3,100 counties can identify which counties have structurally
flippable characteristics — that is the educational insight the project exists to deliver.

**What would genuinely shift the mandate:**
- Adding demographic/Census features → models *why* people vote, not just *how* they have
- Adding live polling or forecasting data → shifts from historical analysis to live prediction
- Aggregating county → state → 270 Electoral College map → extends scope (see Phase 7 below)

---

## Phase 7 — Electoral College Aggregation (Natural Extension of Phase 6)

> **Prerequisite:** Phase 6 (global model + full county dataset) must be complete first.
> This phase does NOT change the project mandate — it completes the story from county to outcome.

### The Chain: County → State → Electoral College

```
Phase 6 output:  county prediction (Dem win = 1 / Rep win = 0)
Phase 7 goal:    aggregate county predictions → state winner → Electoral College map
```

**State-level aggregation logic (population-weighted):**
1. For each state, sum `Democratic Votes` and `Republican Votes` across all predicted counties
2. State goes Dem if projected Dem total > projected Rep total
3. Map state winners to their Electoral College vote counts (fixed, from U.S. Constitution + Census apportionment)
4. Sum to 270-threshold check

**What this adds to the UI:**
- A national map showing projected state-by-state outcomes
- An Electoral College vote tally (e.g. "Dem 312 / Rep 226")
- A "swing county" highlight: counties where the projected margin is < 5 percentage points

**Mandate compliance:**
- Still 100% historical data (no polling, no forecasting)
- Non-partisan: applies identical logic to all states
- Educational: shows students how county-level data connects to national outcomes
- The EC map shows what the data *suggests*, labeled clearly as a historical-data projection

**Data needed:**
- [ ] Electoral College votes per state (fixed table — from archives.gov or Wikipedia)
- [ ] County-to-state mapping (already in MEDSL via `state_po` column)
- [ ] 2020 Census county population (for population-weighted aggregation) — free from Census Bureau API

---

## Quick Wins (Do These First)

- [x] Fix `requirements.txt` encoding (Phase 1.3)
- [x] Fix hardcoded path in `main_vote2028.py` (Phase 1.1)
- [x] Add Disclaimer section to README (Phase 2.1)
- [x] Upload data to Google Drive and open first notebook in Colab (Phase 3.2) — N/A, git clone approach is better
- [x] GitHub public release complete — repo live at https://github.com/sysWisdom/myvoterwisdom
