# Orange Modeling Guide: Predicting OK Days

This guide uses the prepared file:

`Mountain Wellness/modeling/ok_days_orange_model_data.csv`

The target variable is `ok_day_label`, with two classes:

- `OK`
- `Not OK`

The numeric variable `ok_day` is the same target encoded as 1/0. Do not use `ok_day`
as an input feature, because that would leak the answer into the model.

## Recommended Orange Workflow

Use this widget flow:

`File -> Select Columns -> Data Sampler -> Logistic Regression / Tree / Random Forest -> Test & Score -> Confusion Matrix`

Optional visual checks:

`Test & Score -> ROC Analysis`

`Model -> Predictions`

`Tree -> Tree Viewer`

## Step 1: Load the Data

1. Open Orange.
2. Add a `File` widget.
3. Load `ok_days_orange_model_data.csv`.
4. Check that the table has 5,962 rows.

## Step 2: Set the Target

Add `Select Columns`.

Set:

- Target: `ok_day_label`
- Meta: `date`, `ok_day`
- Features: the variables used for the chosen model setup below.

## Model Setup A: Weather-Condition Classifier

Purpose: validate that the weather variables correctly identify OK days.

Use these features:

- `temperature_2m_max`
- `precipitation_sum`
- `wind_gusts_10m_max`
- optionally `zone`, `month`, `season`

Expected result:

This model should perform extremely well because these variables directly define an OK
day. This is useful as a technical validation, but it is not the strongest strategic model.

Report interpretation:

> The first model confirms that the OK-day indicator is internally consistent: days are
> classified mainly according to maximum temperature, precipitation, and wind gusts,
> which are the operational criteria used to define outdoor activity feasibility.

## Model Setup B: Planning-Oriented Classifier

Purpose: estimate the probability of an OK day using location and calendar structure,
without directly giving the model the variables that define `ok_day`.

Use these features:

- `zone`
- `month`
- `season`
- `day_of_year`
- optional supporting variables: `sunshine_hours`, `cloudcover_mean`,
  `relative_humidity_2m_mean`, `shortwave_radiation_sum`

Exclude these direct rule variables:

- `temperature_2m_max`
- `precipitation_sum`
- `wind_gusts_10m_max`
- `ok_day`

Recommended learners:

- `Logistic Regression`
- `Tree`
- `Random Forest`
- `Naive Bayes`

Recommended evaluation:

- Use `Test & Score` with cross-validation, for example 10 folds.
- Compare AUC, CA, F1, Precision, and Recall.
- Because `Not OK` is the majority class, do not rely only on accuracy.

Report interpretation:

> The planning-oriented model evaluates whether location and seasonal timing contain
> predictive information about OK-day availability. This connects modeling to the
> business decision because it estimates when each location is more likely to support
> outdoor wellness programming.

## Useful Descriptive Results From the Prepared Table

Overall OK-day counts:

- Guarda: 623 OK days out of 2,981 daily observations, 20.9%.
- Vila Real: 612 OK days out of 2,981 daily observations, 20.5%.

Seasonal OK-day rates:

- Guarda summer: 276 / 736 days, 37.5%.
- Vila Real summer: 211 / 736 days, 28.7%.
- Guarda spring: 140 / 736 days, 19.0%.
- Vila Real spring: 182 / 736 days, 24.7%.
- Guarda autumn: 207 / 728 days, 28.4%.
- Vila Real autumn: 210 / 728 days, 28.8%.
- Guarda winter: 0 / 781 days, 0.0%.
- Vila Real winter: 9 / 781 days, 1.2%.

Suggested wording for Milestone 3:

> The predictive modeling should not be interpreted as a final decision by itself.
> Instead, it supports the decision framework by showing whether OK-day availability is
> predictable from location and season. The most decision-relevant output is not only
> overall accuracy, but the predicted probability of OK days across the operational
> calendar.

