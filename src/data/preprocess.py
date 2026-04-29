import pandas as pd
import numpy as np
import yaml
import os

def load_params():
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)

def preprocess(raw_path: str, processed_path: str):
    print(f"[preprocess] Loading raw data from {raw_path}")
    df = pd.read_csv(raw_path)
    print(f"[preprocess] Raw shape: {df.shape}")

    # ── Rename columns to snake_case ──────────────────────────────────────────
    df.columns = [c.replace(".", "_") for c in df.columns]

    # ── Drop rows with any nulls ──────────────────────────────────────────────
    df = df.dropna()

    # ── Feature engineering ───────────────────────────────────────────────────
    # Month-based seasonality flags
    df["is_peak_season"] = df["Month"].apply(
        lambda m: 1 if m in [10, 11, 12, 1, 2] else 0
    )

    # Volume/Weight ratio — proxy for fish density/scarcity
    df["volume_weight_ratio"] = (
        df["Production_Volume_tonnes"] / (df["Weight_g"] + 1)
    )

    # Body mass index proxy
    df["bmi_proxy"] = df["Weight_g"] / (df["Length_cm"] ** 2 + 1)

    # Cost to price ratio
    df["cost_price_ratio"] = df["Cost_TL"] / (df["Price_TL"] + 1)

    # Wind impact on fishing days
    df["wind_impact"] = df["Wind_Speed_kmh"] / (df["Active_Fishing_Days"] + 1)

    # ── Encode categoricals ───────────────────────────────────────────────────
    df = pd.get_dummies(df, columns=["Species", "Fishing_Area"], drop_first=False)

    # ── Save processed data ───────────────────────────────────────────────────
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df.to_csv(processed_path, index=False)
    print(f"[preprocess] Processed shape: {df.shape}")
    print(f"[preprocess] Saved to {processed_path}")
    return df

if __name__ == "__main__":
    params = load_params()
    preprocess(
        raw_path=params["data"]["raw_path"],
        processed_path=params["data"]["processed_path"]
    )
