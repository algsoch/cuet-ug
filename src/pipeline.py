"""
Main Pipeline Module for DU Admission Analyzer
Orchestrates the complete data processing pipeline
"""

import pandas as pd
import logging
from typing import Optional, Dict, Any
import os
from datetime import datetime

from .pdf_extractor import extract_pdf
from .data_cleaner import clean_data
from .improved_data_cleaner import clean_data_improved
from .smart_data_cleaner import smart_clean_data
from .perfect_data_cleaner import PerfectDataCleaner
from .analytics import generate_analytics_summary, set_current_clean_data
from .excel_exporter import export_to_excel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DUAdmissionPipeline:
    """
    Complete pipeline for processing DU admission PDFs
    """
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Pipeline state
        self.raw_data = None
        self.clean_data = None
        self.analytics = None
        self.export_path = None
        
        logger.info(f"Pipeline initialized with output directory: {output_dir}")
    
    def process_pdf(self, pdf_source: str, export_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete pipeline: extract → clean → analyze → export
        
        Args:
            pdf_source: Path or URL to PDF file
            export_filename: Optional custom filename for Excel export
            
        Returns:
            Dict containing all results and file paths
        """
        try:
            logger.info("🚀 Starting DU Admission Analysis Pipeline")
            logger.info(f"Processing PDF: {pdf_source}")
            
            # Step 1: Extract data from PDF
            logger.info("📄 Step 1: Extracting data from PDF...")
            self.raw_data = extract_pdf(pdf_source)
            logger.info(f"✅ Extracted {len(self.raw_data)} rows")
            
            # Step 2: Clean and normalize data using PERFECT cleaner
            logger.info("🧹 Step 2: Cleaning and normalizing data with PERFECT cleaner...")
            
            # Save raw data first
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_csv_path = os.path.join(self.output_dir, f"raw_extraction_{timestamp}.csv")
            self.raw_data.to_csv(raw_csv_path, index=False)
            
            # Use perfect cleaner
            perfect_cleaner = PerfectDataCleaner()
            self.clean_data = perfect_cleaner.clean(raw_csv_path)
            logger.info(f"✅ PERFECT cleaned data: {len(self.clean_data)} rows, {self.clean_data['NAME OF THE COLLEGE'].nunique()} unique colleges")
            
            # Set current data for backend caching
            set_current_clean_data(self.clean_data)
            
            # Step 3: Generate analytics
            logger.info("📊 Step 3: Generating analytics...")
            self.analytics = generate_analytics_summary(self.clean_data)
            logger.info("✅ Analytics generated")
            
            # Step 4: Export to Excel
            logger.info("📤 Step 4: Exporting to Excel...")
            self.export_path = export_to_excel(
                self.clean_data, 
                filename=export_filename,
                output_dir=self.output_dir
            )
            logger.info(f"✅ Exported to: {self.export_path}")
            
            # Step 5: Save clean data as CSV backup
            csv_path = self._save_csv_backup()
            
            # Compile results
            results = {
                'success': True,
                'data_shape': self.clean_data.shape,
                'analytics': self.analytics,
                'files': {
                    'excel': self.export_path,
                    'csv': csv_path
                },
                'summary': self._generate_summary()
            }
            
            logger.info("🎉 Pipeline completed successfully!")
            return results
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'stage': self._get_current_stage()
            }
    
    def _save_csv_backup(self) -> str:
        """Save clean data as CSV backup with PERFECT naming convention"""
        if self.clean_data is None:
            raise ValueError("No clean data available to save")
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"DU_Admission_PERFECT_Clean_{timestamp}.csv"
        csv_path = os.path.join(self.output_dir, csv_filename)
        
        self.clean_data.to_csv(csv_path, index=False)
        logger.info(f"� Perfect cleaned data saved to: {csv_path}")
        
        return csv_path
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the processing results"""
        if self.analytics is None:
            return {}
        
        overview = self.analytics.get('overview', {})
        insights = self.analytics.get('insights', [])
        
        return {
            'total_seats': overview.get('total_seats', 0),
            'total_colleges': overview.get('total_colleges', 0),
            'total_programs': overview.get('total_programs', 0),
            'key_insights': insights[:3] if insights else [],  # Top 3 insights
            'processing_timestamp': datetime.now().isoformat()
        }
    
    def _get_current_stage(self) -> str:
        """Get current processing stage for error reporting"""
        if self.export_path:
            return "export"
        elif self.analytics:
            return "analytics"
        elif self.clean_data is not None:
            return "cleaning"
        elif self.raw_data is not None:
            return "extraction"
        else:
            return "initialization"
    
    def get_clean_dataframe(self) -> Optional[pd.DataFrame]:
        """Get the clean DataFrame"""
        return self.clean_data
    
    def get_analytics(self) -> Optional[Dict[str, Any]]:
        """Get the analytics results"""
        return self.analytics


def process_admission_pdf(pdf_source: str, output_dir: str = "outputs", 
                         export_filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to process a single PDF through the complete pipeline
    
    Args:
        pdf_source: Path or URL to PDF file
        output_dir: Directory for output files
        export_filename: Optional custom filename for Excel export
        
    Returns:
        Dict containing results and file paths
    """
    pipeline = DUAdmissionPipeline(output_dir)
    return pipeline.process_pdf(pdf_source, export_filename)


def batch_process_pdfs(pdf_sources: list, output_dir: str = "outputs") -> Dict[str, Any]:
    """
    Process multiple PDFs in batch
    
    Args:
        pdf_sources: List of PDF paths or URLs
        output_dir: Directory for output files
        
    Returns:
        Dict containing batch processing results
    """
    logger.info(f"🔄 Starting batch processing of {len(pdf_sources)} PDFs")
    
    results = {
        'batch_summary': {
            'total_pdfs': len(pdf_sources),
            'successful': 0,
            'failed': 0,
            'start_time': datetime.now().isoformat()
        },
        'individual_results': {},
        'combined_data': None,
        'combined_analytics': None
    }
    
    all_dataframes = []
    
    for i, pdf_source in enumerate(pdf_sources, 1):
        logger.info(f"📄 Processing PDF {i}/{len(pdf_sources)}: {pdf_source}")
        
        try:
            pipeline = DUAdmissionPipeline(output_dir)
            result = pipeline.process_pdf(pdf_source, f"batch_{i}_analysis.xlsx")
            
            if result['success']:
                results['batch_summary']['successful'] += 1
                all_dataframes.append(pipeline.get_clean_dataframe())
            else:
                results['batch_summary']['failed'] += 1
            
            results['individual_results'][f'pdf_{i}'] = result
            
        except Exception as e:
            logger.error(f"❌ Failed to process PDF {i}: {str(e)}")
            results['batch_summary']['failed'] += 1
            results['individual_results'][f'pdf_{i}'] = {
                'success': False,
                'error': str(e)
            }
    
    # Combine all successful dataframes
    if all_dataframes:
        logger.info("🔗 Combining all successful extractions...")
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Export combined results
        combined_pipeline = DUAdmissionPipeline(output_dir)
        combined_pipeline.clean_data = combined_df
        combined_pipeline.analytics = generate_analytics_summary(combined_df)
        
        combined_export_path = export_to_excel(
            combined_df, 
            "Combined_Batch_Analysis.xlsx",
            output_dir
        )
        
        results['combined_data'] = combined_df.shape
        results['combined_analytics'] = combined_pipeline.analytics
        results['combined_export_path'] = combined_export_path
        
        logger.info(f"✅ Combined analysis exported to: {combined_export_path}")
    
    results['batch_summary']['end_time'] = datetime.now().isoformat()
    logger.info(f"🎉 Batch processing completed: {results['batch_summary']['successful']} successful, {results['batch_summary']['failed']} failed")
    
    return results
