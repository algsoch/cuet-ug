"""
Data Cleaning Module for DU Admission Analyzer
Handles cleaning and normalization of extracted PDF data
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


class DataCleaner:
    """
    Comprehensive data cleaning class for DU admission data
    """
    
    def __init__(self):
        self.expected_columns = EXPECTED_COLUMNS
        self.numeric_columns = NUMERIC_COLUMNS
        self.header_patterns = HEADER_PATTERNS
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main cleaning pipeline that processes raw extracted data
        
        Args:
            df: Raw DataFrame from PDF extraction
            
        Returns:
            pd.DataFrame: Clean, structured data
        """
        logger.info("Starting data cleaning pipeline...")
        logger.info(f"Input shape: {df.shape}")
        
        # Step 1: Initial cleanup
        df = self._initial_cleanup(df)
        
        # Step 2: Identify and set proper columns
        df = self._identify_columns(df)
        
        # Step 3: Remove header rows that appear multiple times
        df = self._remove_duplicate_headers(df)
        
        # Step 4: Fix column misalignments (like Evening college names)
        df = self._fix_column_misalignment(df)
        
        # Step 5: Fix corrupted program names (BEFORE merging split rows)
        df = self._fix_corrupted_program_names(df)
        
        # Step 6: Merge split rows (college/program names spanning multiple lines)
        df = self._merge_split_rows(df)
        
        # Step 7: Normalize column alignment
        df = self._normalize_columns(df)
        
        # Step 8: Convert numeric columns
        df = self._convert_numeric_columns(df)
        
        # Step 9: Clean text columns
        df = self._clean_text_columns(df)
        
        # Step 10: Final validation and cleanup
        df = self._final_validation(df)
        
        logger.info(f"✅ Data cleaning complete. Output shape: {df.shape}")
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
    
    def _fix_column_misalignment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix column misalignment issues like Evening college names"""
        logger.info("Step 4: Fixing column misalignments")
        
        fixed_rows = []
        i = 0
        
        while i < len(df):
            current_row = df.iloc[i].copy()
            
            # Check if this is a college-only row followed by an Evening pattern
            if (i < len(df) - 1 and 
                self._is_college_only_row(current_row) and
                self._is_evening_continuation_row(df.iloc[i + 1])):
                
                # Merge the college name with Evening and realign columns
                next_row = df.iloc[i + 1].copy()
                merged_row = self._merge_evening_college_row(current_row, next_row)
                fixed_rows.append(merged_row)
                i += 2  # Skip both rows as we've merged them
                
            else:
                fixed_rows.append(current_row)
                i += 1
        
        # Convert back to DataFrame
        df_fixed = pd.DataFrame(fixed_rows)
        df_fixed = df_fixed.reset_index(drop=True)
        
        logger.info(f"Fixed column misalignments: {len(df)} -> {len(df_fixed)} rows")
        return df_fixed
    
    def _is_college_only_row(self, row: pd.Series) -> bool:
        """Check if row contains only college name (no S.NO., no numbers)"""
        # Should have college name in column 1, but empty S.NO. and no numeric data
        has_college = (len(row) > 1 and 
                      pd.notna(row.iloc[1]) and 
                      str(row.iloc[1]).strip() != '')
        
        # S.NO. should be empty
        sno_empty = (pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '')
        
        # All numeric columns should be empty
        numeric_empty = all(pd.isna(row.iloc[i]) or str(row.iloc[i]).strip() == '' 
                           for i in range(3, min(len(row), 10)))
        
        return has_college and sno_empty and numeric_empty
    
    def _is_evening_continuation_row(self, row: pd.Series) -> bool:
        """Check if row is an Evening college continuation with (Evening) in column 1"""
        # Should have S.NO. in column 0
        has_sno = (pd.notna(row.iloc[0]) and 
                  str(row.iloc[0]).strip().isdigit())
        
        # Should have (Evening) in column 1
        has_evening = (len(row) > 1 and 
                      pd.notna(row.iloc[1]) and 
                      '(Evening)' in str(row.iloc[1]))
        
        return has_sno and has_evening
    
    def _merge_evening_college_row(self, college_row: pd.Series, evening_row: pd.Series) -> pd.Series:
        """Merge college-only row with Evening continuation row"""
        merged = evening_row.copy()
        
        # Combine college name with (Evening)
        college_name = str(college_row.iloc[1]).strip()
        evening_part = str(evening_row.iloc[1]).strip()
        merged.iloc[1] = f"{college_name} {evening_part}"
        
        # The program should move from column 2 to column 2 (stays same)
        # Numeric data should already be in correct positions (columns 3-9)
        
        return merged

    def _merge_split_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Merge rows where college/program names are split across multiple lines"""
        logger.info("Step 6: Merging split rows")
        
        merged_rows = []
        i = 0
        
        while i < len(df):
            current_row = df.iloc[i].copy()
            
            # Check if this might be a split row (empty S.NO. and numeric columns)
            if (i > 0 and 
                self._is_likely_continuation_row(current_row)):
                
                # Merge with previous row
                prev_row = merged_rows[-1]
                merged_row = self._merge_two_rows(prev_row, current_row)
                merged_rows[-1] = merged_row
                
            else:
                merged_rows.append(current_row)
            
            i += 1
        
        # Convert back to DataFrame
        df_merged = pd.DataFrame(merged_rows)
        df_merged = df_merged.reset_index(drop=True)
        
        logger.info(f"Merged from {len(df)} to {len(df_merged)} rows")
        return df_merged
    
    def _is_likely_continuation_row(self, row: pd.Series) -> bool:
        """Check if a row is likely a continuation of the previous row"""
        # Must have empty S.NO. (first column)
        sno_empty = pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == ''
        if not sno_empty:
            return False
        
        # Check if ALL numeric columns (columns 3-9: UR,OBC,SC,ST,EWS,SIKH,PwBD) are empty
        numeric_cols_empty = True
        try:
            # Columns 3-9 are the numeric seat columns
            for i in range(3, min(10, len(row))):
                val = str(row.iloc[i]).strip()
                if val != '' and val != 'nan':
                    numeric_cols_empty = False
                    break
        except:
            pass
        
        # A continuation row should have empty S.NO. AND empty numeric columns
        # It may have college name OR program name continuation text
        college_name = str(row.iloc[1]).strip() if len(row) > 1 else ''
        program_name = str(row.iloc[2]).strip() if len(row) > 2 else ''
        
        # It's a continuation if S.NO. is empty, numeric columns are empty,
        # and there's some text in college or program name columns
        has_continuation_text = (college_name not in ['', 'nan']) or (program_name not in ['', 'nan'])
        
        return sno_empty and numeric_cols_empty and has_continuation_text
    
    def _merge_two_rows(self, row1: pd.Series, row2: pd.Series) -> pd.Series:
        """Merge two rows by concatenating non-empty values"""
        merged = row1.copy()
        
        for i, col in enumerate(merged.index):
            val1 = str(row1.iloc[i] if i < len(row1) else '').strip()
            val2 = str(row2.iloc[i] if i < len(row2) else '').strip()
            
            # Handle empty values
            if val1 in ['', 'nan', 'None']:
                merged.iloc[i] = val2
            elif val2 not in ['', 'nan', 'None']:
                # For college and program names (columns 1 and 2), add space between parts
                if i in [1, 2]:  # College name or program name columns
                    # Check if val2 looks like a continuation (doesn't start with capital or number)
                    if val2.lower().startswith(('science/', 'economics/', 'mathematics/', 'philosophy))', 'history/', 'pol.')):
                        # No space for obvious continuations like "Science/Economics"
                        merged.iloc[i] = f"{val1}{val2}"
                    else:
                        # Add space for other continuations
                        merged.iloc[i] = f"{val1} {val2}".strip()
                else:
                    # For other columns, just concatenate with space
                    merged.iloc[i] = f"{val1} {val2}".strip()
        
        return merged
    
    def _fix_corrupted_program_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix cases where new entries have corrupted program names that are continuations"""
        logger.info("Step 5: Fixing corrupted program names")
        
        original_count = len(df)
        df = df.copy()
        rows_to_remove = []
        
        i = 0
        while i < len(df):
            current_row = df.iloc[i]
            
            # Check if this row has a program that looks like a continuation
            if self._has_corrupted_program_name(current_row):
                # Look back for incomplete program
                incomplete_idx = self._find_incomplete_program_above(df, i)
                if incomplete_idx is not None and incomplete_idx not in rows_to_remove:
                    # Get the incomplete program from the found row
                    incomplete_row = df.iloc[incomplete_idx]
                    incomplete_program = str(incomplete_row.iloc[2]).strip()
                    corrupted_program = str(current_row.iloc[2]).strip()
                    
                    # Combine the programs (remove extra B.A Program text)
                    combined_program = f"{incomplete_program} {corrupted_program}"
                    
                    # Update the current row with the complete program (use column name)
                    program_col = df.columns[2]  # Get the actual column name for program
                    df.at[i, program_col] = combined_program
                    
                    # Mark the incomplete row for removal
                    rows_to_remove.append(incomplete_idx)
                    
                    logger.info(f"Fixed corruption: '{incomplete_program}' + '{corrupted_program}' -> '{combined_program}'")
                    
            i += 1
        
        # Remove the incomplete rows that were merged (in reverse order to maintain indices)
        if rows_to_remove:
            rows_to_remove.sort(reverse=True)
            for idx in rows_to_remove:
                df = df.drop(df.index[idx]).reset_index(drop=True)
        
        logger.info(f"Fixed corrupted program names: {original_count} -> {len(df)} rows")
        return df
    
    def _has_corrupted_program_name(self, row: pd.Series) -> bool:
        """Check if a row has a program name that looks like a continuation"""
        if len(row) < 3:
            return False
            
        program = str(row.iloc[2]).strip()
        
        # Patterns that indicate a continuation/corruption
        corruption_patterns = [
            'Science/Economics/Mathematics/Philosophy))',
            'Science/Economics/Mathematics/Sanskrit))',
            'Science/Economics/Mathematics))',
            'History/Political Science)',
            'Economics/Mathematics/Philosophy))',
            'Science/Economics/Mathematics/',
            'History/Pol.',
            '/Economics/Mathematics',
            'Philosophy))',
            ')) B.A Program',
            # Additional patterns for incomplete continuations
            r'^[A-Za-z]+/[A-Za-z]+/[A-Za-z]+\)?\)?,?$',  # Subjects separated by /
            r'^\)\),?$',  # Just closing parentheses
        ]
        
        # Check literal patterns first
        for pattern in corruption_patterns[:10]:  # First 10 are literal
            if pattern in program:
                return True
        
        # Check regex patterns
        import re
        for pattern in corruption_patterns[10:]:  # Last ones are regex
            if re.match(pattern, program):
                return True
                
        return False
    
    def _find_incomplete_program_above(self, df: pd.DataFrame, current_idx: int) -> Optional[int]:
        """Find the most recent row above with an incomplete program name"""
        # Look back only 1-2 rows to find the direct incomplete pair
        for i in range(max(0, current_idx - 2), current_idx):
            if i < len(df):
                row = df.iloc[i]
                program = str(row.iloc[2]).strip()
                college = str(row.iloc[1]).strip() if len(row) > 1 else ""
                
                # Only look for rows that have empty college names (these are the direct continuation rows)
                if college in ['', 'nan', 'None']:
                    # Check if program ends with patterns that suggest it's incomplete
                    incomplete_patterns = [
                        '(English/Hindi/History/Pol.',
                        '+ Any One Out Of These (English/Hindi/History/Pol.',
                        '(Sanskrit + Any One Out Of These (English/Hindi/History/Pol.',
                        'Any one out of these (English/Hindi/History/Pol.',
                        'Any two discipline from these (English/Hindi/History/Pol.',
                        'Philosophy + Any one out of these (English/Hindi/History/Pol.',
                    ]
                    
                    if any(pattern in program for pattern in incomplete_patterns):
                        return i
        
        return None
    
    def _has_valid_content(self, row: pd.Series) -> bool:
        """Check if row has valid content worth keeping"""
        # Must have S.NO.
        has_sno = (pd.notna(row.iloc[0]) and str(row.iloc[0]).strip().isdigit())
        
        # Must have college name
        has_college = (len(row) > 1 and pd.notna(row.iloc[1]) and 
                      str(row.iloc[1]).strip() not in ['', 'nan'])
        
        return bool(has_sno and has_college)

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix column misalignment issues"""
        logger.info("Step 5: Normalizing column alignment")
        
        # This is where we can implement logic to detect and fix
        # cases where numbers have shifted to wrong columns
        
        for i in range(len(df)):
            # Check if numeric values are in the right places
            # and shift them if needed
            row = df.iloc[i]
            df.iloc[i] = self._fix_column_alignment(row)
        
        return df
    
    def _fix_column_alignment(self, row: pd.Series) -> pd.Series:
        """Fix alignment issues in a single row"""
        # Extract all numeric values from the row
        numeric_values = []
        text_values = {}
        
        for col in row.index:
            val = str(row[col]).strip()
            
            if col in ['S.NO.', 'NAME OF THE COLLEGE', 'NAME OF THE PROGRAM']:
                text_values[col] = val
            elif val.isdigit():
                numeric_values.append(int(val))
            elif val == '' or val == 'nan':
                numeric_values.append(0)
            else:
                # Try to extract number from string
                numbers = re.findall(r'\d+', val)
                if numbers:
                    numeric_values.append(int(numbers[0]))
                else:
                    numeric_values.append(0)
        
        # Rebuild the row with proper alignment
        fixed_row = row.copy()
        
        # Set text columns
        for col, val in text_values.items():
            fixed_row[col] = val
        
        # Distribute numeric values to numeric columns
        for i, col in enumerate(self.numeric_columns):
            if i < len(numeric_values):
                fixed_row[col] = str(numeric_values[i])
            else:
                fixed_row[col] = '0'
        
        return fixed_row
    
    def _convert_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert numeric columns from string to integer"""
        logger.info("Step 6: Converting numeric columns")
        
        for col in self.numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._safe_int_convert)
        
        return df
    
    def _safe_int_convert(self, value) -> int:
        """Safely convert a value to integer"""
        try:
            # Handle different input types
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
        logger.info("Step 7: Cleaning text columns")
        
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
        
        # Fix common OCR errors
        text = text.replace('|', 'I')  # Pipe to I
        text = text.replace('0', 'O')  # Zero to O in college names (if appropriate)
        
        return text.title()  # Title case
    
    def _final_validation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final validation and cleanup"""
        logger.info("Step 8: Final validation")
        initial_count = len(df)
        
        # Remove rows where college name is empty
        before_college_filter = len(df)
        df = df[df['NAME OF THE COLLEGE'].str.strip() != '']
        after_college_filter = len(df)
        if before_college_filter != after_college_filter:
            logger.info(f"Removed {before_college_filter - after_college_filter} rows with empty college names")
        
        # Instead of removing rows with all zeros, just log them
        # Some programs might legitimately have 0 seats in all categories
        before_zero_filter = len(df)
        numeric_sum = df[self.numeric_columns].sum(axis=1)
        zero_rows = df[numeric_sum == 0]
        if len(zero_rows) > 0:
            logger.info(f"Found {len(zero_rows)} rows with all zero seats (keeping them)")
            # Only remove if ALL columns including college/program names are also empty/invalid
            valid_data_mask = (
                (df['NAME OF THE COLLEGE'].str.strip() != '') & 
                (df['NAME OF THE PROGRAM'].str.strip() != '')
            )
            df = df[valid_data_mask]
            after_validation_filter = len(df)
            if before_zero_filter != after_validation_filter:
                logger.info(f"Removed {before_zero_filter - after_validation_filter} rows with invalid data")
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Add row numbers if S.NO. is missing
        if 'S.NO.' in df.columns:
            df['S.NO.'] = range(1, len(df) + 1)
        
        final_count = len(df)
        logger.info(f"Final validation: {initial_count} -> {final_count} rows (lost {initial_count - final_count})")
        
        return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function for data cleaning
    
    Args:
        df: Raw DataFrame from PDF extraction
        
    Returns:
        pd.DataFrame: Clean data
    """
    cleaner = DataCleaner()
    return cleaner.clean_data(df)
