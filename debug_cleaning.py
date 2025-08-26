"""
Debug script to identify where data is being lost during cleaning
"""

import pandas as pd
import os
import sys
sys.path.insert(0, 'src')
from src.data_cleaner import DataCleaner

def debug_cleaning_process():
    """Debug each step of the cleaning process to identify data loss"""
    
    # Load raw data
    output_dir = 'outputs'
    raw_files = [f for f in os.listdir(output_dir) if f.startswith('raw_extraction_') and f.endswith('.csv')]
    if not raw_files:
        print("No raw files found!")
        return
    
    latest_raw = max(raw_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
    raw_path = os.path.join(output_dir, latest_raw)
    
    print(f"Loading raw data from: {latest_raw}")
    df = pd.read_csv(raw_path)
    print(f"Initial raw data: {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    print(f"Sample data:")
    print(df.head(10).to_string())
    print("\n" + "="*80 + "\n")
    
    # Initialize cleaner
    cleaner = DataCleaner()
    
    # Step by step debugging
    print("STEP 1: Initial cleanup")
    df_step1 = cleaner._initial_cleanup(df.copy())
    print(f"After initial cleanup: {len(df_step1)} rows (lost: {len(df) - len(df_step1)})")
    
    print("\nSTEP 2: Identify columns")
    df_step2 = cleaner._identify_columns(df_step1.copy())
    print(f"After column identification: {len(df_step2)} rows (lost: {len(df_step1) - len(df_step2)})")
    print(f"Columns after step 2: {list(df_step2.columns)}")
    
    print("\nSTEP 3: Remove duplicate headers")
    df_step3 = cleaner._remove_duplicate_headers(df_step2.copy())
    print(f"After removing duplicate headers: {len(df_step3)} rows (lost: {len(df_step2) - len(df_step3)})")
    
    print("\nSTEP 4: Fix column misalignment")
    df_step4 = cleaner._fix_column_misalignment(df_step3.copy())
    print(f"After fixing column misalignment: {len(df_step4)} rows (lost: {len(df_step3) - len(df_step4)})")
    
    print("\nSTEP 5: Fix corrupted program names")
    df_step5 = cleaner._fix_corrupted_program_names(df_step4.copy())
    print(f"After fixing corrupted programs: {len(df_step5)} rows (lost: {len(df_step4) - len(df_step5)})")
    
    print("\nSTEP 6: Merge split rows")
    df_step6 = cleaner._merge_split_rows(df_step5.copy())
    print(f"After merging split rows: {len(df_step6)} rows (lost: {len(df_step5) - len(df_step6)})")
    
    print("\nSTEP 7: Normalize columns")
    df_step7 = cleaner._normalize_columns(df_step6.copy())
    print(f"After normalizing columns: {len(df_step7)} rows (lost: {len(df_step6) - len(df_step7)})")
    
    print("\nSTEP 8: Convert numeric columns")
    df_step8 = cleaner._convert_numeric_columns(df_step7.copy())
    print(f"After converting numeric: {len(df_step8)} rows (lost: {len(df_step7) - len(df_step8)})")
    
    print("\nSTEP 9: Clean text columns")
    df_step9 = cleaner._clean_text_columns(df_step8.copy())
    print(f"After cleaning text: {len(df_step9)} rows (lost: {len(df_step8) - len(df_step9)})")
    
    print("\nSTEP 10: Final validation")
    df_final = cleaner._final_validation(df_step9.copy())
    print(f"After final validation: {len(df_final)} rows (lost: {len(df_step9) - len(df_final)})")
    
    print(f"\n" + "="*80)
    print(f"TOTAL DATA LOSS: {len(df)} -> {len(df_final)} rows")
    print(f"Lost: {len(df) - len(df_final)} rows ({((len(df) - len(df_final)) / len(df) * 100):.1f}%)")
    
    # Show samples of what's being kept vs lost
    print(f"\nSample of final cleaned data:")
    print(df_final.head(10).to_string())
    
    # Check what kind of rows are being removed
    print(f"\nAnalyzing removed rows...")
    
    # Find rows that were present in step 3 but removed in final validation
    if len(df_step3) > len(df_final):
        print(f"Major loss happened between step 3 and final: {len(df_step3)} -> {len(df_final)}")
        
        # Check what final validation is removing
        print("\nChecking final validation criteria...")
        
        # Simulate final validation checks
        before_college_filter = len(df_step9)
        has_college = df_step9['NAME OF THE COLLEGE'].str.strip() != ''
        after_college_filter = has_college.sum()
        print(f"Rows with valid college names: {after_college_filter}/{before_college_filter}")
        
        # Check rows with empty college names
        empty_college_rows = df_step9[~has_college]
        print(f"Rows with empty college names: {len(empty_college_rows)}")
        if len(empty_college_rows) > 0:
            print("Sample empty college rows:")
            print(empty_college_rows.head().to_string())

if __name__ == "__main__":
    debug_cleaning_process()
