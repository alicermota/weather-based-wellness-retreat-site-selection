from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(".matplotlib-cache").resolve()))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import make_scorer, matthews_corrcoef
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "dataset"
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURE_DIR = ROOT / "reports" / "figures"

CITY_LABELS = {
    "GUARDA": "Guarda",
    "VILA_REAL": "Vila Real",
}

CHART_COLORS = {
    "Guarda": "#2563eb",
    "Vila Real": "#059669",
    "Suitable": "#059669",
    "Not suitable": "#9ca3af",
}


def season_from_month(month: int) -> str:
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Autumn"


def load_raw_weather() -> pd.DataFrame:
    frames = []
    for path in sorted(RAW_DIR.glob("raw_*.csv")):
        frame = pd.read_csv(path)
        frame["source_file"] = path.name
        frames.append(frame)

    if not frames:
        raise FileNotFoundError(f"No raw weather files found in {RAW_DIR}")

    data = pd.concat(frames, ignore_index=True)
    data.columns = data.columns.str.strip()
    data["date"] = pd.to_datetime(data["date"], errors="raise")
    data["zone"] = data["zone"].str.upper().str.strip()
    data["city"] = data["zone"].map(CITY_LABELS).fillna(data["zone"].str.title())
    data = data.drop_duplicates(subset=["date", "zone"]).sort_values(["date", "zone"])

    required = [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "shortwave_radiation_sum",
        "sunshine_duration",
        "relative_humidity_2m_mean",
        "cloudcover_mean",
    ]
    missing_counts = data[required].isna().sum()
    if missing_counts.sum() > 0:
        raise ValueError(f"Unexpected missing values:\n{missing_counts[missing_counts > 0]}")

    return data


def add_features(data: pd.DataFrame) -> pd.DataFrame:
    featured = data.copy()
    featured["year"] = featured["date"].dt.year
    featured["month"] = featured["date"].dt.month
    featured["month_name"] = featured["date"].dt.month_name()
    featured["day_of_year"] = featured["date"].dt.dayofyear
    featured["season"] = featured["month"].map(season_from_month)
    featured["sunshine_hours"] = featured["sunshine_duration"] / 3600
    featured["temperature_range"] = featured["temperature_2m_max"] - featured["temperature_2m_min"]
    featured["rain_day"] = featured["precipitation_sum"] >= 1.0
    featured["hot_day"] = featured["temperature_2m_max"] > 30.0
    featured["freezing_day"] = featured["temperature_2m_min"] < 0.0
    featured["windy_day"] = featured["wind_gusts_10m_max"] >= 40.0
    featured["comfort_temperature"] = featured["temperature_2m_max"].between(18.0, 30.0, inclusive="both")
    featured["dry_day"] = featured["precipitation_sum"] < 1.0
    featured["sunny_enough"] = featured["sunshine_hours"] >= 3.0
    featured["low_cloud_cover"] = featured["cloudcover_mean"] <= 80.0
    featured["suitable_retreat_day"] = (
        featured["comfort_temperature"]
        & featured["dry_day"]
        & ~featured["windy_day"]
    ).astype(int)
    featured["ok_day"] = featured["suitable_retreat_day"]
    featured["suitability_label"] = featured["suitable_retreat_day"].map({1: "Suitable", 0: "Not suitable"})
    featured["ok_day_label"] = featured["suitability_label"].map({"Suitable": "OK", "Not suitable": "Not OK"})
    featured["month_sin"] = np.sin(2 * np.pi * featured["month"] / 12)
    featured["month_cos"] = np.cos(2 * np.pi * featured["month"] / 12)
    featured["day_sin"] = np.sin(2 * np.pi * featured["day_of_year"] / 365.25)
    featured["day_cos"] = np.cos(2 * np.pi * featured["day_of_year"] / 365.25)
    return featured


