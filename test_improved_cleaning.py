"""
Test script to compare old vs improved data cleaning
"""

import pandas as pd
import os
import sys
sys.path.insert(0, 'src')
from src.data_cleaner import clean_data
from src.improved_data_cleaner import clean_data_improved

def test_cleaning_comparison():
    """Compare old vs improved cleaning methods"""
    
    # Load raw data
    output_dir = 'outputs'
    raw_files = [f for f in os.listdir(output_dir) if f.startswith('raw_extraction_') and f.endswith('.csv')]
    if not raw_files:
        print("No raw files found!")
        return
    
    latest_raw = max(raw_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
    raw_path = os.path.join(output_dir, latest_raw)
    
    print(f"Loading raw data from: {latest_raw}")
    raw_df = pd.read_csv(raw_path)
    print(f"Raw data: {len(raw_df)} rows")
    
    # Test old cleaning method
    print(f"\n" + "="*60)
    print("TESTING OLD CLEANING METHOD")
    print("="*60)
    old_cleaned = clean_data(raw_df.copy())
    print(f"Old method result: {len(old_cleaned)} rows")
    old_data_loss = len(raw_df) - len(old_cleaned)
    old_loss_percent = (old_data_loss / len(raw_df)) * 100
    print(f"Old method data loss: {old_data_loss} rows ({old_loss_percent:.1f}%)")
    
    # Test improved cleaning method
    print(f"\n" + "="*60)
    print("TESTING IMPROVED CLEANING METHOD")
    print("="*60)
    new_cleaned = clean_data_improved(raw_df.copy())
    print(f"Improved method result: {len(new_cleaned)} rows")
    new_data_loss = len(raw_df) - len(new_cleaned)
    new_loss_percent = (new_data_loss / len(raw_df)) * 100
    print(f"Improved method data loss: {new_data_loss} rows ({new_loss_percent:.1f}%)")
    
    # Compare results
    print(f"\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)
    improvement = len(new_cleaned) - len(old_cleaned)
    improvement_percent = (improvement / len(old_cleaned)) * 100 if len(old_cleaned) > 0 else 0
    
    print(f"Data recovery improvement: +{improvement} rows ({improvement_percent:.1f}%)")
    print(f"Old method efficiency: {((len(old_cleaned) / len(raw_df)) * 100):.1f}%")
    print(f"New method efficiency: {((len(new_cleaned) / len(raw_df)) * 100):.1f}%")
    
    # Check data quality
    if len(new_cleaned) > 0:
        print(f"\nData quality check:")
        print(f"Unique colleges (new): {new_cleaned['NAME OF THE COLLEGE'].nunique()}")
        print(f"Unique programs (new): {new_cleaned['NAME OF THE PROGRAM'].nunique()}")
        
        # Check for valid data
        valid_rows = new_cleaned[
            (new_cleaned['NAME OF THE COLLEGE'].str.strip() != '') & 
            (new_cleaned['NAME OF THE PROGRAM'].str.strip() != '')
        ]
        print(f"Rows with valid college & program: {len(valid_rows)}/{len(new_cleaned)} ({(len(valid_rows)/len(new_cleaned)*100):.1f}%)")
        
        # Show sample
        print(f"\nSample of improved cleaned data:")
        print(new_cleaned.head().to_string())
    
    # Save improved results for testing
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    improved_file = os.path.join(output_dir, f"DU_Admission_Improved_Clean_{timestamp}.csv")
    new_cleaned.to_csv(improved_file, index=False)
    print(f"\nImproved cleaned data saved to: {improved_file}")
    
    return {
        'raw_rows': len(raw_df),
        'old_cleaned_rows': len(old_cleaned),
        'new_cleaned_rows': len(new_cleaned),
        'improvement': improvement,
        'new_efficiency': (len(new_cleaned) / len(raw_df)) * 100
    }

if __name__ == "__main__":
    test_cleaning_comparison()
