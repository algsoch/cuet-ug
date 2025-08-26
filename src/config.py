"""
Configuration module for DU Admission Analyzer
Contains all constants and configuration settings
"""

# Column mappings and configurations
EXPECTED_COLUMNS = [
    'S.NO.',
    'NAME OF THE COLLEGE',
    'NAME OF THE PROGRAM',
    'UR',
    'OBC',
    'SC',
    'ST',
    'EWS',
    'SIKH',
    'PwBD'
]

# Category full names for better readability
CATEGORY_NAMES = {
    'UR': 'Unreserved (General)',
    'OBC': 'Other Backward Class',
    'SC': 'Scheduled Caste',
    'ST': 'Scheduled Tribe',
    'EWS': 'Economically Weaker Section',
    'SIKH': 'Sikh Minority',
    'PwBD': 'Persons with Benchmark Disabilities'
}

# Numeric columns that should be converted from string to int
NUMERIC_COLUMNS = ['UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']

# Common headers that appear repeatedly in PDFs and should be removed
HEADER_PATTERNS = [
    'S.NO.',
    'NAME OF THE COLLEGE',
    'NAME OF THE PROGRAM',
    'PROGRAM',
    'COLLEGE'
]

# PDF extraction settings
PDF_EXTRACTION_SETTINGS = {
    'pages': 'all',
    'multiple_tables': True,
    'pandas_options': {
        'header': None,
        'dtype': str
    },
    'java_options': ["-Xmx1024m"]  # Increase memory for large PDFs
}

# File paths
DEFAULT_OUTPUT_DIR = "outputs"
DEFAULT_DATA_DIR = "data"

# Excel export settings
EXCEL_SHEETS = {
    'raw_data': 'Raw Data',
    'analytics': 'Analytics Summary',
    'college_wise': 'College-wise Analysis',
    'program_wise': 'Program-wise Analysis',
    'category_wise': 'Category-wise Analysis'
}