def build_summaries(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    complete_years = data[data["year"] < 2026].copy()

    monthly = (
        complete_years.groupby(["city", "zone", "season", "month", "month_name"], as_index=False)
        .agg(
            days=("date", "count"),
            suitable_days=("suitable_retreat_day", "sum"),
            suitability_rate=("suitable_retreat_day", "mean"),
            avg_max_temp_c=("temperature_2m_max", "mean"),
            avg_min_temp_c=("temperature_2m_min", "mean"),
            avg_sunshine_hours=("sunshine_hours", "mean"),
            rain_days=("rain_day", "sum"),
            hot_days=("hot_day", "sum"),
            freezing_days=("freezing_day", "sum"),
            windy_days=("windy_day", "sum"),
            avg_precipitation_mm=("precipitation_sum", "mean"),
        )
        .sort_values(["city", "month"])
    )
    monthly["suitability_rate"] = (monthly["suitability_rate"] * 100).round(1)

    annual = (
        complete_years.groupby(["city", "zone", "year"], as_index=False)
        .agg(
            days=("date", "count"),
            suitable_days=("suitable_retreat_day", "sum"),
            suitability_rate=("suitable_retreat_day", "mean"),
            rain_days=("rain_day", "sum"),
            hot_days=("hot_day", "sum"),
            freezing_days=("freezing_day", "sum"),
            windy_days=("windy_day", "sum"),
        )
        .sort_values(["city", "year"])
    )
    annual["suitability_rate"] = (annual["suitability_rate"] * 100).round(1)

    scorecard = (
        annual.groupby(["city", "zone"], as_index=False)
        .agg(
            avg_suitable_days_per_year=("suitable_days", "mean"),
            avg_suitability_rate=("suitability_rate", "mean"),
            avg_rain_days_per_year=("rain_days", "mean"),
            avg_hot_days_per_year=("hot_days", "mean"),
            avg_freezing_days_per_year=("freezing_days", "mean"),
            avg_windy_days_per_year=("windy_days", "mean"),
            min_suitable_days=("suitable_days", "min"),
            max_suitable_days=("suitable_days", "max"),
        )
        .sort_values("avg_suitable_days_per_year", ascending=False)
    )
    numeric_cols = scorecard.select_dtypes("number").columns
    scorecard[numeric_cols] = scorecard[numeric_cols].round(1)
    return monthly, annual, scorecard


def validate_planning_model(data: pd.DataFrame) -> pd.DataFrame:
    model_data = data.copy()
    features = [
        "city",
        "season",
        "month",
        "day_of_year",
        "sunshine_hours",
        "cloudcover_mean",
        "relative_humidity_2m_mean",
        "shortwave_radiation_sum",
    ]
    target = "suitable_retreat_day"

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["city", "season"]),
            (
                "numeric",
                StandardScaler(),
                [
                    "month",
                    "day_of_year",
                    "sunshine_hours",
                    "cloudcover_mean",
                    "relative_humidity_2m_mean",
                    "shortwave_radiation_sum",
                ],
            ),
        ]
    )
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=5, min_samples_leaf=20, class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(
            n_estimators=250,
            max_depth=8,
            min_samples_leaf=20,
            class_weight="balanced",
            random_state=42,
        ),
        "Naive Bayes": GaussianNB(),
    }

    scoring = {
        "roc_auc": "roc_auc",
        "accuracy": "accuracy",
        "f1": "f1",
        "precision": "precision",
        "recall": "recall",
        "mcc": make_scorer(matthews_corrcoef),
    }
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    rows = []
    for name, model in models.items():
        pipeline = Pipeline([("preprocessor", preprocessor), ("model", model)])
        scores = cross_validate(
            pipeline,
            model_data[features],
            model_data[target],
            cv=cv,
            scoring=scoring,
            n_jobs=None,
            error_score="raise",
        )
        rows.append(
            {
                "model": name,
                "validation": "10-fold stratified CV",
                "roc_auc": scores["test_roc_auc"].mean(),
                "accuracy": scores["test_accuracy"].mean(),
                "f1": scores["test_f1"].mean(),
                "precision": scores["test_precision"].mean(),
                "recall": scores["test_recall"].mean(),
                "mcc": scores["test_mcc"].mean(),
            }
        )

    return pd.DataFrame(rows).round(3)


