import os
import time
import requests
import joblib
import pandas as pd
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
DATA_FILE = Path("data/raw/lending_data.csv")

if not DATA_FILE.exists():
    print("Dataset not found!")
    exit(1)

print("=========================================")
print("LENDING CLUB FULL PLATFORM VALIDATION")
print("=========================================")
print(f"Dataset: {DATA_FILE.name} ({os.path.getsize(DATA_FILE) / 1024 / 1024:.2f} MB)")

# 1. Ingestion
print("\n[1] Uploading Dataset...")
start_time = time.time()
with open(DATA_FILE, "rb") as f:
    res = requests.post(f"{BASE_URL}/ingestion/upload", files={"file": f})
upload_time = time.time() - start_time
print("Status:", res.status_code)
if res.status_code == 200:
    data = res.json()
    print("Ingestion Summary:", data)
else:
    print("Error:", res.text)
    exit(1)

# 2. Feature Engineering
print("\n[2] Triggering Feature Engineering...")
start_time = time.time()
res = requests.post(f"{BASE_URL}/ml/features/generate")
fe_time = time.time() - start_time
print("Status:", res.status_code)
if res.status_code == 200:
    print("Feature Engineering Summary:", res.json())
else:
    print("Error:", res.text)
    exit(1)

# 3. Model Training
print("\n[3] Triggering Model Training...")
start_time = time.time()
res = requests.post(f"{BASE_URL}/ml/train")
train_time = time.time() - start_time
print("Status:", res.status_code)
if res.status_code == 200:
    metadata = res.json()
    print("\n=========================================")
    print("TRAINING METRICS")
    print(f"Model: {metadata.get('model_name')}")
    print(f"Dataset Mode: {metadata.get('dataset_mode')}")
    print(f"Training Rows: {metadata.get('training_rows')}")
    print(f"Feature Count: {metadata.get('feature_count')}")
    print("\nMetrics:")
    metrics = metadata.get('metrics', {})
    for k, v in metrics.items():
        if k != "confusion_matrix":
            print(f"  {k}: {v:.4f}")
    print("\nConfusion Matrix:")
    for row in metrics.get('confusion_matrix', []):
        print("  ", row)
else:
    print("Error:", res.text)
    exit(1)

# 4. Feature Importance
print("\n[4] Extracting Feature Importance...")
try:
    model = joblib.load("artifacts/models/best_model.joblib")
    preprocessor = joblib.load("artifacts/models/preprocessing_pipeline.joblib")
    
    # Try to get feature names
    try:
        feature_names = preprocessor.get_feature_names_out()
    except:
        feature_names = [f"Feature {i}" for i in range(metadata.get('feature_count'))]
        
    importances = None
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = abs(model.coef_[0])
        
    if importances is not None:
        importance_df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
        importance_df = importance_df.sort_values(by="Importance", ascending=False).head(20)
        print(importance_df.to_string(index=False))
    else:
        print("Model does not support feature_importances_.")
except Exception as e:
    print("Error extracting feature importance:", e)

# 5. Held-Out Prediction Example
print("\n[5] Held-Out Prediction Test...")
# Take top 5 rows from dataset
df_base = pd.read_csv(DATA_FILE).head(5)
test_file = Path("benchmarks/held_out_test.csv")
df_base.to_csv(test_file, index=False)

start_time = time.time()
with open(test_file, "rb") as f:
    res = requests.post(f"{BASE_URL}/ml/predict", files={"file": f})
pred_time = time.time() - start_time

if res.status_code == 200:
    preds = res.json().get("predictions", [])
    print(f"Prediction successful ({pred_time:.2f}s). Showing 5 examples:")
    for p in preds:
        print(f"  ID: {p['id']} -> {p['risk_category']} (Prob: {p['probability']:.4f}, Confidence: {p['confidence_score']:.4f})")
else:
    print("Error:", res.text)

print("\n--- TIMING SUMMARY ---")
print(f"Total Upload/Ingestion: {data.get('ingestion_time', upload_time):.2f}s")
print(f"  - Validation: {data.get('validation_time', 0):.2f}s")
print(f"  - DB Insertion: {data.get('db_insertion_time', 0):.2f}s")
print(f"Feature Engineering: {fe_time:.2f}s")
print(f"Model Training: {train_time:.2f}s")
