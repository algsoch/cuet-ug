#!/usr/bin/env python3
"""
Test the Proper Data Cleaner to get exactly 1528 rows
"""

import sys
sys.path.insert(0, 'src')

import pandas as pd
from src.proper_data_cleaner import proper_clean_data
import os
from datetime import datetime

def test_proper_cleaner():
    """Test the proper data cleaner"""
    print("🎯 Testing Proper Data Cleaner...")
    
    # Load the latest raw data
    raw_file = 'outputs/raw_extraction_20250826_022226.csv'
    if not os.path.exists(raw_file):
        print(f"❌ Raw file not found: {raw_file}")
        return
    
    # Load raw data
    raw_df = pd.read_csv(raw_file)
    print(f"📊 Raw data: {len(raw_df)} rows")
    
    # Test proper cleaning
    print("\n🎯 Running proper cleaning...")
    proper_cleaned_df = proper_clean_data(raw_df)
    
    print(f"\n📈 PROPER CLEANING RESULTS:")
    print(f"   Raw rows: {len(raw_df)}")
    print(f"   Clean rows: {len(proper_cleaned_df)}")
    print(f"   Target: 1528 rows")
    print(f"   Achievement: {'🎉 PERFECT!' if len(proper_cleaned_df) == 1528 else f'❌ Got {len(proper_cleaned_df)}'}")
    
    # Check the specific examples
    print(f"\n🔍 Checking specific examples...")
    
    # Delhi School of Journalism
    journalism_rows = proper_cleaned_df[proper_cleaned_df['NAME OF THE COLLEGE'].str.contains('Delhi School of Journalism', na=False)]
    print(f"   Delhi School of Journalism: {len(journalism_rows)} rows")
    if len(journalism_rows) > 0:
        prog = journalism_rows.iloc[0]['NAME OF THE PROGRAM']
        print(f"     Program: {prog}")
    
    # Hindu College patterns
    hindu_colleges = proper_cleaned_df[proper_cleaned_df['NAME OF THE COLLEGE'].str.contains('Hindu College', na=False)]
    print(f"   Hindu College variants: {len(hindu_colleges)} rows")
    hindu_college_names = hindu_colleges['NAME OF THE COLLEGE'].unique()
    for name in hindu_college_names[:5]:
        count = len(hindu_colleges[hindu_colleges['NAME OF THE COLLEGE'] == name])
        print(f"     '{name}': {count} programs")
    
    # Check unique colleges
    unique_colleges = proper_cleaned_df['NAME OF THE COLLEGE'].nunique()
    print(f"   Unique colleges: {unique_colleges} (target: ~93)")
    
    # Save the proper cleaned data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"outputs/DU_Admission_PROPER_Clean_{timestamp}.csv"
    proper_cleaned_df.to_csv(output_file, index=False)
    print(f"\n💾 Proper cleaned data saved to: {output_file}")
    
    # Show sample of college names to verify quality
    print(f"\n📋 Sample college names:")
    sample_colleges = proper_cleaned_df['NAME OF THE COLLEGE'].unique()[:15]
    for i, college in enumerate(sample_colleges, 1):
        count = len(proper_cleaned_df[proper_cleaned_df['NAME OF THE COLLEGE'] == college])
        print(f"   {i:2d}. {college} ({count} programs)")
    
    # Check for non-B programs
    print(f"\n🔍 Programs not starting with 'B.':")
    non_b_programs = proper_cleaned_df[~proper_cleaned_df['NAME OF THE PROGRAM'].str.startswith('B.', na=False)]
    print(f"   Found {len(non_b_programs)} non-B programs")
    for i, (_, row) in enumerate(non_b_programs.head(5).iterrows()):
        print(f"     {i+1}. {row['NAME OF THE COLLEGE']}: {row['NAME OF THE PROGRAM']}")
    
    return proper_cleaned_df

if __name__ == "__main__":
    result = test_proper_cleaner()
    print("\n🎉 Proper cleaning test complete!")