def save_outputs(
    features: pd.DataFrame,
    monthly: pd.DataFrame,
    annual: pd.DataFrame,
    scorecard: pd.DataFrame,
    validation: pd.DataFrame,
) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    features.to_csv(PROCESSED_DIR / "weather_retreat_features.csv", index=False)
    monthly.to_csv(PROCESSED_DIR / "city_monthly_summary.csv", index=False)
    annual.to_csv(PROCESSED_DIR / "city_annual_summary.csv", index=False)
    scorecard.to_csv(PROCESSED_DIR / "recommendation_scorecard.csv", index=False)
    validation.to_csv(PROCESSED_DIR / "model_validation.csv", index=False)


def style_axis(ax: plt.Axes, title: str, ylabel: str = "") -> None:
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)


def build_visualisations(monthly: pd.DataFrame, annual: pd.DataFrame, scorecard: pd.DataFrame, validation: pd.DataFrame) -> None:
    plt.rcParams.update({"figure.facecolor": "white", "axes.facecolor": "white", "font.size": 10})

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for city, frame in monthly.groupby("city"):
        ax.plot(frame["month"], frame["suitability_rate"], marker="o", linewidth=2.5, label=city, color=CHART_COLORS[city])
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    style_axis(ax, "Monthly Share of Weather-Suitable Retreat Days", "Suitable days (%)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "monthly_suitability_rate.png", dpi=180)
    plt.close(fig)

    annual_pivot = annual.pivot(index="year", columns="city", values="suitable_days")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    annual_pivot.plot(kind="bar", ax=ax, color=[CHART_COLORS[col] for col in annual_pivot.columns], width=0.78)
    style_axis(ax, "Annual Weather-Suitable Days by City", "Days per year")
    ax.legend(frameon=False, title="")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "annual_suitable_days.png", dpi=180)
    plt.close(fig)

    score_metrics = scorecard.set_index("city")[
        [
            "avg_suitable_days_per_year",
            "avg_rain_days_per_year",
            "avg_hot_days_per_year",
            "avg_freezing_days_per_year",
            "avg_windy_days_per_year",
        ]
    ]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    score_metrics.T.plot(kind="bar", ax=ax, color=[CHART_COLORS[col] for col in score_metrics.index], width=0.75)
    ax.set_xticklabels(
        ["Suitable days", "Rain days", "Hot days", "Freezing days", "Windy days"],
        rotation=0,
        ha="center",
    )
    style_axis(ax, "Weather Risk and Opportunity Scorecard", "Average days per year")
    ax.legend(frameon=False, title="")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "city_scorecard.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.8))
    validation.set_index("model")[["accuracy", "precision", "recall", "f1", "roc_auc"]].plot(
        kind="bar", ax=ax, color=["#2563eb", "#059669", "#f59e0b", "#7c3aed", "#dc2626"], width=0.72
    )
    ax.set_ylim(0, 1)
    style_axis(ax, "Planning Model Validation on 2025 Weather", "Score")
    ax.legend(frameon=False, ncols=3)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "model_validation.png", dpi=180)
    plt.close(fig)


def main() -> None:
    raw = load_raw_weather()
    features = add_features(raw)
    monthly, annual, scorecard = build_summaries(features)
    validation = validate_planning_model(features)
    save_outputs(features, monthly, annual, scorecard, validation)
    build_visualisations(monthly, annual, scorecard, validation)

    winner = scorecard.iloc[0]
    print("Weather analysis complete")
    print(f"Records analysed: {len(features):,}")
    print(f"Date range: {features['date'].min().date()} to {features['date'].max().date()}")
    print(f"Recommended city: {winner['city']}")
    print(scorecard.to_string(index=False))
    print()
    print(validation.to_string(index=False))


if __name__ == "__main__":
    main()
