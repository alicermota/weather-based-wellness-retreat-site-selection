# Weather-Based Site Selection for a Mountain Wellness Retreat

## Project Summary

This project evaluates whether **Guarda** or **Vila Real** is the better Portuguese mountain location for a premium outdoor wellness retreat.

The analysis is based on the full group report, Orange Data Mining workflows, generated figures, and Python validation scripts from the Mountain Wellness project. A reproducible Python pipeline and Streamlit dashboard are also included to make the project easier to review and rerun.

## Business Question

**Which city offers the stronger climate profile for a mountain wellness retreat, considering outdoor comfort, rainfall disruption, heat/cold risk, atmospheric quality, predictability, and seasonal business fit?**

The recommendation is climate-led rather than purely statistical. The project compares the two cities across:

- comfort and OK-day availability;
- temperature and extreme-event risk;
- precipitation volume, frequency, and seasonality;
- sunshine, cloud cover, and perceived wellness atmosphere;
- annual predictability;
- classification-model validation of OK-day structure.

## Main Recommendation

**Recommended location: Guarda**

The report recommends Guarda if the retreat is designed as a summer/autumn-led outdoor wellness destination with strong indoor winter infrastructure.

The decision is not based on a large annual gap in OK days. Guarda and Vila Real are close overall:

| Indicator | Guarda | Vila Real | Interpretation |
|---|---:|---:|---|
| Total OK days, 2018-early 2026 | 623 | 612 | Slight Guarda advantage |
| Summer OK days | 276 | 211 | Strong Guarda peak-season advantage |
| Spring OK days | 140 | 182 | Vila Real shoulder-season advantage |
| Hot days above 30 C | 159 | 270 | Vila Real has higher heat risk |
| Warm nights above 20 C | 15 | 75 | Vila Real has higher sleep/cooling risk |
| Freezing days below 0 C | 326 | 67 | Guarda has higher winter operating risk |
| Rain days at or above 1 mm | 856 | 1,039 | Vila Real has greater rainfall disruption |
| Mean sunshine hours/day | 9.12 | 8.82 | Guarda is brighter |
| Mean cloud cover | 51.2% | 54.1% | Guarda is less cloudy |

The final logic is that Guarda performs better on the dimensions that matter most for a premium outdoor wellness retreat: summer usability, lower peak-season heat risk, lower rainfall disruption, brighter atmosphere, and more stable annual OK-day availability. Vila Real remains a credible alternative for a milder, spring-oriented concept.

## Primary Report

The main written report is:

```text
reports/Report.pdf
```

This is the source of truth for the full methodology, findings, validation, and recommendation. It includes:

- problem framing and client context;
- dataset description;
- data quality discussion;
- preprocessing and derived variables;
- temperature analysis;
- precipitation analysis;
- sunshine/cloud-cover atmosphere analysis;
- statistical validation;
- OK-day predictive modelling;
- integrated trade-off matrix;
- limitations and assumptions;
- final recommendation and next steps;
- appendix with reproducibility and Orange workflow guidance.

A concise LaTeX decision-report draft is also included:

```text
reports/climate_suitability_report.tex
```

## Dataset

Raw data:

```text
dataset/raw_GUARDA.csv
dataset/raw_VILA_REAL.csv
```

The two files contain daily meteorological observations for Guarda and Vila Real from **2018-01-01 to 2026-02-28**, with **2,981 observations per city** and **5,962 total rows**.

Key variables include:

- daily max/min/mean temperature;
- daily precipitation;
- max wind speed and wind gusts;
- sunshine duration;
- shortwave radiation;
- relative humidity;
- cloud cover;
- date, location, latitude, and longitude.

## Derived Variables

The report and workflows create:

- `month`, `year`, and `season`;
- `sunshine_hours = sunshine_duration / 3600`;
- `rain_day`, where precipitation is at least 1 mm;
- `hot_day`, where max temperature is above 30 C;
- `freezing_day`, where min temperature is below 0 C;
- `warm_night`, where min temperature is above 20 C;
- `ok_day`, where:

```text
precipitation_sum < 1.0 mm
wind_gusts_10m_max < 40 km/h
18 C <= temperature_2m_max <= 30 C
```

