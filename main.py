"""
Main Entry Point for DU Admission Analyzer
Can be used as a standalone script or imported as a module
"""

import sys
import os
import argparse
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline import process_admission_pdf, batch_process_pdfs


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description="DU Admission Analyzer - Extract and analyze Delhi University admission data from PDFs"
    )
    
    parser.add_argument(
        'pdf_source',
        help='Path or URL to the PDF file to process'
    )
    
    parser.add_argument(
        '--output-dir',
        default='outputs',
        help='Directory to save output files (default: outputs)'
    )
    
    parser.add_argument(
        '--filename',
        help='Custom filename for Excel export'
    )
    
    parser.add_argument(
        '--batch',
        nargs='+',
        help='Process multiple PDFs in batch mode'
    )
    
    args = parser.parse_args()
    
    try:
        if args.batch:
            # Batch processing mode
            print("🔄 Starting batch processing...")
            results = batch_process_pdfs(args.batch, args.output_dir)
            
            print(f"\n📊 Batch Processing Summary:")
            print(f"   Total PDFs: {results['batch_summary']['total_pdfs']}")
            print(f"   Successful: {results['batch_summary']['successful']}")
            print(f"   Failed: {results['batch_summary']['failed']}")
            
            if results.get('combined_export_path'):
                print(f"   Combined Analysis: {results['combined_export_path']}")
        
        else:
            # Single PDF processing
            print(f"🚀 Processing PDF: {args.pdf_source}")
            results = process_admission_pdf(
                args.pdf_source,
                args.output_dir,
                args.filename
            )
            
            if results['success']:
                print(f"\n✅ Processing successful!")
                print(f"📊 Data Shape: {results['data_shape']}")
                print(f"📁 Excel Export: {results['files']['excel']}")
                print(f"📄 CSV Backup: {results['files']['csv']}")
                
                # Print key insights
                insights = results['analytics'].get('insights', [])
                if insights:
                    print(f"\n🔍 Key Insights:")
                    for i, insight in enumerate(insights[:5], 1):
                        print(f"   {i}. {insight}")
            else:
                print(f"❌ Processing failed: {results['error']}")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️ Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
