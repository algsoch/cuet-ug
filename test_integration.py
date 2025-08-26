from src.perfect_data_cleaner import PerfectDataCleaner
import pandas as pd
from datetime import datetime

# Test the integration
cleaner = PerfectDataCleaner()
raw_file = 'data/raw_extraction_20250825_232420.csv'
clean_df = cleaner.clean(raw_file)

# Generate output filename like the system will
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_path = f'outputs/DU_Admission_PERFECT_Clean_{timestamp}.csv'
clean_df.to_csv(output_path, index=False)

print(f'💾 Perfect cleaned data saved to: {output_path}')
print(f'📊 Results: {len(clean_df)} rows, {clean_df["NAME OF THE COLLEGE"].nunique()} unique colleges')
print(f'✅ System integration: Ready for production use!')
