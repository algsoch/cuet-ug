#!/usr/bin/env python3

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the cleaner
from src.data_cleaner import DataCleaner

# Load the latest raw data
raw_file = 'outputs/raw_extraction_20250825_234600.csv'
df = pd.read_csv(raw_file)

print(f"Loaded {len(df)} rows")

# Look at the specific corruption area
print("\nRows around the corruption (1190-1210):")
for i in range(1190, min(1210, len(df))):
    row = df.iloc[i]
    print(f"Row {i}: {list(row)}")

# Test the corruption detection
cleaner = DataCleaner()

print("\nTesting corruption detection on specific rows:")
for i in [1195, 1196, 1198, 1199]:  # The problematic rows
    if i < len(df):
        row = df.iloc[i]
        is_corrupted = cleaner._has_corrupted_program_name(row)
        program = str(row.iloc[2]).strip() if len(row) > 2 else "N/A"
        print(f"Row {i}: '{program}' -> Corrupted: {is_corrupted}")

# Test incomplete detection
print("\nTesting incomplete program detection:")
for i in [1194, 1195, 1197, 1198]:  # The rows that might be incomplete
    if i < len(df):
        row = df.iloc[i]
        program = str(row.iloc[2]).strip() if len(row) > 2 else "N/A"
        
        # Test if this row would be found as incomplete from future rows
        incomplete_idx = cleaner._find_incomplete_program_above(df, i + 5)
        print(f"Row {i}: '{program}' -> Found as incomplete from future rows: {incomplete_idx == i}")