## Original Analysis Assets

The original group work is preserved in:

```text
project_work/Group06_Milestone3/
```

Important files:

- `Alice Mota Orange File.ows`: classification workflow with Logistic Regression, Tree, Random Forest, Naive Bayes, Test and Score, Confusion Matrix, and ROC Analysis.
- `Martim Carmo Orange File.ows`: precipitation workflow with raw-file loading, concatenation, month/year/season features, rain-day derivation, group-by summaries, bar plots, box plots, t-test, Cohen's d, ANOVA, confidence intervals, and annual statistics.
- `Tomas Vidal Orange File.ows`: atmosphere workflow using sunshine, cloud cover, annual/monthly grouping, bar plots, box plots, distributions, and data-table checks.
- `Rodrigo Calado Python file.py`: Python script generating validation/model figures such as statistical tests, annual CV, monthly CV, extreme frequencies, model performance, and annual OK-day variability.
- `figures/`: generated charts used in the report.

Additional modelling files referenced by the report are preserved in:

```text
project_work/modeling/
```

These include OK-day model datasets, Orange model flows, annual/monthly planning summaries, and modelling notes.

## Model Validation

The report uses Orange Data Mining as the main visual modelling environment. The OK-day model excludes the direct rule variables that define the target and uses indirect planning/atmospheric features such as:

- zone;
- season;
- month;
- day of year;
- sunshine hours;
- cloud cover;
- relative humidity;
- shortwave radiation.

The report's model comparison shows that Random Forest provides the strongest balance for planning, with the highest overall performance among the tested models.

The supplementary Python pipeline in `src/build_analysis.py` mirrors the same target definition and uses 10-fold stratified cross-validation for a reproducible dashboard-ready summary.

## Visualisations

Report figures from the original group work:

```text
project_work/Group06_Milestone3/figures/
```

Supplementary dashboard figures:

```text
reports/figures/
```

The original figure set includes OK-day monthly/annual/seasonal charts, temperature distributions, precipitation charts, atmosphere summaries, statistical validation, model performance, and annual predictability visuals.

## Streamlit Dashboard

A short dashboard is included for quick review:

```bash
streamlit run dashboard/streamlit_app.py
```

The dashboard reads the processed files in:

```text
data/processed/
```

It summarizes the recommendation, monthly suitability, weather risks, scorecard results, and model validation.

## Reproduce the Supplementary Python Pipeline

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python src/build_analysis.py
```

This regenerates:

- `data/processed/weather_retreat_features.csv`;
- `data/processed/city_monthly_summary.csv`;
- `data/processed/city_annual_summary.csv`;
- `data/processed/recommendation_scorecard.csv`;
- `data/processed/model_validation.csv`;
- dashboard figures in `reports/figures/`.

## Project Structure

```text
.
├── dashboard/
│   └── streamlit_app.py
├── data/
│   └── processed/
├── dataset/
│   ├── raw_GUARDA.csv
│   └── raw_VILA_REAL.csv
├── project_work/
│   ├── Group06_Milestone3/
│   │   ├── *.ows
│   │   ├── Rodrigo Calado Python file.py
│   │   └── figures/
│   └── modeling/
├── reports/
│   ├── Report.pdf
│   ├── climate_suitability_report.tex
│   └── figures/
├── src/
│   └── build_analysis.py
├── requirements.txt
└── README.md
```

## Limitations

- The recommendation is climate-led and does not include full financial due diligence.
- The analysis compares only Guarda and Vila Real.
- OK-day thresholds are transparent business assumptions, not a complete comfort model.
- Daily data cannot distinguish between rainfall or heat during activity hours versus overnight conditions.
- Site-level microclimate, slope, shade, road access, land cost, permits, staffing, and competitors are outside the weather dataset.
- Historical weather patterns do not fully account for long-term climate change.

## Next Steps

Before investment, the client should:

- validate the exact property microclimate in Guarda;
- estimate heating, insulation, and indoor wellness infrastructure costs;
- create a summer/autumn outdoor programming calendar;
- compare land cost, access, permitting, staffing, and competitor positioning;
- update the analysis with future climate projections.
