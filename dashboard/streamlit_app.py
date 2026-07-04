from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    features = pd.read_csv(PROCESSED_DIR / "weather_retreat_features.csv", parse_dates=["date"])
    monthly = pd.read_csv(PROCESSED_DIR / "city_monthly_summary.csv")
    scorecard = pd.read_csv(PROCESSED_DIR / "recommendation_scorecard.csv")
    validation = pd.read_csv(PROCESSED_DIR / "model_validation.csv")
    return features, monthly, scorecard, validation


st.set_page_config(
    page_title="Mountain Wellness Site Selection",
    layout="wide",
)

st.title("Weather-Based Site Selection for a Mountain Wellness Retreat")
st.caption("Climate suitability comparison for Guarda and Vila Real, Portugal")

try:
    features, monthly, scorecard, validation = load_data()
except FileNotFoundError:
    st.error("Processed files not found. Run `python src/build_analysis.py` from the project root first.")
    st.stop()

recommended_city = scorecard.iloc[0]["city"]
date_min = features["date"].min().date()
date_max = features["date"].max().date()

st.subheader(f"Recommendation: {recommended_city}")
st.write(
    "The recommended city is the one with the strongest average count of weather-suitable retreat days "
    "across complete historical years, balanced against rain, heat, freezing, and wind risks."
)

metric_cols = st.columns(4)
metric_cols[0].metric("Recommended city", recommended_city)
metric_cols[1].metric("Records analysed", f"{len(features):,}")
metric_cols[2].metric("Date range", f"{date_min} to {date_max}")
metric_cols[3].metric("Cities compared", features["city"].nunique())

st.divider()

selected_cities = st.multiselect(
    "Cities",
    sorted(features["city"].unique()),
    default=sorted(features["city"].unique()),
)

filtered_monthly = monthly[monthly["city"].isin(selected_cities)]
filtered_features = features[features["city"].isin(selected_cities)]

left, right = st.columns((1.3, 1))

with left:
    st.subheader("Monthly Suitability")
    monthly_chart = filtered_monthly.pivot(index="month_name", columns="city", values="suitability_rate")
    month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    monthly_chart = monthly_chart.reindex(month_order)
    st.line_chart(monthly_chart, y_label="Suitable days (%)")

with right:
    st.subheader("City Scorecard")
    st.dataframe(
        scorecard[
            [
                "city",
                "avg_suitable_days_per_year",
                "avg_suitability_rate",
                "avg_rain_days_per_year",
                "avg_hot_days_per_year",
                "avg_freezing_days_per_year",
                "avg_windy_days_per_year",
            ]
        ],
        hide_index=True,
        use_container_width=True,
    )

st.subheader("Weather Risk Profile")
risk = (
    filtered_features[filtered_features["year"] < 2026]
    .groupby("city")
    .agg(
        suitable_days=("suitable_retreat_day", "sum"),
        rain_days=("rain_day", "sum"),
        hot_days=("hot_day", "sum"),
        freezing_days=("freezing_day", "sum"),
        windy_days=("windy_day", "sum"),
    )
)
st.bar_chart(risk, y_label="Days")

st.subheader("Model Validation")
st.write("Planning models use 10-fold stratified cross-validation with location, seasonality, sunshine, cloud cover, humidity, and solar radiation features.")
st.dataframe(validation, hide_index=True, use_container_width=True)

st.subheader("Business Interpretation")
st.write(
    "Use the weather suitability score as a site-screening tool, not as the only investment criterion. "
    "The next decision stage should combine this climate signal with land cost, access, accommodation capacity, "
    "local partnerships, and customer demand."
)
