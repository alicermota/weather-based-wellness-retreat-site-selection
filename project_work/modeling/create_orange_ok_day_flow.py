from pathlib import Path
import csv
import html
import json

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODELING = ROOT / "modeling"
CSV_PATH = MODELING / "ok_days_orange_model_data.csv"
TAB_PATH = MODELING / "ok_day_planning_model_orange.tab"
FLOW_PATH = MODELING / "ok_day_prediction_fairness_flow.ows"
REPORT_PATH = MODELING / "ok_day_predictive_model_fairness_notes.md"


FEATURES = [
    "zone",
    "season",
    "month",
    "day_of_year",
    "sunshine_hours",
    "cloudcover_mean",
    "relative_humidity_2m_mean",
    "shortwave_radiation_sum",
]
META = ["date"]
TARGET = "ok_day_label"


def write_orange_tab() -> None:
    data = pd.read_csv(CSV_PATH)
    data = data[META + FEATURES + [TARGET]].copy()

    names = META + FEATURES + [TARGET]
    types = [
        "time",
        "discrete",
        "discrete",
        "continuous",
        "continuous",
        "continuous",
        "continuous",
        "continuous",
        "continuous",
        "discrete",
    ]
    roles = [
        "meta",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "class",
    ]

    with TAB_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(names)
        writer.writerow(types)
        writer.writerow(roles)
        for row in data.itertuples(index=False, name=None):
            writer.writerow(row)


def node(node_id, name, qualified_name, title, x, y):
    return (
        f'\t\t<node id="{node_id}" name="{html.escape(name)}" '
        f'qualified_name="{html.escape(qualified_name)}" project_name="Orange3" '
        f'version="" title="{html.escape(title)}" position="({x}, {y})" />'
    )


def link(link_id, source, sink, source_channel, sink_channel, source_id, sink_id):
    return (
        f'\t\t<link id="{link_id}" source_node_id="{source}" sink_node_id="{sink}" '
        f'source_channel="{source_channel}" sink_channel="{sink_channel}" '
        f'enabled="true" source_channel_id="{source_id}" sink_channel_id="{sink_id}" />'
    )


