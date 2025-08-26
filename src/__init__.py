"""
DU Admission Analyzer Package
A comprehensive tool for extracting, cleaning, analyzing, and exporting Delhi University admission data
"""

from .pipeline import process_admission_pdf, batch_process_pdfs, DUAdmissionPipeline
from .pdf_extractor import extract_pdf
from .data_cleaner import clean_data
from .analytics import generate_analytics_summary
from .excel_exporter import export_to_excel

__version__ = "1.0.0"
__author__ = "DU Admission Analysis Team"

# Main functions for easy import
__all__ = [
    'process_admission_pdf',
    'batch_process_pdfs', 
    'DUAdmissionPipeline',
    'extract_pdf',
    'clean_data',
    'generate_analytics_summary',
    'export_to_excel'
]
