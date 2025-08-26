#!/usr/bin/env python3
"""
Script to find all split college name patterns in raw data
"""

import pandas as pd

# Load the latest raw data
df = pd.read_csv('outputs/raw_extraction_20250826_022226.csv')
print(f'Total raw rows: {len(df)}')

# Find all patterns where college names are split
print('\nFinding all split college name patterns...')
split_patterns = []

for i in range(len(df) - 1):
    current_row = df.iloc[i]
    next_row = df.iloc[i + 1]
    
    # Check if current row has college name but no S.NO. and all zeros
    current_sno = str(current_row.iloc[0]).strip()
    current_college = str(current_row.iloc[1]).strip() if len(current_row) > 1 else ''
    
    # Check if next row has 'College' as college name and has S.NO.
    next_sno = str(next_row.iloc[0]).strip()
    next_college = str(next_row.iloc[1]).strip() if len(next_row) > 1 else ''
    
    # Pattern: current row has college name but no S.NO., next row has 'College' + S.NO.
    if (current_sno in ['nan', ''] and 
        current_college not in ['nan', '', 'College'] and 
        next_sno.isdigit() and 
        next_college == 'College'):
        
        split_patterns.append({
            'row_i': i,
            'college_part1': current_college,
            'row_next': i + 1,
            'college_part2': next_college,
            'sno': next_sno
        })
        
        if len(split_patterns) <= 10:  # Show first 10 examples
            print(f'Split Pattern {len(split_patterns)}:')
            print(f'  Row {i}: {current_row.tolist()}')
            print(f'  Row {i+1}: {next_row.tolist()}')
            print(f'  Should merge: "{current_college} {next_college}"')
            print('---')

print(f'\nFound {len(split_patterns)} total split college name patterns!')

# Also check for other split patterns
print('\nChecking for program name split patterns...')
program_splits = 0

for i in range(len(df) - 1):
    current_row = df.iloc[i]
    next_row = df.iloc[i + 1]
    
    current_program = str(current_row.iloc[2]).strip() if len(current_row) > 2 else ''
    next_program = str(next_row.iloc[2]).strip() if len(next_row) > 2 else ''
    
    # Look for incomplete programs ending with "B.A" and next row starting with degree type
    if (current_program.endswith('B.A') or current_program.endswith('B.Sc') or current_program.endswith('B.Com')) and next_program.startswith('('):
        program_splits += 1
        if program_splits <= 5:
            print(f'Program Split {program_splits}: "{current_program}" + "{next_program}"')

print(f'\nFound {program_splits} potential program split patterns!')
