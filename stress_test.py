import os
import time
import requests
import pandas as pd
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
DATA_FILE = Path("data/raw/lending_data.csv")
BENCHMARK_DIR = Path("benchmarks")

size = 250000

print(f"Generating realistic stress test dataset ({size} rows)...")
df_base = pd.read_csv(DATA_FILE)
multiplier = (size // len(df_base)) + 1
df_new = pd.concat([df_base] * multiplier, ignore_index=True)
df_new = df_new.head(size)

df_new['member_id'] = [(size * 1000000) + i for i in range(size)]
if 'id' in df_new.columns:
    df_new['id'] = [f"ID-{size}-{i}" for i in range(size)]

out_path = BENCHMARK_DIR / f"stress_dataset_{size}.csv"
df_new.to_csv(out_path, index=False)
print(f"Generated {out_path} ({os.path.getsize(out_path) / 1024 / 1024:.2f} MB)")

print("\nRunning ingestion stress test...")
start_time = time.time()
with open(out_path, "rb") as f:
    response = requests.post(f"{BASE_URL}/ingestion/upload", files={"file": f})

elapsed = time.time() - start_time
if response.status_code == 200:
    data = response.json()
    t_total = data.get("ingestion_time", elapsed)
    t_val = data.get("validation_time", 0)
    t_db = data.get("db_insertion_time", 0)
    print(f"  Success! Total: {t_total:.2f}s (Val: {t_val:.2f}s, DB: {t_db:.2f}s)")
else:
    print(f"  Failed! Status {response.status_code}, {response.text}")
