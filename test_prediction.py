import requests
import pandas as pd
import io

url = "http://127.0.0.1:8000/ml/predict"

# 1. Valid CSV
print("Testing Valid CSV...")
valid_csv = """loan_amnt,int_rate,annual_inc,fico_range_low,fico_range_high,term,grade,home_ownership,addr_state,member_id
10000,10.5,50000,700,704,36 months,A,RENT,NY,APP-1
20000,15.5,60000,650,654,60 months,C,OWN,CA,APP-2
"""
files = {'file': ('test.csv', io.StringIO(valid_csv), 'text/csv')}
response = requests.post(url, files=files)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# 2. Invalid CSV (missing annual_inc)
print("Testing Invalid CSV...")
invalid_csv = """loan_amnt,int_rate,fico_range_low,fico_range_high,term,grade,home_ownership,addr_state
10000,10.5,700,704,36 months,A,RENT,NY
"""
files2 = {'file': ('test2.csv', io.StringIO(invalid_csv), 'text/csv')}
response2 = requests.post(url, files=files2)
print(f"Status: {response2.status_code}")
print(f"Response: {response2.json()}\n")

# 3. Not CSV extension
print("Testing Not CSV Extension...")
files3 = {'file': ('test3.txt', io.StringIO(valid_csv), 'text/plain')}
response3 = requests.post(url, files=files3)
print(f"Status: {response3.status_code}")
print(f"Response: {response3.json()}\n")

