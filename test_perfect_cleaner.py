import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.perfect_data_cleaner import PerfectDataCleaner
import pandas as pd
from datetime import datetime

def test_perfect_cleaner():
    """Test the perfect data cleaner"""
    
    print("🎯 Testing Perfect Data Cleaner...")
    
    # Load raw data first to check
    raw_file = "data/raw_extraction_20250825_232420.csv"
    raw_df = pd.read_csv(raw_file)
    print(f"📊 Raw data: {len(raw_df)} rows")
    
    # Run perfect cleaning
    print(f"\n🎯 Running perfect cleaning...")
    cleaner = PerfectDataCleaner()
    clean_df = cleaner.clean(raw_file)
    
    # Generate timestamp for output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"outputs/DU_Admission_PERFECT_Clean_{timestamp}.csv"
    
    # Save results
    clean_df.to_csv(output_file, index=False)
    
    # Analysis
    print(f"\n📈 PERFECT CLEANING RESULTS:")
    print(f"   Raw rows: {len(raw_df)}")
    print(f"   Clean rows: {len(clean_df)}")
    print(f"   Target: 1528 rows")
    
    if len(clean_df) == 1528:
        print(f"   Achievement: 🎉 PERFECT ROW COUNT!")
    else:
        print(f"   Achievement: {len(clean_df)/1528*100:.1f}% of target")
    
    # Check unique colleges
    unique_colleges = clean_df['NAME OF THE COLLEGE'].nunique()
    print(f"\n🎯 College Analysis:")
    print(f"   Unique colleges: {unique_colleges} (target: ~93)")
    
    if unique_colleges >= 90:
        print(f"   🎉 EXCELLENT college count!")
    elif unique_colleges >= 80:
        print(f"   ✅ Very good college count!")
    elif unique_colleges >= 70:
        print(f"   ✅ Good college count!")
    else:
        print(f"   ⚠️  Below target college count")
    
    # Check for problematic patterns
    college_counts = clean_df['NAME OF THE COLLEGE'].value_counts()
    
    problematic = []
    for college in college_counts.index:
        college_str = str(college).strip()
        if (len(college_str) <= 3 or 
            college_str in ['College', 'Sciences', 'Commerce', 'Studies', 'For Women (W)', 'Sciences for Women (W)', '(W)', '(Evening)'] or
            college_str.startswith('(') or
            college_str == 'nan'):
            problematic.append((college, college_counts[college]))
    
    if problematic:
        print(f"\n⚠️  Found {len(problematic)} problematic college names:")
        for college, count in problematic[:5]:
            print(f"      '{college}' ({count} programs)")
    else:
        print(f"\n✅ No problematic college names found!")
    
    # Check for double suffixes
    double_suffix_colleges = []
    for college in college_counts.index:
        college_str = str(college)
        if '(W) (W)' in college_str or '(Evening) (Evening)' in college_str:
            double_suffix_colleges.append((college, college_counts[college]))
    
    if double_suffix_colleges:
        print(f"\n⚠️  Found {len(double_suffix_colleges)} double suffix issues:")
        for college, count in double_suffix_colleges:
            print(f"      '{college}' ({count} programs)")
    else:
        print(f"\n✅ No double suffix issues found!")
    
    # Sample college names
    print(f"\n📋 Top 15 colleges by program count:")
    for i, (college, count) in enumerate(college_counts.head(15).items(), 1):
        print(f"   {i:2d}. {college} ({count} programs)")
    
    print(f"\n💾 Perfect cleaned data saved to: {output_file}")
    print(f"\n🎉 Perfect cleaning test complete!")
    
    return clean_df, college_counts

if __name__ == "__main__":
    df, counts = test_perfect_cleaner()
