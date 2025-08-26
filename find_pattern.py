import pandas as pd

def find_college_pattern():
    """Look at specific program examples to understand the college name patterns"""
    
    # Load raw data
    raw_df = pd.read_csv("data/raw_extraction_20250825_232420.csv")
    
    # Fix column names
    if '1' in raw_df.columns:
        raw_df.columns = ['S.NO.', 'NAME OF THE COLLEGE', 'NAME OF THE PROGRAM', 'UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
    
    # Load proper cleaned data  
    clean_df = pd.read_csv("outputs/DU_Admission_PROPER_Clean_20250826_024928.csv")
    
    print("🔍 FINDING COLLEGE NAME PATTERNS")
    print("=" * 50)
    
    # Look for specific program that appears in 'College' group
    program_to_find = "B.A. (Hons.) English"
    
    print(f"\n🎯 Searching for program: '{program_to_find}'")
    
    # Find in cleaned data
    clean_matches = clean_df[clean_df['NAME OF THE PROGRAM'] == program_to_find]
    
    if len(clean_matches) > 0:
        print(f"\n📊 CLEANED DATA ({len(clean_matches)} matches):")
        for i, (idx, row) in enumerate(clean_matches.iterrows()):
            college = row['NAME OF THE COLLEGE']
            print(f"   {i+1}. College: '{college}'")
    
    # Find in raw data
    raw_matches = raw_df[raw_df['NAME OF THE PROGRAM'] == program_to_find]
    
    if len(raw_matches) > 0:
        print(f"\n📄 RAW DATA ({len(raw_matches)} matches):")
        for i, (idx, row) in enumerate(raw_matches.iterrows()):
            s_no = row['S.NO.']
            college = row['NAME OF THE COLLEGE']
            print(f"   {i+1}. Row {idx}: S.NO.={s_no}, College: '{college}'")
        
        # Look at context around these matches
        print(f"\n🔍 CONTEXT AROUND MATCHES:")
        for idx in raw_matches.index[:3]:  # First 3 matches
            context_start = max(0, idx - 3)
            context_end = min(len(raw_df), idx + 4)
            
            print(f"\n   Context for row {idx} (showing rows {context_start}-{context_end-1}):")
            for ctx_idx in range(context_start, context_end):
                if ctx_idx < len(raw_df):
                    ctx_row = raw_df.iloc[ctx_idx]
                    s_no = str(ctx_row['S.NO.'])
                    college = str(ctx_row['NAME OF THE COLLEGE'])[:60]
                    program = str(ctx_row['NAME OF THE PROGRAM'])[:40]
                    marker = " ⭐" if ctx_idx == idx else ""
                    print(f"      {ctx_idx:4d}: S.NO.={s_no:>3} | College='{college}' | Program='{program}'{marker}")

if __name__ == "__main__":
    find_college_pattern()
