# DU Admission Analyzer 🎓

A comprehensive, production-grade Python tool for extracting, cleaning, analyzing, and exporting Delhi University admission data from PDF files. Built with modularity and FastAPI integration in mind.

## 🌟 Features

- **📄 Robust PDF Extraction**: Multiple extraction methods (tabula-py, pdfplumber) with fallback mechanisms
- **🧹 Intelligent Data Cleaning**: Handles split rows, duplicate headers, column misalignment, and data type conversion
- **📊 Comprehensive Analytics**: Generate insights on seats by college, program, category, and more
- **📤 Multi-format Export**: Excel with multiple formatted sheets + CSV backup
- **🔄 Batch Processing**: Process multiple PDFs simultaneously
- **🚀 FastAPI Ready**: Modular design for easy web API integration
- **🐍 Production-grade**: Clean code, error handling, logging, and documentation

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Module Documentation](#module-documentation)
- [FastAPI Integration](#fastapi-integration)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## 🔧 Installation

### Prerequisites
- Python 3.8+
- Java (for tabula-py PDF extraction)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages
- pandas>=2.0.0
- tabula-py>=2.8.0
- openpyxl>=3.1.0
- xlsxwriter>=3.1.0
- requests>=2.31.0
- matplotlib>=3.7.0
- seaborn>=0.12.0
- pdfplumber>=0.10.0

## 🚀 Quick Start

### Command Line Usage

```bash
# Process a single PDF
python main.py "https://admission.uod.ac.in/userfiles/downloads/25082025_VacantSeats_UG_Spot_Round.pdf"

# Process with custom output directory
python main.py "path/to/your/pdf.pdf" --output-dir "my_outputs"

# Batch processing
python main.py --batch "pdf1.pdf" "pdf2.pdf" "pdf3.pdf"
```

### Python Script Usage

```python
from src import process_admission_pdf

# Simple one-liner processing
results = process_admission_pdf("path/to/pdf.pdf")

if results['success']:
    print(f"✅ Processed {results['data_shape'][0]} rows")
    print(f"📁 Excel: {results['files']['excel']}")
    print(f"📄 CSV: {results['files']['csv']}")
```

### Jupyter Notebook

Open `demo_notebook.ipynb` for an interactive demonstration with visualizations and step-by-step processing.

## 📖 Usage Examples

### 1. Basic Processing

```python
from src.pipeline import process_admission_pdf

# Process DU admission PDF
pdf_url = "https://admission.uod.ac.in/userfiles/downloads/25082025_VacantSeats_UG_Spot_Round.pdf"
results = process_admission_pdf(pdf_url)

# Access results
print(f"Total seats: {results['analytics']['overview']['total_seats']}")
print(f"Total colleges: {results['analytics']['overview']['total_colleges']}")
```

### 2. Step-by-Step Processing

```python
from src.pdf_extractor import extract_pdf
from src.data_cleaner import clean_data
from src.analytics import generate_analytics_summary
from src.excel_exporter import export_to_excel

# Step 1: Extract
raw_data = extract_pdf("path/to/pdf.pdf")

# Step 2: Clean
clean_data_df = clean_data(raw_data)

# Step 3: Analyze
analytics = generate_analytics_summary(clean_data_df)

# Step 4: Export
excel_path = export_to_excel(clean_data_df, "analysis.xlsx")
```

### 3. Custom Analytics

```python
from src.analytics import AdmissionAnalytics

# Create analytics object
analytics = AdmissionAnalytics(clean_data_df)

# Get specific insights
college_analysis = analytics._analyze_by_college()
program_analysis = analytics._analyze_by_program()
category_analysis = analytics._analyze_by_category()

# Generate visualizations
visualizations = analytics.create_visualizations()
```

### 4. Batch Processing

```python
from src.pipeline import batch_process_pdfs

pdf_list = [
    "round1.pdf",
    "round2.pdf", 
    "round3.pdf"
]

batch_results = batch_process_pdfs(pdf_list, "batch_outputs")
print(f"Processed {batch_results['batch_summary']['successful']} PDFs successfully")
```

## 📚 Module Documentation

### Core Modules

#### `src.pipeline`
- **`process_admission_pdf()`**: Main function for single PDF processing
- **`batch_process_pdfs()`**: Batch processing multiple PDFs
- **`DUAdmissionPipeline`**: Complete pipeline class

#### `src.pdf_extractor`
- **`extract_pdf()`**: Extract tables from PDF using multiple methods
- **`PDFExtractor`**: Advanced extraction class with fallback mechanisms

#### `src.data_cleaner`
- **`clean_data()`**: Clean and normalize extracted data
- **`DataCleaner`**: Comprehensive cleaning pipeline

#### `src.analytics`
- **`generate_analytics_summary()`**: Generate comprehensive analytics
- **`AdmissionAnalytics`**: Advanced analytics and visualization class

#### `src.excel_exporter`
- **`export_to_excel()`**: Export to formatted Excel with multiple sheets
- **`ExcelExporter`**: Advanced Excel export with formatting

### Configuration

Edit `src/config.py` to customize:
- Column mappings
- Category names
- PDF extraction settings
- Export formats

## 🌐 FastAPI Integration

The modular design makes FastAPI integration straightforward:

```python
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import tempfile
import os
from src.pipeline import process_admission_pdf

app = FastAPI(title="DU Admission Analyzer API")

@app.post("/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Process the PDF
        results = process_admission_pdf(tmp_path)
        
        if results['success']:
            return {
                "status": "success",
                "data_shape": results['data_shape'],
                "analytics": results['analytics']['overview'],
                "insights": results['analytics']['insights'][:3],
                "download_url": f"/download/{os.path.basename(results['files']['excel'])}"
            }
        else:
            return {"status": "error", "message": results['error']}
    
    finally:
        # Clean up temp file
        os.unlink(tmp_path)

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"outputs/{filename}"
    return FileResponse(file_path, filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 📁 Project Structure

```
du_admission_analyzer/
├── src/                          # Core modules
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration settings
│   ├── pdf_extractor.py         # PDF extraction logic
│   ├── data_cleaner.py          # Data cleaning pipeline
│   ├── analytics.py             # Analytics and insights
│   ├── excel_exporter.py        # Excel export functionality
│   └── pipeline.py              # Main processing pipeline
├── data/                        # Downloaded PDFs (auto-created)
├── outputs/                     # Generated outputs (auto-created)
├── main.py                      # Command-line interface
├── demo_notebook.ipynb          # Interactive demonstration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔧 Advanced Configuration

### PDF Extraction Settings

Modify `src/config.py` to adjust PDF extraction parameters:

```python
PDF_EXTRACTION_SETTINGS = {
    'pages': 'all',
    'multiple_tables': True,
    'lattice': True,  # For grid-based tables
    'java_options': ["-Xmx2048m"]  # Increase memory
}
```

### Custom Column Mappings

```python
EXPECTED_COLUMNS = [
    'S.NO.',
    'NAME OF THE COLLEGE',
    'NAME OF THE PROGRAM',
    'UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD'
]

CATEGORY_NAMES = {
    'UR': 'Unreserved (General)',
    'OBC': 'Other Backward Class',
    # ... add more mappings
}
```

## 🐛 Common Issues & Solutions

### Issue: PDF Extraction Fails
**Solution**: The tool tries multiple extraction methods. If all fail:
1. Ensure the PDF is not password-protected
2. Check if the PDF contains actual tables (not images)
3. Try a different PDF extraction tool manually

### Issue: Column Misalignment
**Solution**: The cleaner automatically detects and fixes common alignment issues. For persistent issues:
1. Check the `_fix_column_alignment()` method in `data_cleaner.py`
2. Add custom logic for your specific PDF format

### Issue: Java Memory Errors
**Solution**: Increase Java heap size in `config.py`:
```python
'java_options': ["-Xmx4096m"]  # Increase to 4GB
```

## 📊 Sample Output

The tool generates:

1. **Excel file** with multiple sheets:
   - Raw Data
   - Analytics Summary
   - College-wise Analysis
   - Program-wise Analysis
   - Category-wise Analysis
   - Top Performers

2. **CSV backup** of clean data

3. **Analytics dictionary** with:
   - Overview statistics
   - Detailed breakdowns
   - Key insights
   - Top performers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for Delhi University admission data analysis
- Uses tabula-py for PDF table extraction
- Pandas for data manipulation
- xlsxwriter for Excel formatting

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Common Issues](#-common-issues--solutions) section
2. Review the demo notebook for examples
3. Open an issue on GitHub with detailed error information

---

**Made with ❤️ for the DU community**
