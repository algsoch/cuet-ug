#!/usr/bin/env python3
"""
Analyze the context of problematic college names
"""

import pandas as pd

# Load raw data and look for problematic patterns
raw_df = pd.read_csv('outputs/raw_extraction_20250826_022226.csv')

print('Looking at raw data around problematic S.NO. ranges...')

# Find rows with these S.NO. values
target_snos = [130, 131, 132, 201, 202, 203, 221, 222, 223, 225]

for target_sno in target_snos:
    for i, row in raw_df.iterrows():
        sno = str(row.iloc[0]).strip()
        if sno == str(target_sno):
            college = str(row.iloc[1]).strip()
            program = str(row.iloc[2]).strip()
            print(f'S.NO.{sno}: College="{college}", Program="{program}"')
            
            # Look for context before this row
            print(f'  Context before (rows {i-5} to {i-1}):')
            for j in range(max(0, i-5), i):
                if j < len(raw_df):
                    ctx_row = raw_df.iloc[j]
                    ctx_sno = str(ctx_row.iloc[0]).strip()
                    ctx_college = str(ctx_row.iloc[1]).strip()
                    ctx_program = str(ctx_row.iloc[2]).strip()
                    print(f'    Row {j}: S.NO.="{ctx_sno}", College="{ctx_college}", Program="{ctx_program}"')
            print('---')
            break
