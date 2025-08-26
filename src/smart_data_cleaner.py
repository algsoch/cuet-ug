"""
Smart Data Cleaner for DU Admission Analyzer
Handles split college names and preserves maximum data
"""

import pandas as pd
import numpy as np
import re
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartDataCleaner:
    """
    Enhanced data cleaning class that preserves maximum data by 
    intelligently handling split college names and other patterns
    """
    
    def __init__(self):
        self.expected_columns = [
            'S.NO.', 'NAME OF THE COLLEGE', 'NAME OF THE PROGRAM', 
            'UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD'
        ]
        self.numeric_columns = ['UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
        self.header_patterns = [
            'S.NO', 'NAME OF THE COLLEGE', 'NAME OF THE PROGRAM',
            'UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD'
        ]
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main cleaning pipeline that preserves maximum data
        """
        logger.info("🧹 Starting SMART data cleaning pipeline...")
        logger.info(f"Input shape: {df.shape}")
        
        # Step 1: Initial setup
        df = self._initial_setup(df)
        logger.info(f"After initial setup: {df.shape}")
        
        # Step 2: Remove only clear header rows
        df = self._remove_header_rows(df)
        logger.info(f"After removing headers: {df.shape}")
        
        # Step 3: SMART merge split college names
        df = self._smart_merge_split_colleges(df)
        logger.info(f"After merging split colleges: {df.shape}")
        
        # Step 4: Fix remaining column alignments
        df = self._fix_column_alignments(df)
        logger.info(f"After fixing alignments: {df.shape}")
        
        # Step 5: Convert and clean data
        df = self._convert_and_clean(df)
        logger.info(f"After conversion: {df.shape}")
        
        # Step 6: Final validation (conservative)
        df = self._conservative_validation(df)
        logger.info(f"✅ SMART cleaning complete: {df.shape}")
        
        return df
    
    def _initial_setup(self, df: pd.DataFrame) -> pd.DataFrame:
        """Set up proper column structure"""
        # Remove completely empty rows
        df = df.dropna(how='all')
        df = df[~(df.astype(str) == '').all(axis=1)]
        df = df.reset_index(drop=True)
        
        # Set proper columns
        if df.shape[1] >= len(self.expected_columns):
            df = df.iloc[:, :len(self.expected_columns)]
        df.columns = self.expected_columns
        
        return df
    
    def _remove_header_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove only clear header repetitions"""
        def is_clear_header(row):
            row_str = ' '.join(str(val).upper() for val in row if pd.notna(val))
            # Only remove if it contains multiple clear header patterns
            header_matches = sum(1 for pattern in self.header_patterns 
                               if pattern.upper() in row_str)
            return header_matches >= 4  # More conservative threshold
        
        initial_count = len(df)
        df = df[~df.apply(is_clear_header, axis=1)]
        df = df.reset_index(drop=True)
        
        removed = initial_count - len(df)
        logger.info(f"Removed {removed} clear header rows")
        return df
    
    def _smart_merge_split_colleges(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Intelligently merge split college names using the exact pattern found
        """
        logger.info("🎯 Smart merging split college names...")
        
        merged_rows = []
        i = 0
        merges_made = 0
        
        while i < len(df):
            current_row = df.iloc[i]
            
            # Check if this is a split college pattern
            if i < len(df) - 1 and self._is_split_college_pattern(current_row, df.iloc[i + 1]):
                # Merge the split college
                next_row = df.iloc[i + 1]
                merged_row = self._merge_split_college_rows(current_row, next_row)
                merged_rows.append(merged_row)
                merges_made += 1
                i += 2  # Skip both rows as we merged them
                
                if merges_made <= 5:  # Log first few merges
                    college_name = merged_row['NAME OF THE COLLEGE']
                    program_name = merged_row['NAME OF THE PROGRAM']
                    logger.info(f"Merged #{merges_made}: '{college_name}' - '{program_name}'")
            else:
                merged_rows.append(current_row)
                i += 1
        
        df_merged = pd.DataFrame(merged_rows)
        df_merged = df_merged.reset_index(drop=True)
        
        logger.info(f"✨ Made {merges_made} smart college merges")
        return df_merged
    
    def _is_split_college_pattern(self, current_row: pd.Series, next_row: pd.Series) -> bool:
        """
        Check if this is the exact split college pattern we identified:
        - Current row: no S.NO., has college name part, no program, all zeros
        - Next row: has S.NO., "College" as college name, has program, has data
        """
        # Current row checks
        current_sno = str(current_row['S.NO.']).strip()
        current_college = str(current_row['NAME OF THE COLLEGE']).strip()
        current_program = str(current_row['NAME OF THE PROGRAM']).strip()
        
        # Next row checks
        next_sno = str(next_row['S.NO.']).strip()
        next_college = str(next_row['NAME OF THE COLLEGE']).strip()
        next_program = str(next_row['NAME OF THE PROGRAM']).strip()
        
        # Pattern conditions
        current_has_no_sno = current_sno in ['nan', '', 'None']
        current_has_college_name = (current_college not in ['nan', '', 'None', 'College'] and 
                                   len(current_college) > 5)  # Real college name
        current_has_no_program = current_program in ['nan', '', 'None']
        
        next_has_sno = next_sno.isdigit()
        next_college_is_college = next_college == 'College'
        next_has_program = (next_program not in ['nan', '', 'None'] and 
                           ('B.' in next_program or 'M.' in next_program))
        
        # Check if current row has all zeros in numeric columns
        current_all_zeros = True
        try:
            for col in self.numeric_columns:
                if col in current_row.index:
                    val = str(current_row[col]).strip()
                    if val not in ['nan', '', '0', 'None']:
                        current_all_zeros = False
                        break
        except:
            pass
        
        return (current_has_no_sno and current_has_college_name and current_has_no_program and
                current_all_zeros and next_has_sno and next_college_is_college and next_has_program)
    
    def _merge_split_college_rows(self, college_row: pd.Series, data_row: pd.Series) -> pd.Series:
        """
        Merge split college rows by combining college name and using data from the data row
        """
        merged = data_row.copy()
        
        # Combine college names
        college_part1 = str(college_row['NAME OF THE COLLEGE']).strip()
        college_part2 = str(data_row['NAME OF THE COLLEGE']).strip()
        
        # Create full college name
        if college_part2 == 'College':
            full_college_name = f"{college_part1} {college_part2}"
        else:
            full_college_name = f"{college_part1} {college_part2}".strip()
        
        merged['NAME OF THE COLLEGE'] = full_college_name
        
        # Keep the S.NO., program, and numeric data from the data row
        # (they're already in the data_row which we copied)
        
        return merged
    
    def _fix_column_alignments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fix any remaining column alignment issues
        """
        logger.info("🔧 Fixing column alignments...")
        
        for i in range(len(df)):
            row = df.iloc[i]
            
            # Ensure S.NO. is numeric or make it sequential
            sno = str(row['S.NO.']).strip()
            if not sno.isdigit():
                df.at[i, 'S.NO.'] = str(i + 1)
            
            # Ensure college name is not empty
            college = str(row['NAME OF THE COLLEGE']).strip()
            if college in ['nan', '', 'None']:
                # Try to get from program or use placeholder
                program = str(row['NAME OF THE PROGRAM']).strip()
                if program not in ['nan', '', 'None']:
                    df.at[i, 'NAME OF THE COLLEGE'] = 'Unknown College'
                else:
                    # This row might be invalid, but we'll keep it for now
                    df.at[i, 'NAME OF THE COLLEGE'] = f'College_{i+1}'
        
        return df
    
    def _convert_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert numeric columns and clean text
        """
        logger.info("🔢 Converting and cleaning data...")
        
        # Convert numeric columns
        for col in self.numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._safe_int_convert)
        
        # Clean text columns
        text_columns = ['NAME OF THE COLLEGE', 'NAME OF THE PROGRAM']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._clean_text)
        
        return df
    
    def _safe_int_convert(self, value) -> int:
        """Safely convert value to integer"""
        try:
            if pd.isna(value):
                return 0
            str_val = str(value).strip()
            if str_val in ['', 'nan', 'None']:
                return 0
            # Extract first number
            numbers = re.findall(r'\d+', str_val)
            return int(numbers[0]) if numbers else 0
        except:
            return 0
    
    def _clean_text(self, value) -> str:
        """Clean text values"""
        if pd.isna(value):
            return ''
        text = str(value).strip()
        if text in ['nan', 'None']:
            return ''
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _conservative_validation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Conservative validation that only removes clearly invalid rows
        """
        logger.info("✅ Conservative validation...")
        
        initial_count = len(df)
        
        # Only remove rows where BOTH college AND program are empty
        valid_mask = (
            (df['NAME OF THE COLLEGE'].str.strip() != '') &
            (df['NAME OF THE COLLEGE'] != 'nan') &
            (df['NAME OF THE PROGRAM'].str.strip() != '') &
            (df['NAME OF THE PROGRAM'] != 'nan')
        )
        
        df = df[valid_mask]
        df = df.reset_index(drop=True)
        
        # Renumber S.NO. sequentially
        df['S.NO.'] = range(1, len(df) + 1)
        
        final_count = len(df)
        removed = initial_count - final_count
        logger.info(f"Conservative validation: removed only {removed} clearly invalid rows")
        
        return df


def smart_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function for smart data cleaning
    """
    cleaner = SmartDataCleaner()
    return cleaner.clean_data(df)
