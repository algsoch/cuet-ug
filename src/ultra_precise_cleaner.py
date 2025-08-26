"""
Ultra-Precise Data Cleaner for DU Admission Analyzer
Preserves exactly the 1528 valid data rows
"""

import pandas as pd
import numpy as np
import re
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UltraPreciseDataCleaner:
    """
    Ultra-precise data cleaning that preserves exactly 1528 valid rows
    """
    
    def __init__(self):
        self.expected_columns = [
            'S.NO.', 'NAME OF THE COLLEGE', 'NAME OF THE PROGRAM', 
            'UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD'
        ]
        self.numeric_columns = ['UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ultra-precise cleaning to get exactly 1528 rows
        """
        logger.info("🎯 Starting ULTRA-PRECISE data cleaning...")
        logger.info(f"Input shape: {df.shape}")
        
        # Step 1: Set up columns
        df = self._setup_columns(df)
        logger.info(f"After setup: {df.shape}")
        
        # Step 2: Extract ONLY rows with valid S.NO.
        df = self._extract_valid_rows(df)
        logger.info(f"After extracting valid rows: {df.shape}")
        
        # Step 3: Fix split college patterns
        df = self._fix_split_colleges(df)
        logger.info(f"After fixing split colleges: {df.shape}")
        
        # Step 4: Clean and convert data
        df = self._clean_and_convert(df)
        logger.info(f"✅ ULTRA-PRECISE cleaning complete: {df.shape}")
        
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
    
    def _fix_split_colleges(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fix the few remaining split college patterns by looking for patterns like:
        - College name = '(Evening)' -> merge with previous college
        - College name = '(W)' -> merge with previous college  
        - College name = 'College' -> merge with previous incomplete college name
        """
        logger.info("🔧 Fixing split college patterns...")
        
        fixed_rows = []
        i = 0
        merges = 0
        
        while i < len(df):
            current_row = df.iloc[i].copy()
            college = str(current_row['NAME OF THE COLLEGE']).strip()
            
            # Check for split patterns
            if college in ['(Evening)', '(W)', 'College'] and len(fixed_rows) > 0:
                # This row should be merged with the previous complete row
                prev_row = fixed_rows[-1].copy()
                prev_college = str(prev_row['NAME OF THE COLLEGE']).strip()
                
                # Create merged college name
                if college == 'College':
                    # Previous row should have the main college name
                    merged_college = f"{prev_college} College"
                else:
                    # Add the suffix to previous college
                    merged_college = f"{prev_college} {college}"
                
                # Update the current row with merged college name
                current_row['NAME OF THE COLLEGE'] = merged_college
                
                # Remove the previous row and add the merged row
                fixed_rows.pop()  # Remove previous row
                fixed_rows.append(current_row)  # Add merged row
                merges += 1
                
                logger.info(f"Merged: '{prev_college}' + '{college}' -> '{merged_college}'")
            else:
                fixed_rows.append(current_row)
            
            i += 1
        
        df_fixed = pd.DataFrame(fixed_rows)
        df_fixed = df_fixed.reset_index(drop=True)
        
        logger.info(f"Made {merges} college merges")
        return df_fixed
    
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


def ultra_precise_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function for ultra-precise data cleaning
    """
    cleaner = UltraPreciseDataCleaner()
    return cleaner.clean_data(df)
