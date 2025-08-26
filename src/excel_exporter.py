"""
Excel Export Module for DU Admission Analyzer
Handles exporting data and analytics to Excel files with multiple sheets
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from .config import EXCEL_SHEETS, DEFAULT_OUTPUT_DIR
from .analytics import AdvancedAdmissionAnalytics, generate_analytics_summary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExcelExporter:
    """
    Comprehensive Excel export class with multiple sheets and formatting
    """
    
    def __init__(self, output_dir: str = DEFAULT_OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_to_excel(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Export DataFrame and analytics to Excel with multiple sheets
        
        Args:
            df: Clean DataFrame with admission data
            filename: Optional custom filename
            
        Returns:
            str: Path to the exported Excel file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"DU_Admission_Analysis_{timestamp}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        logger.info(f"Starting Excel export to: {filepath}")
        
        # Clean data for Excel export - handle NaN/Inf values
        df_clean = df.copy()
        df_clean = df_clean.fillna('')  # Replace NaN with empty string
        df_clean = df_clean.replace([float('inf'), float('-inf')], 0)  # Replace Inf with 0
        
        # Generate analytics
        analytics = AdvancedAdmissionAnalytics(df_clean)
        analytics_data = analytics.get_complete_analysis()
        
        # Create Excel writer with nan_inf_to_errors option
        with pd.ExcelWriter(filepath, engine='xlsxwriter', 
                          engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
            # Get workbook and add formats
            workbook = writer.book
            self._add_formats(workbook)
            
            # Sheet 1: Raw Data
            self._export_raw_data(df_clean, writer, workbook)
            
            # Sheet 2: Analytics Summary
            self._export_analytics_summary(analytics_data, writer, workbook)
            
            # Convert new analytics format to legacy format for Excel export
            legacy_analytics = self._convert_to_legacy_format(analytics_data)
            
            # Sheet 3: College-wise Analysis
            self._export_college_analysis(legacy_analytics.get('college_wise', {}), writer, workbook)
            
            # Sheet 4: Program-wise Analysis
            self._export_program_analysis(legacy_analytics.get('program_wise', {}), writer, workbook)
            
            # Sheet 5: Category-wise Analysis
            self._export_category_analysis(legacy_analytics.get('category_wise', {}), writer, workbook)
            
            # Sheet 6: Top Performers
            self._export_top_performers(legacy_analytics.get('top_performers', {}), writer, workbook)
        
        logger.info(f"✅ Excel export completed: {filepath}")
        return filepath
    
    def _convert_to_legacy_format(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert new AdvancedAdmissionAnalytics format to legacy format for Excel export"""
        
        # If it's already in legacy format, return as is
        if 'college_wise' in analytics_data:
            return analytics_data
        
        # Extract overview data safely
        overview_data = analytics_data.get('overview', {})
        if not isinstance(overview_data, dict):
            overview_data = {}
        
        # Convert new format to legacy format
        legacy_format = {
            'overview': {
                'total_colleges': overview_data.get('total_colleges', 0),
                'total_programs': overview_data.get('total_programs', 0),
                'total_seats': overview_data.get('total_seats', 0),
                'avg_seats_per_program': overview_data.get('avg_seats_per_program', 0),
                'avg_seats_per_college': overview_data.get('avg_seats_per_college', 0)
            },
            'totals': overview_data.get('categories', {}),
            'college_wise': pd.DataFrame(),
            'program_wise': pd.DataFrame(),
            'category_wise': pd.DataFrame(),
            'top_performers': {},
            'insights': self._extract_insights_safely(analytics_data.get('insights', []))
        }
        
        # Convert college analysis safely
        try:
            if 'colleges' in analytics_data and isinstance(analytics_data['colleges'], dict):
                college_data = analytics_data['colleges'].get('college_stats', [])
                if college_data and isinstance(college_data, list):
                    df = pd.DataFrame(college_data)
                    if 'NAME OF THE COLLEGE' in df.columns:
                        legacy_format['college_wise'] = df.set_index('NAME OF THE COLLEGE')
                    
                    # Top performers from college analysis
                    top_colleges = analytics_data['colleges'].get('top_by_seats', [])
                    if top_colleges and isinstance(top_colleges, list):
                        df_top = pd.DataFrame(top_colleges)
                        if 'NAME OF THE COLLEGE' in df_top.columns:
                            legacy_format['top_performers']['top_colleges_by_seats'] = df_top.set_index('NAME OF THE COLLEGE')
        except Exception as e:
            logger.warning(f"Error converting college data: {e}")
        
        # Convert program analysis safely
        try:
            if 'programs' in analytics_data and isinstance(analytics_data['programs'], dict):
                program_data = analytics_data['programs'].get('program_stats', [])
                if program_data and isinstance(program_data, list):
                    df = pd.DataFrame(program_data)
                    if 'NAME OF THE PROGRAM' in df.columns:
                        legacy_format['program_wise'] = df.set_index('NAME OF THE PROGRAM')
                    
                    # Top performers from program analysis
                    top_programs = analytics_data['programs'].get('top_by_seats', [])
                    if top_programs and isinstance(top_programs, list):
                        df_top = pd.DataFrame(top_programs)
                        if 'NAME OF THE PROGRAM' in df_top.columns:
                            legacy_format['top_performers']['top_programs_by_seats'] = df_top.set_index('NAME OF THE PROGRAM')
        except Exception as e:
            logger.warning(f"Error converting program data: {e}")
        
        # Convert category analysis safely
        try:
            if 'categories' in analytics_data and isinstance(analytics_data['categories'], dict):
                category_data = analytics_data['categories']
                if 'totals' in category_data and isinstance(category_data['totals'], dict):
                    # Convert to DataFrame format expected by excel exporter
                    category_list = []
                    for cat, total in category_data['totals'].items():
                        percentage = category_data.get('percentages', {}).get(cat, 0)
                        category_list.append({
                            'Category': cat, 
                            'Total_Seats': total, 
                            'Percentage': percentage
                        })
                    if category_list:
                        legacy_format['category_wise'] = pd.DataFrame(category_list).set_index('Category')
        except Exception as e:
            logger.warning(f"Error converting category data: {e}")
        
        return legacy_format
    
    def _extract_insights_safely(self, insights_data):
        """Safely extract insights as list of strings"""
        if not insights_data:
            return []
        
        result = []
        try:
            if isinstance(insights_data, list):
                for insight in insights_data:
                    if isinstance(insight, dict):
                        text = insight.get('description', insight.get('title', str(insight)))
                    else:
                        text = str(insight)
                    result.append(text)
            else:
                result.append(str(insights_data))
        except Exception as e:
            logger.warning(f"Error extracting insights: {e}")
            result.append("Error processing insights")
        
        return result
    
    def _add_formats(self, workbook):
        """Add formatting styles to the workbook"""
        self.header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#4472C4',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        self.title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': '#2F5597',
            'align': 'center'
        })
        
        self.number_format = workbook.add_format({
            'num_format': '#,##0',
            'align': 'center',
            'border': 1
        })
        
        self.text_format = workbook.add_format({
            'text_wrap': True,
            'align': 'left',
            'valign': 'top',
            'border': 1
        })
        
        self.summary_format = workbook.add_format({
            'bold': True,
            'bg_color': '#E7E6E6',
            'border': 1,
            'align': 'center'
        })
    
    def _export_raw_data(self, df: pd.DataFrame, writer, workbook):
        """Export raw data to the first sheet"""
        sheet_name = EXCEL_SHEETS['raw_data']
        df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2)
        
        worksheet = writer.sheets[sheet_name]
        
        # Add title
        worksheet.merge_range('A1:J1', 'DU Admission Data - Raw Data', self.title_format)
        
        # Format headers
        for col_num, value in enumerate(df.columns):
            worksheet.write(2, col_num, value, self.header_format)
        
        # Format data
        for row_num in range(len(df)):
            for col_num, column in enumerate(df.columns):
                cell_value = df.iloc[row_num, col_num]
                
                if column in ['UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']:
                    worksheet.write(row_num + 3, col_num, cell_value, self.number_format)
                else:
                    worksheet.write(row_num + 3, col_num, cell_value, self.text_format)
        
        # Adjust column widths
        self._adjust_column_widths(worksheet, df)
    
    def _export_analytics_summary(self, analytics_data: Dict[str, Any], writer, workbook):
        """Export analytics summary to dedicated sheet"""
        sheet_name = EXCEL_SHEETS['analytics']
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Add title
        worksheet.merge_range('A1:D1', 'Analytics Summary', self.title_format)
        
        row = 3
        
        # Overview section
        worksheet.write(row, 0, 'OVERVIEW', self.header_format)
        row += 1
        
        overview = analytics_data.get('overview', {})
        for key, value in overview.items():
            worksheet.write(row, 0, key.replace('_', ' ').title(), self.text_format)
            # Handle different value types safely
            if isinstance(value, (dict, list)):
                # Convert complex types to string representation
                cell_value = str(len(value)) if isinstance(value, (dict, list)) else str(value)
            elif isinstance(value, (int, float)):
                cell_value = value
            else:
                cell_value = str(value)
            worksheet.write(row, 1, cell_value, self.number_format if isinstance(cell_value, (int, float)) else self.text_format)
            row += 1
        
        row += 2
        
        # Totals section
        worksheet.write(row, 0, 'CATEGORY TOTALS', self.header_format)
        row += 1
        
        totals = analytics_data.get('totals', {})
        for key, value in totals.items():
            worksheet.write(row, 0, key.replace('_', ' ').title(), self.text_format)
            # Ensure value is a simple type for Excel
            cell_value = value if isinstance(value, (int, float)) else str(value)
            worksheet.write(row, 1, cell_value, self.number_format if isinstance(cell_value, (int, float)) else self.text_format)
            row += 1
        
        row += 2
        
        # Insights section
        worksheet.write(row, 0, 'KEY INSIGHTS', self.header_format)
        row += 1
        
        insights = analytics_data.get('insights', [])
        for insight in insights:
            # Handle insight format - could be string or dict
            if isinstance(insight, dict):
                insight_text = insight.get('description', str(insight))
            else:
                insight_text = str(insight)
            worksheet.write(row, 0, insight_text, self.text_format)
            row += 1
        
        # Adjust column widths
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 15)
    
    def _export_college_analysis(self, college_data: pd.DataFrame, writer, workbook):
        """Export college-wise analysis"""
        sheet_name = EXCEL_SHEETS['college_wise']
        
        # Reset index to include college names as a column
        college_df = college_data.reset_index()
        college_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2)
        
        worksheet = writer.sheets[sheet_name]
        
        # Add title
        worksheet.merge_range('A1:L1', 'College-wise Analysis', self.title_format)
        
        # Format headers
        for col_num, value in enumerate(college_df.columns):
            worksheet.write(2, col_num, value, self.header_format)
        
        # Format data
        for row_num in range(len(college_df)):
            for col_num, column in enumerate(college_df.columns):
                cell_value = college_df.iloc[row_num, col_num]
                
                if column == 'NAME OF THE COLLEGE':
                    worksheet.write(row_num + 3, col_num, cell_value, self.text_format)
                else:
                    worksheet.write(row_num + 3, col_num, cell_value, self.number_format)
        
        self._adjust_column_widths(worksheet, college_df)
    
    def _export_program_analysis(self, program_data: pd.DataFrame, writer, workbook):
        """Export program-wise analysis"""
        sheet_name = EXCEL_SHEETS['program_wise']
        
        # Reset index to include program names as a column
        program_df = program_data.reset_index()
        program_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2)
        
        worksheet = writer.sheets[sheet_name]
        
        # Add title
        worksheet.merge_range('A1:L1', 'Program-wise Analysis', self.title_format)
        
        # Format headers
        for col_num, value in enumerate(program_df.columns):
            worksheet.write(2, col_num, value, self.header_format)
        
        # Format data
        for row_num in range(len(program_df)):
            for col_num, column in enumerate(program_df.columns):
                cell_value = program_df.iloc[row_num, col_num]
                
                if column == 'NAME OF THE PROGRAM':
                    worksheet.write(row_num + 3, col_num, cell_value, self.text_format)
                else:
                    worksheet.write(row_num + 3, col_num, cell_value, self.number_format)
        
        self._adjust_column_widths(worksheet, program_df)
    
    def _export_category_analysis(self, category_data: pd.DataFrame, writer, workbook):
        """Export category-wise analysis"""
        sheet_name = EXCEL_SHEETS['category_wise']
        category_data.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2)
        
        worksheet = writer.sheets[sheet_name]
        
        # Add title
        worksheet.merge_range('A1:D1', 'Category-wise Analysis', self.title_format)
        
        # Format headers
        for col_num, value in enumerate(category_data.columns):
            worksheet.write(2, col_num, value, self.header_format)
        
        # Format data
        for row_num in range(len(category_data)):
            for col_num, column in enumerate(category_data.columns):
                cell_value = category_data.iloc[row_num, col_num]
                
                if column in ['Total_Seats']:
                    worksheet.write(row_num + 3, col_num, cell_value, self.number_format)
                elif column == 'Percentage':
                    percentage_format = workbook.add_format({'num_format': '0.00%', 'align': 'center', 'border': 1})
                    # Convert percentage value to decimal for Excel
                    try:
                        percentage_value = float(str(cell_value)) / 100
                        worksheet.write(row_num + 3, col_num, percentage_value, percentage_format)
                    except (ValueError, TypeError):
                        worksheet.write(row_num + 3, col_num, cell_value, self.text_format)
                else:
                    worksheet.write(row_num + 3, col_num, cell_value, self.text_format)
        
        self._adjust_column_widths(worksheet, category_data)
    
    def _export_top_performers(self, top_performers: Dict[str, pd.DataFrame], writer, workbook):
        """Export top performers analysis"""
        sheet_name = 'Top Performers'
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Add title
        worksheet.merge_range('A1:F1', 'Top Performers Analysis', self.title_format)
        
        row = 3
        
        for section_name, data in top_performers.items():
            # Section header
            section_title = section_name.replace('_', ' ').title()
            worksheet.write(row, 0, section_title, self.header_format)
            row += 1
            
            # Reset index to include names as a column
            section_df = data.reset_index()
            
            # Write headers
            for col_num, value in enumerate(section_df.columns):
                worksheet.write(row, col_num, value, self.header_format)
            
            row += 1
            
            # Write data
            for data_row in range(len(section_df)):
                for col_num, column in enumerate(section_df.columns):
                    cell_value = section_df.iloc[data_row, col_num]
                    
                    if isinstance(cell_value, (int, float)):
                        worksheet.write(row, col_num, cell_value, self.number_format)
                    else:
                        worksheet.write(row, col_num, cell_value, self.text_format)
                
                row += 1
            
            row += 2  # Add space between sections
        
        # Adjust column widths
        worksheet.set_column('A:A', 40)
        worksheet.set_column('B:F', 15)
    
    def _adjust_column_widths(self, worksheet, df: pd.DataFrame):
        """Adjust column widths based on content"""
        for col_num, column in enumerate(df.columns):
            # Calculate max width needed
            max_width = max(
                len(str(column)),
                df[column].astype(str).str.len().max() if not df.empty else 0
            )
            
            # Set reasonable limits
            width = min(max(max_width + 2, 10), 50)
            worksheet.set_column(col_num, col_num, width)


def export_to_excel(df: pd.DataFrame, filename: Optional[str] = None, output_dir: str = DEFAULT_OUTPUT_DIR) -> str:
    """
    Convenience function for Excel export
    
    Args:
        df: Clean DataFrame with admission data
        filename: Optional custom filename
        output_dir: Output directory
        
    Returns:
        str: Path to exported file
    """
    exporter = ExcelExporter(output_dir)
    return exporter.export_to_excel(df, filename)
