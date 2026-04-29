import pandas as pd
import numpy as np
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, RegressionPreset
from evidently.pipeline.column_mapping import ColumnMapping
import os

def run_drift_report():
    print("[Evidently] Loading data...")
    df = pd.read_csv("data/processed/fish_processed.csv")

    # Simulate reference (training) vs current (production) split
    split = int(len(df) * 0.8)
    reference = df.iloc[:split].copy()
    current = df.iloc[split:].copy()

    # ── Price model drift ─────────────────────────────────────────────────────
    price_col_map = ColumnMapping(
        target="Price_TL",
        prediction=None,
        numerical_features=[
            "Month", "Weight_g", "Length_cm", "Width_cm", "Height_cm",
            "Age_years", "Quality_Score", "Season_Availability", "Cost_TL",
            "Wind_Speed_kmh", "Sea_Surface_Temp_C", "Active_Fishing_Days",
            "Production_Volume_tonnes", "Fishing_Ban_Flag",
            "is_peak_season", "bmi_proxy", "wind_impact"
        ]
    )

    price_report = Report(metrics=[DataDriftPreset()])
    price_report.run(
        reference_data=reference,
        current_data=current,
        column_mapping=price_col_map
    )

    os.makedirs("monitoring/reports", exist_ok=True)
    price_report.save_html("monitoring/reports/price_drift_report.html")
    print("[Evidently] Price drift report saved → monitoring/reports/price_drift_report.html")

    # ── Catch model drift ─────────────────────────────────────────────────────
    catch_col_map = ColumnMapping(
        target="Production_Volume_tonnes",
        prediction=None,
        numerical_features=[
            "Month", "Weight_g", "Length_cm", "Width_cm", "Height_cm",
            "Age_years", "Quality_Score", "Season_Availability", "Cost_TL",
            "Wind_Speed_kmh", "Sea_Surface_Temp_C", "Active_Fishing_Days",
            "Fishing_Ban_Flag", "is_peak_season", "bmi_proxy", "wind_impact"
        ]
    )

    catch_report = Report(metrics=[DataDriftPreset()])
    catch_report.run(
        reference_data=reference,
        current_data=current,
        column_mapping=catch_col_map
    )
    catch_report.save_html("monitoring/reports/catch_drift_report.html")
    print("[Evidently] Catch drift report saved → monitoring/reports/catch_drift_report.html")

    print("\n✅ Drift monitoring complete. Open HTML reports in browser.")

if __name__ == "__main__":
    run_drift_report()