def write_flow() -> None:
    # The workflow intentionally keeps widget settings light. Orange will preserve the
    # layout and links; if the File widget does not auto-load, browse to TAB_PATH.
    nodes = [
        node(0, "File", "Orange.widgets.data.owfile.OWFile", "OK-day planning data", 50, 220),
        node(1, "Data Table", "Orange.widgets.data.owtable.OWTable", "Inspect data", 260, 90),
        node(2, "Logistic Regression", "Orange.widgets.model.owlogisticregression.OWLogisticRegression", "Logistic Regression", 520, 80),
        node(3, "Tree", "Orange.widgets.model.owclassificationtree.OWClassificationTree", "Decision Tree", 520, 200),
        node(4, "Random Forest", "Orange.widgets.model.owrandomforest.OWRandomForest", "Random Forest", 520, 320),
        node(5, "Naive Bayes", "Orange.widgets.model.ownaivebayes.OWNaiveBayes", "Naive Bayes", 520, 440),
        node(6, "Test and Score", "Orange.widgets.evaluate.owtestandscore.OWTestAndScore", "Cross-validation + fairness metrics", 820, 230),
        node(7, "Confusion Matrix", "Orange.widgets.evaluate.owconfusionmatrix.OWConfusionMatrix", "Confusion Matrix", 1090, 120),
        node(8, "ROC Analysis", "Orange.widgets.evaluate.owrocanalysis.OWROCAnalysis", "ROC Analysis", 1090, 280),
        node(9, "Predictions", "Orange.widgets.evaluate.owpredictions.OWPredictions", "Predictions by zone", 1090, 440),
        node(10, "Tree Viewer", "Orange.widgets.visualize.owtreeviewer.OWTreeViewer", "Tree Viewer", 820, 500),
    ]
    links = [
        link(0, 0, 1, "Data", "Data", "data", "data"),
        link(1, 0, 6, "Data", "Data", "data", "train_data"),
        link(2, 2, 6, "Learner", "Learner", "learner", "learner"),
        link(3, 3, 6, "Learner", "Learner", "learner", "learner"),
        link(4, 4, 6, "Learner", "Learner", "learner", "learner"),
        link(5, 5, 6, "Learner", "Learner", "learner", "learner"),
        link(6, 6, 7, "Evaluation Results", "Evaluation Results", "evaluations_results", "evaluation_results"),
        link(7, 6, 8, "Evaluation Results", "Evaluation Results", "evaluations_results", "evaluation_results"),
        link(8, 6, 9, "Predictions", "Data", "predictions", "data"),
        link(9, 3, 10, "Tree", "Tree", "tree", "tree"),
    ]
    annotation = {
        "type": "text",
        "rect": [45, 20, 940, 50],
        "text": (
            "Target: ok_day_label. Features: zone, season, month/day, sunshine, cloud cover, "
            "humidity and radiation. Direct rule variables are excluded. Treat zone as the "
            "fairness/comparison variable only for an audit of whether model performance differs by location."
        ),
    }
    scheme = f"""<?xml version='1.0' encoding='utf-8'?>
<scheme version="2.0" title="OK Day Prediction" description="Predict OK days for Guarda and Vila Real using planning-oriented predictors.">
\t<nodes>
{chr(10).join(nodes)}
\t</nodes>
\t<links>
{chr(10).join(links)}
\t</links>
\t<annotations>
\t\t<annotation>{html.escape(json.dumps(annotation))}</annotation>
\t</annotations>
\t<thumbnail />
\t<node_properties>
\t\t<properties node_id="6" format="literal">{{'comparison_criterion': 0, 'controlAreaVisible': True, 'cv_stratified': True, 'n_folds': 10, 'n_repeats': 1, 'resampling': 0, 'shuffle_stratified': True, 'score_table': {{'show_score_hints': {{'Model_': True, 'CA': True, 'PrecisionRecallFSupport': True, 'Precision': True, 'Recall': True, 'F1': True, 'AUC': True, 'MatthewsCorrCoefficient': True, 'StatisticalParityDifference': True, 'EqualOpportunityDifference': True, 'AverageOddsDifference': True, 'DisparateImpact': True}}}}, '__version__': 4, 'context_settings': []}}</properties>
\t</node_properties>
</scheme>
"""
    FLOW_PATH.write_text(scheme, encoding="utf-8")


def write_report_notes() -> None:
    data = pd.read_csv(CSV_PATH)
    season = (
        data.groupby(["zone", "season"])["ok_day"]
        .agg(ok_days="sum", days="count", ok_day_rate="mean")
        .reset_index()
    )
    season["ok_day_rate"] = (season["ok_day_rate"] * 100).round(1)
    overall = (
        data.groupby("zone")["ok_day"]
        .agg(ok_days="sum", days="count", ok_day_rate="mean")
        .reset_index()
    )
    overall["ok_day_rate"] = (overall["ok_day_rate"] * 100).round(1)

    def markdown_table(frame: pd.DataFrame) -> str:
        columns = list(frame.columns)
        rows = [[str(value) for value in row] for row in frame.to_numpy()]
        header = "| " + " | ".join(columns) + " |"
        separator = "| " + " | ".join(["---"] * len(columns)) + " |"
        body = ["| " + " | ".join(row) + " |" for row in rows]
        return "\n".join([header, separator, *body])

    notes = f"""# OK-Day Predictive Model and Fairness Interpretation

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

{markdown_table(overall)}

Seasonal OK-day rate:

{markdown_table(season)}

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
"""
    REPORT_PATH.write_text(notes, encoding="utf-8")


def main() -> None:
    write_orange_tab()
    write_flow()
    write_report_notes()
    print(f"Wrote {TAB_PATH}")
    print(f"Wrote {FLOW_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
