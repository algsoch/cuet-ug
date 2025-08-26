#!/usr/bin/env python3

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the cleaner
from src.data_cleaner import DataCleaner

# Load the data at different stages
raw_file = 'outputs/raw_extraction_20250825_235104.csv'
df_raw = pd.read_csv(raw_file)

print(f"Raw data: {len(df_raw)} rows")

# Simulate the cleaning process step by step
cleaner = DataCleaner()

# Step 1-3: Basic cleaning (simulate these)
df = df_raw.copy()

# Remove headers and do basic cleanup to get to the pre-corruption state
print("\nSimulating basic cleanup to get to corruption step...")

# Just look at the specific problematic area
start_idx = 1190
end_idx = 1200

print(f"\nRaw data around corruption (rows {start_idx}-{end_idx}):")
for i in range(start_idx, min(end_idx, len(df_raw))):
    if i < len(df_raw):
        row = df_raw.iloc[i]
        s_no = str(row.iloc[0]) if pd.notna(row.iloc[0]) else "NaN"
        college = str(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[1]) else "NaN"
        program = str(row.iloc[2]) if len(row) > 2 and pd.notna(row.iloc[2]) else "NaN"
        print(f"Row {i}: S.NO='{s_no}' | College='{college}' | Program='{program}'")

print(f"\nTesting corruption detection:")
for i in range(start_idx, min(end_idx, len(df_raw))):
    if i < len(df_raw):
        row = df_raw.iloc[i]
        is_corrupted = cleaner._has_corrupted_program_name(row)
        program = str(row.iloc[2]) if len(row) > 2 else "N/A"
        print(f"Row {i}: Corrupted={is_corrupted} | Program='{program}'")

print(f"\nTesting incomplete detection:")
for i in range(start_idx, min(end_idx, len(df_raw))):
    if i < len(df_raw):
        incomplete_idx = cleaner._find_incomplete_program_above(df_raw, i)
        program = str(df_raw.iloc[i].iloc[2]) if len(df_raw.iloc[i]) > 2 else "N/A"
        print(f"Row {i}: Program='{program}' | Found incomplete at: {incomplete_idx}")
