"""
Improved Data Cleaning Module for DU Admission Analyzer
Fixed to preserve more data and reduce aggressive row merging
"""

import pandas as pd
import numpy as np
import re
import logging
from typing import List, Dict, Any, Optional
from .config import EXPECTED_COLUMNS, NUMERIC_COLUMNS, HEADER_PATTERNS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedDataCleaner:
    """
    Improved data cleaning class that preserves more data
    """
    
    def __init__(self):
        self.expected_columns = EXPECTED_COLUMNS
        self.numeric_columns = NUMERIC_COLUMNS
        self.header_patterns = HEADER_PATTERNS
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Improved cleaning pipeline that preserves more data
        """
        logger.info("Starting improved data cleaning pipeline...")
        logger.info(f"Input shape: {df.shape}")
        
        # Step 1: Initial cleanup
        df = self._initial_cleanup(df)
        
        # Step 2: Identify and set proper columns
        df = self._identify_columns(df)
        
        # Step 3: Remove header rows that appear multiple times
        df = self._remove_duplicate_headers(df)
        
        # Step 4: IMPROVED - More conservative column misalignment fixing
        df = self._fix_column_misalignment_conservative(df)
        
        # Step 5: IMPROVED - More conservative corrupted program name fixing
        df = self._fix_corrupted_program_names_conservative(df)
        
        # Step 6: IMPROVED - Much more conservative row merging
        df = self._merge_split_rows_conservative(df)
        
        # Step 7: Convert numeric columns
        df = self._convert_numeric_columns(df)
        
        # Step 8: Clean text columns
        df = self._clean_text_columns(df)
        
        # Step 9: IMPROVED - Less aggressive final validation
        df = self._final_validation_conservative(df)
        
        logger.info(f"✅ Improved data cleaning complete. Output shape: {df.shape}")
        return df
    
    def _initial_cleanup(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove completely empty rows and basic cleanup"""
        logger.info("Step 1: Initial cleanup")
        
        # Remove rows that are completely empty
        df = df.dropna(how='all')
        
        # Remove rows where all values are empty strings
        df = df[~(df.astype(str) == '').all(axis=1)]
        
        # Reset index
        df = df.reset_index(drop=True)
        
        logger.info(f"After initial cleanup: {df.shape}")
        return df
    
    def _identify_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify the correct column structure"""
        logger.info("Step 2: Identifying columns")
        
        # If we have the expected number of columns already
        if df.shape[1] == len(self.expected_columns):
            df.columns = self.expected_columns
            logger.info("✅ Columns already match expected structure")
            return df
        
        # Try to find header row and use it to determine column structure
        header_row_idx = self._find_header_row(df)
        
        if header_row_idx is not None:
            # Use the header row to determine columns
            headers = df.iloc[header_row_idx].tolist()
            df = df.iloc[header_row_idx + 1:].reset_index(drop=True)
            
            # Map to expected columns if needed
            df.columns = self._map_to_expected_columns(headers)
        else:
            # Fallback: assume the correct number of columns
            if df.shape[1] >= len(self.expected_columns):
                df = df.iloc[:, :len(self.expected_columns)]
                df.columns = self.expected_columns
            else:
                # Pad with empty columns if needed
                for i in range(df.shape[1], len(self.expected_columns)):
                    df[f'col_{i}'] = ''
                df.columns = self.expected_columns
        
        logger.info(f"Columns set to: {list(df.columns)}")
        return df
    
    def _find_header_row(self, df: pd.DataFrame) -> Optional[int]:
        """Find the row containing column headers"""
        for i in range(len(df)):
            row = df.iloc[i]
            row_str = ' '.join(str(val).upper() for val in row if pd.notna(val))
            
            # Check if this row contains key header patterns
            header_matches = sum(1 for pattern in self.header_patterns 
                               if pattern.upper() in row_str)
            
            if header_matches >= 3:  # At least 3 header patterns found
                return i
        
        return None
    
    def _map_to_expected_columns(self, headers: List[str]) -> List[str]:
        """Map extracted headers to expected column names"""
        mapped_columns = []
        
        for i, header in enumerate(headers):
            if i < len(self.expected_columns):
                mapped_columns.append(self.expected_columns[i])
            else:
                mapped_columns.append(f'extra_col_{i}')
        
        return mapped_columns
    
    def _remove_duplicate_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows that are duplicate headers appearing throughout the PDF"""
        logger.info("Step 3: Removing duplicate headers")
        
        initial_rows = len(df)
        
        # Create patterns to identify header rows
        def is_header_row(row):
            row_str = ' '.join(str(val).upper() for val in row if pd.notna(val) and str(val) != '')
            
            # Check for header patterns
            header_matches = sum(1 for pattern in self.header_patterns 
                               if pattern.upper() in row_str)
            
            return header_matches >= 2
        
        # Remove header rows
        df = df[~df.apply(is_header_row, axis=1)]
        df = df.reset_index(drop=True)
        
        removed_rows = initial_rows - len(df)
        logger.info(f"Removed {removed_rows} duplicate header rows")
        
        return df
    
    def _fix_column_misalignment_conservative(self, df: pd.DataFrame) -> pd.DataFrame:
        """IMPROVED: More conservative column misalignment fixing"""
        logger.info("Step 4: Conservative column misalignment fixing")
        
        fixed_rows = []
        i = 0
        merges_made = 0
        
        while i < len(df):
            current_row = df.iloc[i].copy()
            
            # MUCH more strict criteria for identifying misaligned rows
            if (i < len(df) - 1 and 
                self._is_definite_college_only_row(current_row) and
                self._is_definite_evening_continuation_row(df.iloc[i + 1])):
                
                # Merge the college name with Evening and realign columns
                next_row = df.iloc[i + 1].copy()
                merged_row = self._merge_evening_college_row(current_row, next_row)
                fixed_rows.append(merged_row)
                merges_made += 1
                i += 2  # Skip both rows as we've merged them
                
            else:
                fixed_rows.append(current_row)
                i += 1
        
        # Convert back to DataFrame
        df_fixed = pd.DataFrame(fixed_rows)
        df_fixed = df_fixed.reset_index(drop=True)
        
        logger.info(f"Conservative misalignment fixes: {merges_made} merges, {len(df)} -> {len(df_fixed)} rows")
        return df_fixed
    
    def _is_definite_college_only_row(self, row: pd.Series) -> bool:
        """STRICTER check if row contains only college name"""
        # Must have college name in column 1
        has_college = (len(row) > 1 and 
                      pd.notna(row.iloc[1]) and 
                      str(row.iloc[1]).strip() != '' and
                      len(str(row.iloc[1]).strip()) > 10)  # College names are usually long
        
        # S.NO. must be completely empty
        sno_empty = (pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '')
        
        # Program name must be empty
        program_empty = (len(row) <= 2 or pd.isna(row.iloc[2]) or str(row.iloc[2]).strip() == '')
        
        # ALL numeric columns must be empty
        numeric_empty = all(pd.isna(row.iloc[i]) or str(row.iloc[i]).strip() == '' 
                           for i in range(3, min(len(row), 10)))
        
        return has_college and sno_empty and program_empty and numeric_empty
    
    def _is_definite_evening_continuation_row(self, row: pd.Series) -> bool:
        """STRICTER check if row is an Evening college continuation"""
        # Must have S.NO. in column 0
        has_sno = (pd.notna(row.iloc[0]) and 
                  str(row.iloc[0]).strip().isdigit())
        
        # Must have EXACTLY "(Evening)" in column 1 (not just containing it)
        has_evening = (len(row) > 1 and 
                      pd.notna(row.iloc[1]) and 
                      str(row.iloc[1]).strip() == '(Evening)')
        
        # Must have a program name in column 2
        has_program = (len(row) > 2 and 
                      pd.notna(row.iloc[2]) and 
                      str(row.iloc[2]).strip() != '')
        
        return has_sno and has_evening and has_program
    
    def _merge_evening_college_row(self, college_row: pd.Series, evening_row: pd.Series) -> pd.Series:
        """Merge college-only row with Evening continuation row"""
        merged = evening_row.copy()
        
        # Combine college name with (Evening)
        college_name = str(college_row.iloc[1]).strip()
        evening_part = str(evening_row.iloc[1]).strip()
        merged.iloc[1] = f"{college_name} {evening_part}"
        
        return merged
    
    def _fix_corrupted_program_names_conservative(self, df: pd.DataFrame) -> pd.DataFrame:
        """IMPROVED: More conservative corrupted program name fixing"""
        logger.info("Step 5: Conservative corrupted program name fixing")
        
        original_count = len(df)
        df = df.copy()
        rows_to_remove = []
        fixes_made = 0
        
        i = 0
        while i < len(df):
            current_row = df.iloc[i]
            
            # Much stricter criteria for corruption detection
            if self._has_definite_corrupted_program_name(current_row):
                # Look back ONLY 1 row for incomplete program
                incomplete_idx = self._find_definite_incomplete_program_above(df, i)
                if incomplete_idx is not None and incomplete_idx not in rows_to_remove:
                    # Get the incomplete program from the found row
                    incomplete_row = df.iloc[incomplete_idx]
                    incomplete_program = str(incomplete_row.iloc[2]).strip()
                    corrupted_program = str(current_row.iloc[2]).strip()
                    
                    # Combine the programs
                    combined_program = f"{incomplete_program} {corrupted_program}"
                    
                    # Update the current row with the complete program
                    program_col = df.columns[2]
                    df.at[i, program_col] = combined_program
                    
                    # Mark the incomplete row for removal
                    rows_to_remove.append(incomplete_idx)
                    fixes_made += 1
                    
                    logger.info(f"Fixed definite corruption: '{incomplete_program}' + '{corrupted_program}'")
                    
            i += 1
        
        # Remove the incomplete rows that were merged
        if rows_to_remove:
            rows_to_remove.sort(reverse=True)
            for idx in rows_to_remove:
                df = df.drop(df.index[idx]).reset_index(drop=True)
        
        logger.info(f"Conservative corruption fixes: {fixes_made} fixes, {original_count} -> {len(df)} rows")
        return df
    
    def _has_definite_corrupted_program_name(self, row: pd.Series) -> bool:
        """STRICTER check for corrupted program names"""
        if len(row) < 3:
            return False
            
        program = str(row.iloc[2]).strip()
        
        # Only the most obvious corruption patterns
        definite_corruption_patterns = [
            'Science/Economics/Mathematics/Philosophy))',  # Exact match
            'Science/Economics/Mathematics/Sanskrit))',    # Exact match
            'History/Political Science)',                  # Exact match
        ]
        
        return any(pattern == program for pattern in definite_corruption_patterns)
    
    def _find_definite_incomplete_program_above(self, df: pd.DataFrame, current_idx: int) -> Optional[int]:
        """STRICTER search for incomplete program above"""
        # Look back ONLY 1 row
        if current_idx > 0:
            i = current_idx - 1
            row = df.iloc[i]
            program = str(row.iloc[2]).strip()
            college = str(row.iloc[1]).strip() if len(row) > 1 else ""
            
            # Very specific patterns for incomplete programs
            definite_incomplete_patterns = [
                '(English/Hindi/History/Pol.',  # Must end exactly like this
                'Any One Out Of These (English/Hindi/History/Pol.',
            ]
            
            # College must be empty AND program must end with specific pattern
            if college in ['', 'nan', 'None']:
                if any(program.endswith(pattern) for pattern in definite_incomplete_patterns):
                    return i
        
        return None
    
    def _merge_split_rows_conservative(self, df: pd.DataFrame) -> pd.DataFrame:
        """IMPROVED: Much more conservative row merging"""
        logger.info("Step 6: Conservative split row merging")
        
        merged_rows = []
        i = 0
        merges_made = 0
        
        while i < len(df):
            current_row = df.iloc[i].copy()
            
            # MUCH more strict criteria for identifying continuation rows
            if (i > 0 and 
                self._is_definite_continuation_row(current_row, merged_rows[-1] if merged_rows else None)):
                
                # Merge with previous row
                prev_row = merged_rows[-1]
                merged_row = self._merge_two_rows_conservative(prev_row, current_row)
                merged_rows[-1] = merged_row
                merges_made += 1
                
            else:
                merged_rows.append(current_row)
            
            i += 1
        
        # Convert back to DataFrame
        df_merged = pd.DataFrame(merged_rows)
        df_merged = df_merged.reset_index(drop=True)
        
        logger.info(f"Conservative merging: {merges_made} merges, {len(df)} -> {len(df_merged)} rows")
        return df_merged
    
    def _is_definite_continuation_row(self, row: pd.Series, prev_row: Optional[pd.Series]) -> bool:
        """MUCH STRICTER check for continuation rows"""
        # Must have empty S.NO.
        sno_empty = pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == ''
        if not sno_empty:
            return False
        
        # ALL numeric columns must be empty
        numeric_cols_empty = True
        for i in range(3, min(10, len(row))):
            val = str(row.iloc[i]).strip()
            if val != '' and val != 'nan':
                numeric_cols_empty = False
                break
        
        if not numeric_cols_empty:
            return False
        
        # Must have some text in college OR program column (but not both)
        college_name = str(row.iloc[1]).strip() if len(row) > 1 else ''
        program_name = str(row.iloc[2]).strip() if len(row) > 2 else ''
        
        has_college_text = college_name not in ['', 'nan', 'None']
        has_program_text = program_name not in ['', 'nan', 'None']
        
        # Should have text in exactly one column, not both
        has_continuation_text = (has_college_text and not has_program_text) or (not has_college_text and has_program_text)
        
        if not has_continuation_text:
            return False
        
        # Additional check: if previous row exists, ensure it looks incomplete
        if prev_row is not None:
            prev_college = str(prev_row.iloc[1]).strip() if len(prev_row) > 1 else ''
            prev_program = str(prev_row.iloc[2]).strip() if len(prev_row) > 2 else ''
            
            # Previous row should have valid S.NO. and some data
            prev_sno = str(prev_row.iloc[0]).strip()
            if not prev_sno.isdigit():
                return False
            
            # Check for obvious continuation patterns
            obvious_continuation_patterns = [
                r'.*\($',  # Ends with opening parenthesis
                r'.*\+$',  # Ends with plus sign
                r'.*and$', # Ends with 'and'
                r'.*of$',  # Ends with 'of'
            ]
            
            import re
            if has_college_text:
                # College continuation - previous college should look incomplete
                for pattern in obvious_continuation_patterns:
                    if re.search(pattern, prev_college, re.IGNORECASE):
                        return True
                return False
            
            if has_program_text:
                # Program continuation - previous program should look incomplete
                for pattern in obvious_continuation_patterns:
                    if re.search(pattern, prev_program, re.IGNORECASE):
                        return True
                return False
        
        return False
    
    def _merge_two_rows_conservative(self, row1: pd.Series, row2: pd.Series) -> pd.Series:
        """Conservative merging of two rows"""
        merged = row1.copy()
        
        for i, col in enumerate(merged.index):
            val1 = str(row1.iloc[i] if i < len(row1) else '').strip()
            val2 = str(row2.iloc[i] if i < len(row2) else '').strip()
            
            # Handle empty values
            if val1 in ['', 'nan', 'None']:
                merged.iloc[i] = val2
            elif val2 not in ['', 'nan', 'None']:
                # For college and program names, be more careful with spacing
                if i in [1, 2]:  # College name or program name columns
                    merged.iloc[i] = f"{val1} {val2}".strip()
                else:
                    merged.iloc[i] = val1  # Keep original value for other columns
        
        return merged
    
    def _convert_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert numeric columns from string to integer"""
        logger.info("Step 7: Converting numeric columns")
        
        for col in self.numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._safe_int_convert)
        
        return df
    
    def _safe_int_convert(self, value) -> int:
        """Safely convert a value to integer"""
        try:
            if pd.isna(value):
                return 0
            
            str_val = str(value).strip()
            
            if str_val == '' or str_val == 'nan':
                return 0
            
            # Extract first number if multiple numbers exist
            numbers = re.findall(r'\d+', str_val)
            if numbers:
                return int(numbers[0])
            
            return 0
            
        except:
            return 0
    
    def _clean_text_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize text columns"""
        logger.info("Step 8: Cleaning text columns")
        
        text_columns = ['NAME OF THE COLLEGE', 'NAME OF THE PROGRAM']
        
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._clean_text_value)
        
        return df
    
    def _clean_text_value(self, value) -> str:
        """Clean individual text values"""
        if pd.isna(value):
            return ''
        
        text = str(value).strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text  # Don't apply title case automatically
    
    def _final_validation_conservative(self, df: pd.DataFrame) -> pd.DataFrame:
        """IMPROVED: Less aggressive final validation"""
        logger.info("Step 9: Conservative final validation")
        initial_count = len(df)
        
        # Only remove rows with completely empty college names
        before_filter = len(df)
        df = df[df['NAME OF THE COLLEGE'].str.strip() != '']
        after_filter = len(df)
        
        if before_filter != after_filter:
            logger.info(f"Removed {before_filter - after_filter} rows with empty college names")
        
        # Keep rows even if they have zero seats - they might be valid placeholders
        zero_seat_rows = df[df[self.numeric_columns].sum(axis=1) == 0]
        logger.info(f"Keeping {len(zero_seat_rows)} rows with zero seats")
        
        # Reset index and add row numbers
        df = df.reset_index(drop=True)
        if 'S.NO.' in df.columns:
            df['S.NO.'] = range(1, len(df) + 1)
        
        final_count = len(df)
        logger.info(f"Conservative validation: {initial_count} -> {final_count} rows (lost {initial_count - final_count})")
        
        return df


def clean_data_improved(df: pd.DataFrame) -> pd.DataFrame:
    """
    Improved data cleaning function that preserves more data
    """
    cleaner = ImprovedDataCleaner()
    return cleaner.clean_data(df)
