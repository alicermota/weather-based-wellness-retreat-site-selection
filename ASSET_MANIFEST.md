# Asset Manifest

This repository preserves both the final report artifacts and the original analysis work used to create them.

## Primary Report

- `reports/Report.pdf`
  - Full 70-page final report.
  - Contains business framing, methodology, results, validation, final recommendation, and reproducibility appendix.

## Raw Data

- `dataset/raw_GUARDA.csv`
- `dataset/raw_VILA_REAL.csv`

Both files contain daily weather observations from 2018-01-01 to 2026-02-28.

## Original Group Work

### `project_work/Group06_Milestone3/`

- `Alice Mota Orange File.ows`
  - Orange classification workflow.
  - Includes File, Logistic Regression, Tree, Random Forest, Naive Bayes, Test and Score, Confusion Matrix, and ROC Analysis.

- `Martim Carmo Orange File.ows`
  - Orange precipitation workflow.
  - Includes data loading, concatenation, month/year/season features, rain-day derivation, group-by summaries, bar plots, box plots, t-tests, Cohen's d, ANOVA, confidence intervals, and annual statistics.

- `Tomás Vidal Orange File.ows`
  - Orange atmosphere workflow.
  - Includes sunshine/cloud-cover aggregation, annual and monthly summaries, bar plots, box plots, distributions, and data-table checks.

- `Rodrigo Calado Python file.py`
  - Python validation and modelling figure-generation script.
  - Generates statistical tests/effect-size chart, annual CV chart, monthly CV chart, extreme-event chart, model-performance chart, and annual OK-day variability chart.

- `figures/`
  - Generated report visuals covering OK days, temperature, precipitation, atmosphere, validation, and model performance.

### `project_work/modeling/`

- `ok_day_model_simple.csv`
- `ok_days_orange_model_data.csv`
- `ok_day_planning_model_orange.tab`
- `ok_day_prediction_flow.ows`
- `ok_day_prediction_fairness_flow.ows`
- `create_orange_ok_day_flow.py`
- `prepare_ok_day_model_data.py`
- modelling summaries and notes.

These files support the OK-day predictive modelling and planning validation described in the report.

## Supplementary Python Pipeline

- `src/build_analysis.py`
  - Rebuilds cleaned/processed datasets and dashboard-ready summaries using the same OK-day definition as the report.
  - Uses 10-fold stratified cross-validation for supplementary model validation.

Outputs:

- `data/processed/weather_retreat_features.csv`
- `data/processed/city_monthly_summary.csv`
- `data/processed/city_annual_summary.csv`
- `data/processed/recommendation_scorecard.csv`
- `data/processed/model_validation.csv`

## Dashboard

- `dashboard/streamlit_app.py`
  - Short review dashboard for recommendation, monthly suitability, scorecard, risk profile, and model validation.

## Supplementary Figures

- `reports/figures/`
  - Python-generated dashboard figures.
  - Separate from the original report figures in `project_work/Group06_Milestone3/figures/`.
