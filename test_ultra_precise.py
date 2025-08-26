#!/usr/bin/env python3
"""
Test the Ultra-Precise Data Cleaner to get exactly 1528 rows
"""

import sys
sys.path.insert(0, 'src')

import pandas as pd
from src.ultra_precise_cleaner import ultra_precise_clean_data
import os
from datetime import datetime

def test_ultra_precise_cleaner():
    """Test the ultra-precise data cleaner"""
    print("🎯 Testing Ultra-Precise Data Cleaner...")
    
    # Load the latest raw data
    raw_file = 'outputs/raw_extraction_20250826_022226.csv'
    if not os.path.exists(raw_file):
        print(f"❌ Raw file not found: {raw_file}")
        return
    
    # Load raw data
    raw_df = pd.read_csv(raw_file)
    print(f"📊 Raw data: {len(raw_df)} rows")
    
    # Test ultra-precise cleaning
    print("\n🎯 Running ultra-precise cleaning...")
    ultra_cleaned_df = ultra_precise_clean_data(raw_df)
    
    print(f"\n📈 ULTRA-PRECISE CLEANING RESULTS:")
    print(f"   Raw rows: {len(raw_df)}")
    print(f"   Clean rows: {len(ultra_cleaned_df)}")
    print(f"   Target: 1528 rows")
    print(f"   Achievement: {'✅ PERFECT!' if len(ultra_cleaned_df) == 1528 else '❌ Not exact'}")
    
    # Check the specific examples you mentioned
    print(f"\n🔍 Checking specific examples...")
    
    # Delhi School of Journalism
    journalism_rows = ultra_cleaned_df[ultra_cleaned_df['NAME OF THE COLLEGE'].str.contains('Delhi School of Journalism', na=False)]
    print(f"   Delhi School of Journalism: {len(journalism_rows)} rows")
    if len(journalism_rows) > 0:
        prog = journalism_rows.iloc[0]['NAME OF THE PROGRAM']
        print(f"     Program: {prog}")
    
    # Check unique colleges
    unique_colleges = ultra_cleaned_df['NAME OF THE COLLEGE'].nunique()
    print(f"   Unique colleges: {unique_colleges} (target: ~93)")
    
    # Check for problematic college names
    evening_colleges = ultra_cleaned_df[ultra_cleaned_df['NAME OF THE COLLEGE'] == '(Evening)']
    w_colleges = ultra_cleaned_df[ultra_cleaned_df['NAME OF THE COLLEGE'] == '(W)']
    college_only = ultra_cleaned_df[ultra_cleaned_df['NAME OF THE COLLEGE'] == 'College']
    
    print(f"   Problematic colleges:")
    print(f"     '(Evening)' only: {len(evening_colleges)}")
    print(f"     '(W)' only: {len(w_colleges)}")
    print(f"     'College' only: {len(college_only)}")
    
    # Save the ultra-precise cleaned data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"outputs/DU_Admission_ULTRA_PRECISE_{timestamp}.csv"
    ultra_cleaned_df.to_csv(output_file, index=False)
    print(f"\n💾 Ultra-precise cleaned data saved to: {output_file}")
    
    # Show sample of college names to verify quality
    print(f"\n📋 Sample college names:")
    sample_colleges = ultra_cleaned_df['NAME OF THE COLLEGE'].unique()[:15]
    for i, college in enumerate(sample_colleges, 1):
        print(f"   {i:2d}. {college}")
    
    # Check for non-B programs
    print(f"\n🔍 Programs not starting with 'B.':")
    non_b_programs = ultra_cleaned_df[~ultra_cleaned_df['NAME OF THE PROGRAM'].str.startswith('B.', na=False)]
    print(f"   Found {len(non_b_programs)} non-B programs")
    for i, (_, row) in enumerate(non_b_programs.head(5).iterrows()):
        print(f"     {i+1}. {row['NAME OF THE COLLEGE']}: {row['NAME OF THE PROGRAM']}")
    
    return ultra_cleaned_df

if __name__ == "__main__":
    result = test_ultra_precise_cleaner()
    print("\n🎉 Ultra-precise cleaning test complete!")
