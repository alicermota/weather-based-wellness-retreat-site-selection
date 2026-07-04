# OK-Day Predictive Model and Fairness Interpretation

## Files

- Orange workflow: `ok_day_prediction_fairness_flow.ows`
- Orange dataset: `ok_day_planning_model_orange.tab`
- Source daily dataset: `ok_days_orange_model_data.csv`

## Model Objective

The target is `ok_day_label`, which predicts whether a day is suitable (`OK`) or not
suitable (`Not OK`) for outdoor wellness activities.

The predictive model uses planning-oriented variables:

- `zone`
- `season`
- `month`
- `day_of_year`
- `sunshine_hours`
- `cloudcover_mean`
- `relative_humidity_2m_mean`
- `shortwave_radiation_sum`

The direct rule variables used to define OK days are intentionally excluded from the
Orange `.tab` file:

- `temperature_2m_max`
- `precipitation_sum`
- `wind_gusts_10m_max`

This avoids a circular model where the algorithm simply re-learns the OK-day rule.

## Recommended Orange Evaluation

Open `ok_day_prediction_fairness_flow.ows` and run:

`File -> Logistic Regression / Tree / Random Forest / Naive Bayes -> Test and Score`

Use 10-fold stratified cross-validation. Compare models using:

- AUC
- Classification accuracy
- F1
- Precision
- Recall
- Confusion Matrix
- ROC Analysis

## Fairness Interpretation

Following the critical-thinking perspective from class, fairness should be considered,
but it must be interpreted carefully. In this project, `zone` distinguishes two location
alternatives, Guarda and Vila Real. It is not a protected human attribute such as gender,
age, ethnicity, or socioeconomic status.

Therefore, fairness is not used here to ask whether the model discriminates against
people. Instead, it is used as a methodological audit:

1. Are both locations represented with the same number of daily observations?
2. Are both locations evaluated with the same target definition?
3. Does the model make much larger errors for one location than the other?
4. If fairness metrics differ by zone, are they revealing model bias or real climatic
   differences?

The comparison is procedurally fair because both locations have the same time range,
same variables, same number of rows, and the same OK-day definition.

Important: a difference in OK-day probability between Guarda and Vila Real should not
automatically be treated as unfairness. Detecting climatic differences between locations
is the purpose of the model. Fairness metrics are useful only to check whether prediction
quality is uneven across the two locations.

## Descriptive Baseline

Overall OK-day rate:

| zone | ok_days | days | ok_day_rate |
| --- | --- | --- | --- |
| GUARDA | 623 | 2981 | 20.9 |
| VILA_REAL | 612 | 2981 | 20.5 |

Seasonal OK-day rate:

| zone | season | ok_days | days | ok_day_rate |
| --- | --- | --- | --- | --- |
| GUARDA | Autumn | 207 | 728 | 28.4 |
| GUARDA | Spring | 140 | 736 | 19.0 |
| GUARDA | Summer | 276 | 736 | 37.5 |
| GUARDA | Winter | 0 | 781 | 0.0 |
| VILA_REAL | Autumn | 210 | 728 | 28.8 |
| VILA_REAL | Spring | 182 | 736 | 24.7 |
| VILA_REAL | Summer | 211 | 736 | 28.7 |
| VILA_REAL | Winter | 9 | 781 | 1.2 |

## Suggested Report Wording

The predictive model was developed to estimate the probability of an OK day for outdoor
wellness activities using location, seasonal timing, and atmospheric indicators. The
model intentionally excludes the variables that directly define OK days, so the prediction
task is not circular.

Fairness was considered because the model compares two alternatives, Guarda and Vila
Real. However, in this context `zone` is not a protected human attribute but the decision
alternative itself. For that reason, fairness metrics should not be interpreted as evidence
of social discrimination. Instead, they are used as a critical-thinking checkpoint to
verify whether the model evaluates both locations under equivalent conditions and
whether prediction errors are balanced across zones.
