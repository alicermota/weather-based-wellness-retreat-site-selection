from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "dataset"
OUT_DIR = ROOT / "modeling"


def season_from_month(month: int) -> str:
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Autumn"


def load_city(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    data["date"] = pd.to_datetime(data["date"])
    return data


def main() -> None:
    guarda = load_city(DATASET_DIR / "raw_GUARDA.csv")
    vila_real = load_city(DATASET_DIR / "raw_VILA_REAL.csv")
    data = pd.concat([guarda, vila_real], ignore_index=True)

    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    data["month_name"] = data["date"].dt.month_name()
    data["day_of_year"] = data["date"].dt.dayofyear
    data["season"] = data["month"].map(season_from_month)
    data["sunshine_hours"] = data["sunshine_duration"] / 3600

    data["rain_day"] = (data["precipitation_sum"] >= 1.0).astype(int)
    data["hot_day"] = (data["temperature_2m_max"] > 30.0).astype(int)
    data["freezing_day"] = (data["temperature_2m_min"] < 0.0).astype(int)
    data["warm_night"] = (data["temperature_2m_min"] > 20.0).astype(int)
    data["ok_day"] = (
        (data["precipitation_sum"] < 1.0)
        & (data["wind_gusts_10m_max"] < 40.0)
        & (data["temperature_2m_max"].between(18.0, 30.0, inclusive="both"))
    ).astype(int)
    data["ok_day_label"] = data["ok_day"].map({1: "OK", 0: "Not OK"})

    modeling_columns = [
        "date",
        "year",
        "month",
        "month_name",
        "day_of_year",
        "season",
        "zone",
        "latitude",
        "longitude",
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "shortwave_radiation_sum",
        "sunshine_hours",
        "relative_humidity_2m_mean",
        "cloudcover_mean",
        "rain_day",
        "hot_day",
        "freezing_day",
        "warm_night",
        "ok_day",
        "ok_day_label",
    ]
    model_data = data[modeling_columns].sort_values(["date", "zone"])
    model_path = OUT_DIR / "ok_days_orange_model_data.csv"
    model_data.to_csv(model_path, index=False)

    monthly = (
        model_data.groupby(["zone", "season", "month", "month_name"], as_index=False)
        .agg(
            days=("ok_day", "size"),
            ok_days=("ok_day", "sum"),
            ok_day_rate=("ok_day", "mean"),
            hot_days=("hot_day", "sum"),
            rain_days=("rain_day", "sum"),
            freezing_days=("freezing_day", "sum"),
        )
        .sort_values(["zone", "month"])
    )
    monthly["ok_day_rate"] = (monthly["ok_day_rate"] * 100).round(1)
    monthly_path = OUT_DIR / "ok_day_monthly_planning_summary.csv"
    monthly.to_csv(monthly_path, index=False)

    annual = (
        model_data[model_data["year"] < 2026]
        .groupby(["zone", "year"], as_index=False)
        .agg(
            days=("ok_day", "size"),
            ok_days=("ok_day", "sum"),
            ok_day_rate=("ok_day", "mean"),
            hot_days=("hot_day", "sum"),
            rain_days=("rain_day", "sum"),
            freezing_days=("freezing_day", "sum"),
        )
        .sort_values(["zone", "year"])
    )
    annual["ok_day_rate"] = (annual["ok_day_rate"] * 100).round(1)
    annual_path = OUT_DIR / "ok_day_annual_validation_summary.csv"
    annual.to_csv(annual_path, index=False)

    print(f"Wrote {model_path} ({len(model_data)} rows)")
    print(f"Wrote {monthly_path} ({len(monthly)} rows)")
    print(f"Wrote {annual_path} ({len(annual)} rows)")
    print()
    print("OK-day counts by zone:")
    print(model_data.groupby("zone")["ok_day"].agg(["sum", "mean"]).to_string())


if __name__ == "__main__":
    main()
