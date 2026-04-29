# run_pipeline.ps1
# Run this script from the KharviML root directory in PowerShell
# Usage: .\run_pipeline.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  KharviML Pipeline Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1 - Install dependencies
Write-Host "`n[1/6] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Step 2 - Preprocess data
Write-Host "`n[2/6] Preprocessing data..." -ForegroundColor Yellow
python src/data/preprocess.py

# Step 3 - Train models (MLflow must be running)
Write-Host "`n[3/6] Starting MLflow server in background..." -ForegroundColor Yellow
Write-Host "Open http://localhost:5000 to view experiments" -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "mlflow" -ArgumentList "ui --host 0.0.0.0 --port 5000"
Start-Sleep -Seconds 3

Write-Host "`n[4/6] Training price model..." -ForegroundColor Yellow
python src/models/train_price.py

Write-Host "`n[5/6] Training catch model..." -ForegroundColor Yellow
python src/models/train_catch.py

# Step 4 - Start API locally
Write-Host "`n[6/6] Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "API docs at http://localhost:8000/docs" -ForegroundColor Green
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
