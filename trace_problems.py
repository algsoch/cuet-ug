import pandas as pd

def trace_problematic_colleges():
    """Find what's causing the problematic college assignments"""
    
    # Load raw data
    raw_df = pd.read_csv("data/raw_extraction_20250825_232420.csv")
    
    # The raw file has numeric column names, so let's use proper column names
    if '1' in raw_df.columns:
        raw_df.columns = ['S.NO.', 'NAME OF THE COLLEGE', 'NAME OF THE PROGRAM', 'UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
    
    # Load proper cleaned data  
    clean_df = pd.read_csv("outputs/DU_Admission_PROPER_Clean_20250826_024928.csv")
    
    problematic_colleges = [
        "College",
        "For Women (W)", 
        "Sciences for Women (W)",
        "Studies"
    ]
    
    print("🔍 TRACING PROBLEMATIC COLLEGE ASSIGNMENTS")
    print("=" * 60)
    
    for problem_college in problematic_colleges:
        print(f"\n🎯 Analyzing: '{problem_college}'")
        
        # Find all rows with this college in cleaned data
        problem_rows = clean_df[clean_df['NAME OF THE COLLEGE'] == problem_college]
        
        if len(problem_rows) > 0:
            print(f"   Found {len(problem_rows)} rows with this college name")
            
            # Show a few sample programs
            sample_programs = problem_rows['NAME OF THE PROGRAM'].head(3).tolist()
            for i, program in enumerate(sample_programs, 1):
                print(f"      {i}. Program: {program[:80]}...")
            
            # Find these programs in raw data to see what the original college name was
            first_program = problem_rows.iloc[0]['NAME OF THE PROGRAM']
            
            # Search in raw data
            raw_matches = raw_df[raw_df['NAME OF THE PROGRAM'].str.contains(first_program[:30], na=False)]
            
            if len(raw_matches) > 0:
                print(f"   📄 Raw data context:")
                for idx, row in raw_matches.head(3).iterrows():
                    s_no = row.get('S.NO.', 'N/A')
                    raw_college = row.get('NAME OF THE COLLEGE', 'N/A')
                    print(f"      Row {idx}: S.NO.={s_no}, College='{raw_college}'")
                
                # Look at surrounding rows too
                if len(raw_matches) > 0:
                    first_idx = raw_matches.index[0]
                    context_start = max(0, first_idx - 5)
                    context_end = min(len(raw_df), first_idx + 5)
                    context_rows = raw_df.iloc[context_start:context_end]
                    
                    print(f"   🔍 Context (rows {context_start}-{context_end}):")
                    for idx, row in context_rows.iterrows():
                        s_no = str(row.get('S.NO.', 'N/A'))
                        college = str(row.get('NAME OF THE COLLEGE', 'N/A'))[:50]
                        program = str(row.get('NAME OF THE PROGRAM', 'N/A'))[:40]
                        marker = " ⭐" if idx in raw_matches.index else ""
                        print(f"      {idx:4d}: S.NO.={s_no:>3} | College='{college}' | Program='{program}'{marker}")

if __name__ == "__main__":
    trace_problematic_colleges()
