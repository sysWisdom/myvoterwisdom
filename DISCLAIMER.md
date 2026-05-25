# Disclaimer

> **This project is a non-partisan, educational research tool.**
> It is not intended to influence elections, predict future outcomes,
> or be used for political campaigning of any kind.

---

## Not for Use in Active Campaigns

**This software and its outputs must not be used for:**

- Political campaign strategy, targeting, or messaging
- Voter contact programs, canvassing lists, or get-out-the-vote targeting
- Political advertising of any kind — digital, print, broadcast, or direct mail
- Fundraising analysis or donor targeting for political candidates or committees
- Any work on behalf of a Political Action Committee (PAC), Super PAC,
  501(c)(4), or political party organization
- Voter suppression, voter caging, or any effort to discourage civic participation
- Opposition research or negative campaign material

These restrictions apply regardless of party affiliation, candidate, jurisdiction,
or election cycle. Violation of this restriction is also a violation of the
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and may result in a permanent ban
from the project.

---

## Data Sources

All data in this project is derived exclusively from **publicly available government
election records**. No proprietary, purchased, or non-public data is included.

### Dataset Summary

| Attribute | Detail |
|---|---|
| **Coverage** | Presidential general elections only |
| **Election years** | 2004, 2008, 2012, 2016, 2020, 2024 |
| **Total records** | 233 county-year observations |
| **Geographic scope** | 39 counties across 25 states |
| **States represented** | AK, AL, AZ, CA, CO, DE, FL, GA, HI, ID, IL, KS, MI, MT, NC, NM, NV, NY, OH, OR, PA, TN, TX, WA, WI |

### Data Fields

| Field | Description |
|---|---|
| `Election Year` | Presidential election year |
| `State` | Two-letter state abbreviation |
| `County` | County or equivalent jurisdiction name |
| `Total Registered Voters` | Registered voter count at time of election |
| `Total Ballots Cast` | Total ballots counted |
| `Vote by Mail Ballots` | Mail-in/absentee ballot count |
| `Vote Center Ballots` | In-person vote center ballot count |
| `Democratic Votes` | Votes cast for the Democratic presidential candidate |
| `Republican Votes` | Votes cast for the Republican presidential candidate |
| `Total Voted` | Total votes counted for president |

### Primary Sources

County-level election data was collected from official public sources including:

- State Secretary of State offices and county election board websites
- The [MIT Election Data and Science Lab (MEDSL)](https://electionlab.mit.edu/) — County Presidential Returns
  doi:[10.7910/DVN/VOQCHQ](https://doi.org/10.7910/DVN/VOQCHQ) — License: CC BY 4.0
- The [U.S. Election Assistance Commission (EAC)](https://www.eac.gov/) — Election Administration and Voting Survey (EAVS)
- Individual county recorder and registrar of voters offices

### Secondary / Validation Source (Tier 3)

The following dataset is used **for cross-validation and rapid prototyping only**.
It is **not** the authoritative training source for ML models in this project.

> **US County Level Election Results 2008–2024**
> Author: Tony McGovern ([@tonmcg](https://github.com/tonmcg))
> Repository: [github.com/tonmcg/US_County_Level_Election_Results_08-24](https://github.com/tonmcg/US_County_Level_Election_Results_08-24)
> DOI: [10.5281/zenodo.14223604](https://doi.org/10.5281/zenodo.14223604)
> License: **MIT** — free to use, modify, and redistribute
> Coverage: 2008, 2012, 2016, 2020, 2024 U.S. presidential elections at the county level

Data in this repository is compiled from published news-outlet sources
(The Guardian, Townhall.com, Fox News, Politico, New York Times) and is described
by the author as **exhaustive but not authoritative**. Researchers should verify
specific results against official state election board records when needed.

Usage in this project:
- `tests/validate_tier3.py` downloads Tier 3 CSVs and cross-checks vote totals
  against MEDSL data, flagging county-years with > 1% divergence
- Downloaded files are cached in `data/county_repo/` (not committed to git)
- `Source` column value `county_repo` identifies any rows sourced from this dataset

> **Note:** This dataset is a research sample — 39 hand-curated counties (Tier 1) plus
> 1,956 counties from MEDSL (Tier 2), across 51 states/territories, 2004–2024.
> It is **not** a nationally representative sample. Counties were selected
> based on data availability during the project's research phase and do not
> represent any deliberate political, demographic, or geographic weighting.

---

## Model Limitations

The machine learning models in this project have significant constraints that
users must understand before interpreting any output.

### 1. This is a historical pattern-matching tool, not a prediction system

The models (Random Forest, Gradient Boosting, Logistic Regression, SVM) identify
patterns in past election data within the same county. They do **not** predict
future elections. Any output labeled "prediction" refers to a cross-validated
estimate of past outcomes, not a forecast.

### 2. The dataset is small and geographically narrow

With 39 counties and 233 observations, this dataset cannot support generalizable
conclusions about national, state, or regional trends. Results for any single
county should be interpreted in the context of that county's own history only.

### 3. The "Wisdom" signal currently produces a single-class training set

The `Wisdom` column (`True` when ≥ 2 of 3 turnout conditions are met) evaluates
to `False` for all 233 records in the current dataset. This means:

- Model training encounters a **single-class problem**
- A reported accuracy of 100% is an **artifact of this imbalance**, not evidence
  of a meaningful model
- The SMOTE oversampler cannot operate without at least two classes
- Users seeing "100% accuracy" should treat the output as **no model trained**,
  not as a reliable result

This will self-correct as more county-year records are added to the dataset.

### 4. No demographic data is included

The dataset contains only aggregate vote counts. There is no individual-level
data, no demographic breakdown, no income, education, race, or age data.
The models cannot and do not make inferences about any group of voters.

### 5. Correlation is not causation

Any patterns identified by this tool reflect correlations in historical data.
They do not establish causal relationships between any variables and election outcomes.

### 6. Vote by Mail and Vote Center fields have sparse coverage

Not all counties or years report `Vote by Mail Ballots` or `Vote Center Ballots`.
Missing values in these fields are expected and do not indicate data corruption.

### 7. The AI Q&A layer is simulated

The FAISS vector store and Q&A feature (`data/vectorStore/`, `data/reasoning/`)
uses synthetic/simulated question-answer pairs generated for research purposes.
It does not represent real voter opinions, real survey data, or any polling source.

---

## No Warranty

This software is provided "as is" under the BSD 3-Clause License, without warranty
of any kind. SysWisdom.AI LLC makes no representations about the accuracy,
completeness, or fitness for purpose of the data or model outputs.

See [LICENSE](LICENSE) for full legal terms.

---

## Contact

Questions about data sources, methodology, or responsible use:
**aj@syswisdom.ai**
