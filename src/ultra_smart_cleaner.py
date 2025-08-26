import pandas as pd
import logging

logger = logging.getLogger(__name__)

class UltraSmartDataCleaner:
    """Ultra-smart data cleaner with sophisticated college name reconstruction"""
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    def clean(self, input_file: str) -> pd.DataFrame:
        """
        Ultra-smart cleaning with context-aware college name reconstruction
        """
        logger.info("🎯 Starting ULTRA-SMART data cleaning...")
        
        # Load raw data
        df = pd.read_csv(input_file)
        logger.info(f"Input shape: {df.shape}")
        
        # Handle the numeric column names issue
        if '1' in df.columns:
            df.columns = ['S.NO.', 'NAME OF THE COLLEGE', 'NAME OF THE PROGRAM', 'UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
            df = df.iloc[1:]  # Skip the header row
        
        # Initial setup
        df = self._setup_data(df)
        logger.info(f"After setup: {df.shape}")
        
        # Step 1: Extract only rows with valid S.NO.
        df = self._extract_valid_rows(df)
        logger.info(f"After extracting valid rows: {df.shape}")
        
        # Step 2: Ultra-smart college name reconstruction using full context
        df = self._ultra_smart_college_reconstruction(df, input_file)
        logger.info(f"After ultra-smart college reconstruction: {df.shape}")
        
        # Step 3: Final cleaning
        df = self._final_cleaning(df)
        logger.info(f"✅ ULTRA-SMART cleaning complete: {df.shape}")
        
        return df
    
    def _setup_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Setup data with proper types"""
        # Clean up any remaining header issues
        df = df[df['S.NO.'] != 'S. NO.'].copy()
        return df
    
    def _extract_valid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract only rows with valid S.NO."""
        logger.info("🎯 Extracting only rows with valid S.NO....")
        
        def is_valid_s_no(s_no):
            try:
                s_no_str = str(s_no).strip()
                if s_no_str in ['', 'nan', 'None']:
                    return False
                int(s_no_str)
                return True
            except:
                return False
        
        valid_rows = df[df['S.NO.'].apply(is_valid_s_no)].copy()
        logger.info(f"Extracted {len(valid_rows)} rows with valid S.NO.")
        
        return valid_rows
    
    def _ultra_smart_college_reconstruction(self, df: pd.DataFrame, raw_file: str) -> pd.DataFrame:
        """
        Ultra-smart college name reconstruction using full raw data context
        """
        logger.info("🧠 Ultra-smart college name reconstruction...")
        
        # Load the raw data again to access full context
        raw_df = pd.read_csv(raw_file)
        if '1' in raw_df.columns:
            raw_df.columns = ['S.NO.', 'NAME OF THE COLLEGE', 'NAME OF THE PROGRAM', 'UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
            raw_df = raw_df.iloc[1:]  # Skip header
        
        # Build a context map by looking at ALL raw data
        context_map = self._build_context_map(raw_df)
        
        # Apply context-aware fixes
        df = self._apply_context_fixes(df, context_map)
        
        return df
    
    def _build_context_map(self, raw_df: pd.DataFrame) -> dict:
        """
        Build a smart context map by analyzing patterns in raw data
        """
        logger.info("📊 Building context map from raw data...")
        
        context_map = {}
        
        # Track the most recent full college name
        current_full_college = None
        
        for i in range(len(raw_df)):
            s_no = str(raw_df.iloc[i]['S.NO.']).strip()
            college = str(raw_df.iloc[i]['NAME OF THE COLLEGE']).strip()
            program = str(raw_df.iloc[i]['NAME OF THE PROGRAM']).strip()
            
            # Check if this is a valid S.NO. row
            try:
                int(s_no)
                is_valid_s_no = True
            except:
                is_valid_s_no = False
            
            if is_valid_s_no:
                # This is a program row
                
                # Case 1: Full college name
                if (len(college) > 10 and 
                    college not in ['(W)', '(Evening)', 'College', 'Sciences', 'Commerce', 'Studies', 'For Women (W)', 'Sciences for Women (W)'] and
                    not college.startswith('(') and
                    'College' in college or 'Department' in college or 'Centre' in college or 'School' in college):
                    
                    current_full_college = college
                    context_map[s_no] = college
                
                # Case 2: Fragment that needs reconstruction
                elif college in ['(W)', '(Evening)', 'College', 'Sciences', 'Commerce', 'Studies', 'For Women (W)', 'Sciences for Women (W)']:
                    
                    # Look backwards for the full college name
                    full_college = self._find_full_college_backwards(raw_df, i, college)
                    
                    if full_college:
                        context_map[s_no] = full_college
                    elif current_full_college:
                        # Fallback to current context
                        if college == '(W)':
                            context_map[s_no] = f"{current_full_college} (W)"
                        elif college == '(Evening)':
                            context_map[s_no] = f"{current_full_college} (Evening)"
                        elif college == 'College':
                            context_map[s_no] = f"{current_full_college}"
                        else:
                            context_map[s_no] = current_full_college
                
                # Case 3: Other cases
                else:
                    if current_full_college:
                        context_map[s_no] = current_full_college
        
        logger.info(f"Built context map with {len(context_map)} entries")
        return context_map
    
    def _find_full_college_backwards(self, raw_df: pd.DataFrame, current_idx: int, fragment: str) -> str:
        """
        Look backwards in raw data to find the full college name for a fragment
        """
        # Look back up to 50 rows
        for look_back in range(1, min(51, current_idx + 1)):
            back_idx = current_idx - look_back
            back_s_no = str(raw_df.iloc[back_idx]['S.NO.']).strip()
            back_college = str(raw_df.iloc[back_idx]['NAME OF THE COLLEGE']).strip()
            
            # Check if this is a context row (nan S.NO.) with a full college name
            if back_s_no in ['nan', 'None', ''] and len(back_college) > 10:
                
                # Known patterns
                if fragment == 'Sciences' and 'Applied' in back_college:
                    return 'Bhaskaracharya College of Applied Sciences'
                elif fragment == 'Commerce' and 'Arts' in back_college:
                    return 'Delhi College of Arts and Commerce'
                elif fragment == 'Studies' and 'Germanic' in back_college:
                    return 'Department of Germanic and Romance Studies'
                elif fragment == 'Studies' and 'Slavonic' in back_college:
                    return 'Department of Slavonic and Finno Ugrian Studies'
                elif fragment == 'Sciences for Women (W)' and 'Applied' in back_college:
                    return 'Bhaskaracharya College of Applied Sciences for Women (W)'
                elif fragment == 'For Women (W)' and len(back_college) > 5:
                    return f"{back_college} for Women (W)"
            
            # Check if this is a valid S.NO. row with a full college name
            try:
                int(back_s_no)
                is_valid = True
            except:
                is_valid = False
            
            if is_valid and len(back_college) > 10:
                if fragment == '(W)':
                    return f"{back_college} (W)"
                elif fragment == '(Evening)':
                    return f"{back_college} (Evening)"
                elif fragment == 'College' and not back_college.endswith('College'):
                    return f"{back_college} College"
                else:
                    return back_college
        
        return ""
    
    def _apply_context_fixes(self, df: pd.DataFrame, context_map: dict) -> pd.DataFrame:
        """
        Apply the context-based fixes to the dataframe
        """
        logger.info("🔧 Applying context-based fixes...")
        
        fixed_count = 0
        
        for i in range(len(df)):
            s_no = str(df.iloc[i]['S.NO.']).strip()
            
            if s_no in context_map:
                original_college = df.iloc[i]['NAME OF THE COLLEGE']
                new_college = context_map[s_no]
                
                if original_college != new_college:
                    df.at[i, 'NAME OF THE COLLEGE'] = new_college
                    fixed_count += 1
                    
                    if fixed_count <= 10:  # Log first 10 fixes
                        logger.info(f"Fixed: '{original_college}' -> '{new_college}'")
        
        logger.info(f"Applied {fixed_count} context-based fixes")
        return df
    
    def _final_cleaning(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final data cleaning and conversion"""
        logger.info("🧼 Final cleaning and conversion...")
        
        # Convert numeric columns
        numeric_columns = ['UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Clean string columns
        string_columns = ['NAME OF THE COLLEGE', 'NAME OF THE PROGRAM']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        return df
