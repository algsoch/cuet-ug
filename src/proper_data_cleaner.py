"""
Proper Data Cleaner for DU Admission Analyzer
Correctly handles college name patterns in PDF extraction
"""

import pandas as pd
import numpy as np
import re
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProperDataCleaner:
    """
    Proper data cleaning that correctly handles all patterns
    """
    
    def __init__(self):
        self.expected_columns = [
            'S.NO.', 'NAME OF THE COLLEGE', 'NAME OF THE PROGRAM', 
            'UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD'
        ]
        self.numeric_columns = ['UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Proper cleaning to get exactly 1528 rows with correct college names
        """
        logger.info("🎯 Starting PROPER data cleaning...")
        logger.info(f"Input shape: {df.shape}")
        
        # Step 1: Set up columns
        df = self._setup_columns(df)
        logger.info(f"After setup: {df.shape}")
        
        # Step 2: Extract ONLY rows with valid S.NO.
        df = self._extract_valid_rows(df)
        logger.info(f"After extracting valid rows: {df.shape}")
        
        # Step 3: Fix college name assignments
        df = self._fix_college_names(df)
        logger.info(f"After fixing college names: {df.shape}")
        
        # Step 4: Clean and convert data
        df = self._clean_and_convert(df)
        logger.info(f"✅ PROPER cleaning complete: {df.shape}")
        
        return df
    
    def _setup_columns(self, df: pd.DataFrame) -> pd.DataFrame:
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
    
    def _extract_valid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract ONLY rows with valid S.NO. - these are our 1528 target rows"""
        logger.info("🎯 Extracting only rows with valid S.NO....")
        
        valid_rows = []
        
        for i, row in df.iterrows():
            sno = str(row['S.NO.']).strip()
            
            # Only keep rows with numeric S.NO.
            if sno.isdigit():
                valid_rows.append(row)
        
        df_valid = pd.DataFrame(valid_rows)
        df_valid = df_valid.reset_index(drop=True)
        
        logger.info(f"Extracted {len(df_valid)} rows with valid S.NO.")
        return df_valid
    
    def _fix_college_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fix college name assignments by looking at patterns:
        1. Split college names like 'Sri Guru Tegh Bahadur Khalsa' + 'College'
        2. Suffix patterns like college name followed by '(W)' or '(Evening)' entries  
        3. Department/Faculty fragments that should be merged
        4. Load context from raw data for better reconstruction
        """
        logger.info("🔧 Fixing college name assignments...")
        
        # Load raw data for context (but only use for specific problem cases)
        raw_df = self._load_raw_context()
        
        # Define known split patterns based on analysis
        split_patterns = {
            'Sciences': 'Bhaskaracharya College of Applied Sciences',
            'Commerce': 'Delhi College of Arts and Commerce', 
            'Romance Studies': 'Department of Germanic and Romance Studies',
            'Ugrian Studies': 'Department of Slavonic and Finno Ugrian Studies',
            'Sciences for Women (W)': 'Bhaskaracharya College of Applied Sciences for Women (W)',
        }
        
        # Keep track of the current college name context
        current_college = None
        fixed_count = 0
        
        for i in range(len(df)):
            college = str(df.at[i, 'NAME OF THE COLLEGE']).strip()
            program = str(df.at[i, 'NAME OF THE PROGRAM']).strip()
            s_no = str(df.at[i, 'S.NO.']).strip()
            
            # Case 1: Known split patterns - use the full name
            if college in split_patterns:
                full_college_name = split_patterns[college]
                df.at[i, 'NAME OF THE COLLEGE'] = full_college_name
                current_college = full_college_name
                fixed_count += 1
                
                if fixed_count <= 5:
                    logger.info(f"Fixed split: '{college}' -> '{full_college_name}'")
            
            # Case 2: Full college name
            elif (college not in ['(W)', '(Evening)', 'College', '', 'nan', 'For Women (W)'] and 
                  not college.startswith('(') and 
                  len(college) > 3):
                current_college = college
            
            # Case 3: Suffix patterns - assign to most recent college
            elif college in ['(W)', '(Evening)'] and current_college:
                full_college_name = f"{current_college} {college}"
                df.at[i, 'NAME OF THE COLLEGE'] = full_college_name
                fixed_count += 1
                
                if fixed_count <= 10:  # Log first few fixes
                    logger.info(f"Fixed suffix: '{college}' -> '{full_college_name}' (Program: {program[:50]}...)")
            
            # Case 4: 'College' only - merge with previous incomplete college name
            elif college == 'College' and current_college:
                # Check if current_college already ends with 'College'
                if not current_college.endswith('College'):
                    full_college_name = f"{current_college} College"
                    df.at[i, 'NAME OF THE COLLEGE'] = full_college_name
                    fixed_count += 1
                    
                    if fixed_count <= 10:
                        logger.info(f"Fixed: '{current_college}' + 'College' -> '{full_college_name}'")
                else:
                    # Already ends with College, just use it
                    df.at[i, 'NAME OF THE COLLEGE'] = current_college
                    fixed_count += 1
            
            # Case 5: 'For Women (W)' - look up in raw data for context
            elif college == 'For Women (W)':
                context_college = self._find_context_college(raw_df, s_no, program)
                if context_college:
                    full_college_name = f"{context_college} for Women (W)"
                    df.at[i, 'NAME OF THE COLLEGE'] = full_college_name
                    current_college = full_college_name
                    fixed_count += 1
                    
                    if fixed_count <= 10:
                        logger.info(f"Fixed context: 'For Women (W)' -> '{full_college_name}'")
                elif current_college:
                    full_college_name = f"{current_college} for Women (W)"
                    df.at[i, 'NAME OF THE COLLEGE'] = full_college_name
                    fixed_count += 1
            
            # Case 6: Empty or problematic college names - use previous college
            elif college in ['', 'nan', 'None'] and current_college:
                df.at[i, 'NAME OF THE COLLEGE'] = current_college
                fixed_count += 1
        
        logger.info(f"Fixed {fixed_count} college name assignments")
        return df
    
    def _load_raw_context(self) -> pd.DataFrame:
        """Load raw data for context lookup"""
        try:
            raw_df = pd.read_csv("data/raw_extraction_20250825_232420.csv")
            if '1' in raw_df.columns:
                raw_df.columns = ['S.NO.', 'NAME OF THE COLLEGE', 'NAME OF THE PROGRAM', 'UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
                raw_df = raw_df.iloc[1:]  # Skip header
            return raw_df
        except:
            return pd.DataFrame()
    
    def _find_context_college(self, raw_df: pd.DataFrame, s_no: str, program: str) -> str:
        """Find the context college name for a given S.NO. and program"""
        if raw_df.empty:
            return ""
        
        try:
            # Find the row with this S.NO. and program in raw data
            matches = raw_df[(raw_df['S.NO.'] == s_no) & (raw_df['NAME OF THE PROGRAM'] == program)]
            
            if not matches.empty:
                row_idx = matches.index[0]
                
                # Look backwards for context
                for look_back in range(1, min(20, row_idx + 1)):
                    back_idx = row_idx - look_back
                    back_s_no = str(raw_df.iloc[back_idx]['S.NO.']).strip()
                    back_college = str(raw_df.iloc[back_idx]['NAME OF THE COLLEGE']).strip()
                    
                    # Look for context rows or valid college names
                    if back_s_no in ['nan', ''] and len(back_college) > 10:
                        # Found a context row with college name
                        if 'College' in back_college or 'School' in back_college:
                            return back_college
                    elif back_s_no not in ['nan', ''] and len(back_college) > 10:
                        # Found a valid college name
                        if 'College' in back_college or 'School' in back_college:
                            return back_college
                        
        except Exception as e:
            logger.warning(f"Error finding context for S.NO. {s_no}: {e}")
        
        return ""
    
    def _clean_and_convert(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and convert the data"""
        logger.info("🧼 Final cleaning and conversion...")
        
        # Convert numeric columns
        for col in self.numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._safe_int_convert)
        
        # Clean text columns
        text_columns = ['NAME OF THE COLLEGE', 'NAME OF THE PROGRAM']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._clean_text)
        
        # Ensure S.NO. is sequential
        df['S.NO.'] = range(1, len(df) + 1)
        
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


def proper_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function for proper data cleaning
    """
    cleaner = ProperDataCleaner()
    return cleaner.clean_data(df)
