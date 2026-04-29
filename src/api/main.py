from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
import joblib
import numpy as np
import pandas as pd
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="KharviML Fish Prediction API",
    description="Predicts fish price and catch volume for Turkish coastal regions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Prometheus metrics ────────────────────────────────────────────────────────
Instrumentator().instrument(app).expose(app)

# ── Load models on startup ────────────────────────────────────────────────────
MODEL_DIR = os.getenv("MODEL_DIR", "models")

price_model = joblib.load(f"{MODEL_DIR}/price_model.pkl")
price_scaler = joblib.load(f"{MODEL_DIR}/price_scaler.pkl")
price_features = joblib.load(f"{MODEL_DIR}/price_feature_cols.pkl")

catch_model = joblib.load(f"{MODEL_DIR}/catch_model.pkl")
catch_scaler = joblib.load(f"{MODEL_DIR}/catch_scaler.pkl")
catch_features = joblib.load(f"{MODEL_DIR}/catch_feature_cols.pkl")


# ── Request schemas ───────────────────────────────────────────────────────────
class PricePredictRequest(BaseModel):
    species: str           # e.g. "Hamsi (Anchovy)"
    fishing_area: str      # e.g. "Black Sea"
    month: int             # 1-12
    weight_g: float
    length_cm: float
    width_cm: float
    height_cm: float
    age_years: int
    quality_score: float
    season_availability: float
    cost_tl: float
    wind_speed_kmh: float
    sea_surface_temp_c: float
    active_fishing_days: int
    fishing_ban_flag: int


class CatchPredictRequest(BaseModel):
    species: str
    fishing_area: str
    month: int
    weight_g: float
    length_cm: float
    width_cm: float
    height_cm: float
    age_years: int
    quality_score: float
    season_availability: float
    cost_tl: float
    wind_speed_kmh: float
    sea_surface_temp_c: float
    active_fishing_days: int
    fishing_ban_flag: int


def build_feature_row(req_dict: dict, feature_cols: list) -> np.ndarray:
    """Build a feature vector matching training columns."""
    species_cols = [
        "Species_Çipura (Sea Bream)", "Species_Hamsi (Anchovy)",
        "Species_İstavrit (Horse Mackerel)", "Species_Kalkan (Turbot)",
        "Species_Levrek (Sea Bass)", "Species_Lüfer (Bluefish)",
        "Species_Palamut (Bonito)"
    ]
    area_cols = [
        "Fishing_Area_Aegean Sea", "Fishing_Area_Black Sea",
        "Fishing_Area_Marmara Sea", "Fishing_Area_Mediterranean Sea"
    ]

    row = {
        "Month": req_dict["month"],
        "Weight_g": req_dict["weight_g"],
        "Length_cm": req_dict["length_cm"],
        "Width_cm": req_dict["width_cm"],
        "Height_cm": req_dict["height_cm"],
        "Age_years": req_dict["age_years"],
        "Quality_Score": req_dict["quality_score"],
        "Season_Availability": req_dict["season_availability"],
        "Cost_TL": req_dict["cost_tl"],
        "Wind_Speed_kmh": req_dict["wind_speed_kmh"],
        "Sea_Surface_Temp_C": req_dict["sea_surface_temp_c"],
        "Active_Fishing_Days": req_dict["active_fishing_days"],
        "Fishing_Ban_Flag": req_dict["fishing_ban_flag"],
        "is_peak_season": 1 if req_dict["month"] in [10, 11, 12, 1, 2] else 0,
        "bmi_proxy": req_dict["weight_g"] / (req_dict["length_cm"] ** 2 + 1),
        "wind_impact": req_dict["wind_speed_kmh"] / (req_dict["active_fishing_days"] + 1),
    }

    # One-hot species
    for col in species_cols:
        species_name = col.replace("Species_", "")
        row[col] = 1 if req_dict["species"] == species_name else 0

    # One-hot area
    for col in area_cols:
        area_name = col.replace("Fishing_Area_", "")
        row[col] = 1 if req_dict["fishing_area"] == area_name else 0

    df_row = pd.DataFrame([row])

    # Align columns to training feature set
    for col in feature_cols:
        if col not in df_row.columns:
            df_row[col] = 0

    return df_row[feature_cols].values


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "KharviML Fish Prediction API is running 🐟"}


@app.post("/predict/price")
def predict_price(req: PricePredictRequest):
    try:
        X = build_feature_row(req.dict(), price_features)
        pred = price_model.predict(X)[0]
        return {
            "predicted_price_TL": round(float(pred), 2),
            "species": req.species,
            "fishing_area": req.fishing_area,
            "month": req.month
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/catch")
def predict_catch(req: CatchPredictRequest):
    try:
        X = build_feature_row(req.dict(), catch_features)
        pred = catch_model.predict(X)[0]
        return {
            "predicted_catch_tonnes": round(float(pred), 2),
            "species": req.species,
            "fishing_area": req.fishing_area,
            "month": req.month
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
