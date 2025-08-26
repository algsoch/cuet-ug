"""
PDF Extraction Module for DU Admission Analyzer
Handles extraction of tabular data from PDF files using multiple extraction methods
"""

import pandas as pd
import pdfplumber
import logging
import os
from typing import List, Optional, Dict, Any
import requests
from io import BytesIO
from .config import PDF_EXTRACTION_SETTINGS, EXPECTED_COLUMNS

# Try to import tabula, but handle gracefully if not available
try:
    from tabula.io import read_pdf
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False
    read_pdf = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not TABULA_AVAILABLE:
    logger.warning("Tabula not available. PDF extraction will use pdfplumber only.")


class PDFExtractor:
    """
    A robust PDF table extraction class that tries multiple methods
    to extract tabular data from DU admission PDFs
    """
    
    def __init__(self):
        # Only include tabula methods if tabula is available
        self.extraction_methods = [
            self._extract_with_pdfplumber,
        ]
        
        if TABULA_AVAILABLE:
            self.extraction_methods.extend([
                self._extract_with_tabula,
                self._extract_with_tabula_lattice
            ])
    
    def extract_pdf(self, pdf_source: str) -> pd.DataFrame:
        """
        Main extraction method that tries multiple approaches
        
        Args:
            pdf_source: File path or URL to the PDF
            
        Returns:
            pd.DataFrame: Extracted and initially cleaned data
            
        Raises:
            Exception: If all extraction methods fail
        """
        logger.info(f"Starting PDF extraction from: {pdf_source}")
        
        # Handle URL downloads
        if pdf_source.startswith(('http://', 'https://')):
            pdf_source = self._download_pdf(pdf_source)
        
        # Validate file exists
        if not os.path.exists(pdf_source):
            raise FileNotFoundError(f"PDF file not found: {pdf_source}")
        
        # Try each extraction method
        for i, method in enumerate(self.extraction_methods, 1):
            try:
                logger.info(f"Attempting extraction method {i}: {method.__name__}")
                df = method(pdf_source)
                
                if df is not None and not df.empty:
                    logger.info(f"✅ Successfully extracted {len(df)} rows using {method.__name__}")
                    
                    # Save raw data before any cleaning
                    self._save_raw_data(df, pdf_source)
                    
                    return self._initial_cleanup(df)
                    
            except Exception as e:
                logger.warning(f"❌ Method {method.__name__} failed: {str(e)}")
                continue
        
        raise Exception("All PDF extraction methods failed. Please check the PDF format.")
    
    def _download_pdf(self, url: str) -> str:
        """Download PDF from URL to temporary location"""
        try:
            logger.info(f"Downloading PDF from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save to data directory
            filename = url.split('/')[-1]
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            filepath = os.path.join('data', filename)
            os.makedirs('data', exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ PDF downloaded to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download PDF: {str(e)}")
            raise
    
    def _extract_with_tabula(self, pdf_path: str) -> Optional[pd.DataFrame]:
        """Extract using tabula-py with stream detection"""
        if not TABULA_AVAILABLE or read_pdf is None:
            logger.info("Tabula not available, skipping tabula extraction method")
            return None
            
        try:
            # Try with stream detection first
            dfs = read_pdf(
                pdf_path,
                pages='all',
                multiple_tables=True,
                pandas_options={'header': None, 'dtype': str},
                java_options=["-Xmx1024m"]
            )
            
            if dfs:
                combined_df = pd.concat(dfs, ignore_index=True)
                return combined_df
                
        except Exception as e:
            logger.warning(f"Tabula stream method failed: {str(e)}")
            return None
    
    def _extract_with_tabula_lattice(self, pdf_path: str) -> Optional[pd.DataFrame]:
        """Extract using tabula-py with lattice detection"""
        if not TABULA_AVAILABLE or read_pdf is None:
            logger.info("Tabula not available, skipping tabula lattice method")
            return None
            
        try:
            dfs = read_pdf(
                pdf_path,
                pages='all',
                multiple_tables=True,
                lattice=True,
                pandas_options={'header': None, 'dtype': str},
                java_options=["-Xmx1024m"]
            )
            
            if dfs:
                combined_df = pd.concat(dfs, ignore_index=True)
                return combined_df
                
        except Exception as e:
            logger.warning(f"Tabula lattice method failed: {str(e)}")
            return None
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Optional[pd.DataFrame]:
        """Extract using pdfplumber as fallback"""
        try:
            all_rows = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if table:
                            all_rows.extend(table)
            
            if all_rows:
                df = pd.DataFrame(all_rows)
                return df
                
        except Exception as e:
            logger.warning(f"PDFPlumber method failed: {str(e)}")
            return None
    
    def _initial_cleanup(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform initial cleanup on extracted data
        """
        logger.info("Performing initial cleanup...")
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Convert all data to string for consistent processing
        df = df.astype(str)
        
        # Replace 'nan' strings with empty strings
        df = df.replace('nan', '')
        
        # Strip whitespace from all text columns
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        
        logger.info(f"Initial cleanup complete. Shape: {df.shape}")
        return df
    
    def _save_raw_data(self, df: pd.DataFrame, pdf_source: str) -> None:
        """Save raw extracted data before any cleaning"""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"raw_extraction_{timestamp}.csv"
            
            # Create outputs directory if it doesn't exist
            os.makedirs('outputs', exist_ok=True)
            filepath = os.path.join('outputs', filename)
            
            df.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"💾 Raw data saved to: {filepath}")
            
        except Exception as e:
            logger.warning(f"Failed to save raw data: {str(e)}")


def extract_pdf(pdf_source: str) -> pd.DataFrame:
    """
    Convenience function for PDF extraction
    
    Args:
        pdf_source: Path or URL to PDF file
        
    Returns:
        pd.DataFrame: Extracted data
    """
    extractor = PDFExtractor()
    return extractor.extract_pdf(pdf_source)
