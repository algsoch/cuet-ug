import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

def analyze_unique_colleges():
    """Check unique colleges in proper cleaned data"""
    
    # Load the latest proper cleaned data
    file_path = "outputs/DU_Admission_PROPER_Clean_20250826_024928.csv"
    
    try:
        df = pd.read_csv(file_path)
        print(f"📊 Loaded {len(df)} rows from proper cleaned data")
        
        # Get unique colleges
        unique_colleges = df['NAME OF THE COLLEGE'].unique()
        num_unique = len(unique_colleges)
        
        print(f"\n🎯 UNIQUE COLLEGES ANALYSIS:")
        print(f"   Total unique colleges: {num_unique}")
        print(f"   Target: ~93 colleges")
        print(f"   Progress: {num_unique/93*100:.1f}% of target")
        
        # Sort colleges by program count
        college_counts = df['NAME OF THE COLLEGE'].value_counts()
        
        print(f"\n📋 ALL {num_unique} UNIQUE COLLEGES:")
        for i, (college, count) in enumerate(college_counts.items(), 1):
            print(f"   {i:2d}. {college} ({count} programs)")
        
        # Check for suspicious patterns
        print(f"\n🔍 CHECKING FOR REMAINING ISSUES:")
        
        suspicious_colleges = []
        for college in unique_colleges:
            college_str = str(college).strip()
            # Check for very short names or suspicious patterns
            if (len(college_str) <= 3 or 
                college_str in ['nan', '', 'None'] or
                college_str.startswith('(') or
                college_str in ['College', 'Sciences', 'Commerce']):
                suspicious_colleges.append(college)
        
        if suspicious_colleges:
            print(f"   Found {len(suspicious_colleges)} suspicious college names:")
            for college in suspicious_colleges:
                count = college_counts.get(college, 0)
                print(f"      '{college}' ({count} programs)")
        else:
            print("   ✅ No suspicious college names found!")
        
        # Check for potential duplicates or similar names
        print(f"\n🔍 CHECKING FOR POTENTIAL DUPLICATES:")
        college_names = [str(c).lower().strip() for c in unique_colleges]
        potential_dups = []
        
        for i, name1 in enumerate(college_names):
            for j, name2 in enumerate(college_names[i+1:], i+1):
                # Check if one is contained in the other (but not exact match)
                if (name1 in name2 or name2 in name1) and name1 != name2:
                    potential_dups.append((unique_colleges[i], unique_colleges[j]))
        
        if potential_dups:
            print(f"   Found {len(potential_dups)} potential duplicates:")
            for dup1, dup2 in potential_dups[:10]:  # Show first 10
                count1 = college_counts.get(dup1, 0)
                count2 = college_counts.get(dup2, 0)
                print(f"      '{dup1}' ({count1}) vs '{dup2}' ({count2})")
        else:
            print("   ✅ No obvious duplicates found!")
            
        return df, college_counts
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

if __name__ == "__main__":
    print("🎯 Analyzing unique colleges in proper cleaned data...")
    df, counts = analyze_unique_colleges()
    print("\n🎉 Analysis complete!")
