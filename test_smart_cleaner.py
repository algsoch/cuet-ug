#!/usr/bin/env python3
"""
Test the Smart Data Cleaner to ensure maximum data preservation
"""

import sys
sys.path.insert(0, 'src')

import pandas as pd
from src.smart_data_cleaner import smart_clean_data
import os
from datetime import datetime

def test_smart_cleaner():
    """Test the smart data cleaner"""
    print("🧹 Testing Smart Data Cleaner...")
    
    # Load the latest raw data
    raw_file = 'outputs/raw_extraction_20250826_022226.csv'
    if not os.path.exists(raw_file):
        print(f"❌ Raw file not found: {raw_file}")
        return
    
    # Load raw data
    raw_df = pd.read_csv(raw_file)
    print(f"📊 Raw data: {len(raw_df)} rows")
    
    # Test smart cleaning
    print("\n🎯 Running smart cleaning...")
    smart_cleaned_df = smart_clean_data(raw_df)
    
    # Calculate efficiency
    efficiency = (len(smart_cleaned_df) / len(raw_df)) * 100
    data_loss = len(raw_df) - len(smart_cleaned_df)
    
    print(f"\n📈 SMART CLEANING RESULTS:")
    print(f"   Raw rows: {len(raw_df)}")
    print(f"   Clean rows: {len(smart_cleaned_df)}")
    print(f"   Data loss: {data_loss} rows ({100-efficiency:.1f}%)")
    print(f"   Data efficiency: {efficiency:.1f}%")
    
    # Check the specific college that was problematic
    print(f"\n🔍 Checking Sri Guru Tegh Bahadur Khalsa College...")
    khalsa_rows = smart_cleaned_df[smart_cleaned_df['NAME OF THE COLLEGE'].str.contains('Sri Guru Tegh Bahadur Khalsa', na=False)]
    print(f"   Found {len(khalsa_rows)} rows for this college")
    
    if len(khalsa_rows) > 0:
        print("   Sample programs:")
        for i, (_, row) in enumerate(khalsa_rows.head(3).iterrows()):
            print(f"     {i+1}. {row['NAME OF THE PROGRAM']} (Seats: {row['UR'] + row['OBC'] + row['SC'] + row['ST'] + row['EWS'] + row['SIKH'] + row['PwBD']})")
    
    # Save the smart cleaned data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"outputs/DU_Admission_SMART_Clean_{timestamp}.csv"
    smart_cleaned_df.to_csv(output_file, index=False)
    print(f"\n💾 Smart cleaned data saved to: {output_file}")
    
    # Verify data quality
    print(f"\n✅ DATA QUALITY CHECK:")
    print(f"   Unique colleges: {smart_cleaned_df['NAME OF THE COLLEGE'].nunique()}")
    print(f"   Unique programs: {smart_cleaned_df['NAME OF THE PROGRAM'].nunique()}")
    print(f"   Total seats: {smart_cleaned_df[['UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']].sum().sum()}")
    
    # Check for any remaining issues
    empty_colleges = smart_cleaned_df[smart_cleaned_df['NAME OF THE COLLEGE'].str.strip() == '']
    empty_programs = smart_cleaned_df[smart_cleaned_df['NAME OF THE PROGRAM'].str.strip() == '']
    print(f"   Empty colleges: {len(empty_colleges)}")
    print(f"   Empty programs: {len(empty_programs)}")
    
    # Compare with previous cleaning
    previous_file = 'outputs/DU_Admission_Improved_Clean_20250826_021637.csv'
    if os.path.exists(previous_file):
        prev_df = pd.read_csv(previous_file)
        improvement = len(smart_cleaned_df) - len(prev_df)
        print(f"\n🚀 IMPROVEMENT OVER PREVIOUS CLEANING:")
        print(f"   Previous: {len(prev_df)} rows")
        print(f"   Smart: {len(smart_cleaned_df)} rows")
        print(f"   Improvement: +{improvement} rows ({(improvement/len(prev_df)*100):.1f}% more data!)")
    
    return smart_cleaned_df

if __name__ == "__main__":
    result = test_smart_cleaner()
    print("\n🎉 Smart cleaning test complete!")
