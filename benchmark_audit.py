import os
import time
import psutil
import requests
import pandas as pd
from pathlib import Path

# Paths and URLs
BASE_URL = "http://127.0.0.1:8000"
DATA_FILE = Path("data/raw/lending_data.csv")
BENCHMARK_DIR = Path("benchmarks")
BENCHMARK_DIR.mkdir(exist_ok=True)

# Sizes to test
SIZES = [100, 1000, 5000, 10000, 25000, 50000, 100000]

def get_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024 # MB

def generate_datasets():
    print("Generating datasets...")
    df_base = pd.read_csv(DATA_FILE)
    for size in SIZES:
        multiplier = (size // len(df_base)) + 1
        df_new = pd.concat([df_base] * multiplier, ignore_index=True)
        df_new = df_new.head(size)
        
        # Make member_ids unique but NUMERIC to pass schema validation
        df_new['member_id'] = [(size * 1000000) + i for i in range(size)]
        # For 'id' column if it exists
        if 'id' in df_new.columns:
            df_new['id'] = [f"ID-{size}-{i}" for i in range(size)]
            
        out_path = BENCHMARK_DIR / f"dataset_{size}.csv"
        df_new.to_csv(out_path, index=False)
        print(f"Generated {out_path} ({os.path.getsize(out_path) / 1024 / 1024:.2f} MB)")

def test_ingestion():
    print("\n--- SECTION 1: INGESTION CAPACITY ---")
    results = []
    for size in SIZES:
        file_path = BENCHMARK_DIR / f"dataset_{size}.csv"
        if not file_path.exists(): continue
        
        print(f"Testing Upload {size} rows...")
        start_time = time.time()
        start_mem = get_memory()
        
        try:
            with open(file_path, "rb") as f:
                response = requests.post(f"{BASE_URL}/ingestion/upload", files={"file": f})
                
            elapsed = time.time() - start_time
            peak_mem = get_memory() - start_mem
            
            if response.status_code == 200:
                data = response.json()
                t_total = data.get("ingestion_time", elapsed)
                t_val = data.get("validation_time", 0)
                t_db = data.get("db_insertion_time", 0)
                print(f"  Success! Total: {t_total:.2f}s (Val: {t_val:.2f}s, DB: {t_db:.2f}s), Mem: {peak_mem:.2f}MB")
                results.append({"size": size, "status": "Success", "time": t_total, "val_time": t_val, "db_time": t_db, "mem": peak_mem})
            else:
                print(f"  Failed! Status {response.status_code}, {response.text}")
                results.append({"size": size, "status": f"Failed ({response.status_code})", "time": elapsed, "mem": peak_mem})
        except Exception as e:
            print(f"  Exception! {str(e)}")
            results.append({"size": size, "status": "Exception", "time": -1, "mem": -1})
    return results

def test_prediction():
    print("\n--- SECTION 5: PREDICTION ENGINE ---")
    results = []
    # Test only up to 10,000 for prediction
    for size in [10, 100, 1000, 10000]:
        file_path = BENCHMARK_DIR / f"dataset_{size}.csv"
        if not file_path.exists():
            # Generate 10 row specifically
            df_base = pd.read_csv(DATA_FILE).head(10)
            df_base.to_csv(BENCHMARK_DIR / "dataset_10.csv", index=False)
            file_path = BENCHMARK_DIR / "dataset_10.csv"
            
        print(f"Testing Prediction {size} rows...")
        start_time = time.time()
        
        try:
            with open(file_path, "rb") as f:
                response = requests.post(f"{BASE_URL}/ml/predict", files={"file": f})
                
            elapsed = time.time() - start_time
            if response.status_code == 200:
                print(f"  Success! Time: {elapsed:.2f}s")
                results.append({"size": size, "status": "Success", "time": elapsed})
            else:
                print(f"  Failed! Status {response.status_code}, {response.text}")
        except Exception as e:
            print(f"  Exception! {str(e)}")
    return results

if __name__ == "__main__":
    generate_datasets()
    ingest_res = test_ingestion()
    pred_res = test_prediction()
