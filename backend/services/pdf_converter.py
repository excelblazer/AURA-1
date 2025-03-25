"""
PDF Conversion Service

This module provides functionality to convert various document types to PDF format.
Supports conversion from Word documents (.docx), Excel spreadsheets (.xlsx), and other formats.
"""

import logging
import subprocess
import os
from pathlib import Path
from typing import Union, Optional, List

logger = logging.getLogger(__name__)

class PDFConverter:
    """
    Service for converting various document types to PDF format.
    
    Supports:
    - Word documents (.docx) to PDF
    - Excel spreadsheets (.xlsx) to PDF
    - Text files (.txt) to PDF
    - HTML files (.html) to PDF
    """
    
    def __init__(self):
        """Initialize the PDF converter service."""
        logger.info("PDF converter service initialized")
    
    def convert_to_pdf(
        self,
        input_file: Union[str, Path],
        output_file: Optional[Union[str, Path]] = None
    ) -> Path:
        """
        Convert a document to PDF format.
        
        Args:
            input_file: Path to the input file
            output_file: Path to the output PDF file (optional)
            
        Returns:
            Path: Path to the generated PDF file
            
        Raises:
            ValueError: If the input file format is not supported
            FileNotFoundError: If the input file does not exist
        """
        input_path = Path(input_file)
        
        # Check if input file exists
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Determine output path if not provided
        if output_file is None:
            output_path = input_path.with_suffix('.pdf')
        else:
            output_path = Path(output_file)
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert based on file extension
        file_extension = input_path.suffix.lower()
        
        if file_extension == '.docx':
            return self._convert_word_to_pdf(input_path, output_path)
        elif file_extension == '.xlsx':
            return self._convert_excel_to_pdf(input_path, output_path)
        elif file_extension == '.txt':
            return self._convert_text_to_pdf(input_path, output_path)
        elif file_extension == '.html':
            return self._convert_html_to_pdf(input_path, output_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _convert_word_to_pdf(self, input_path: Path, output_path: Path) -> Path:
        """
        Convert a Word document to PDF.
        
        Args:
            input_path: Path to the Word document
            output_path: Path to the output PDF file
            
        Returns:
            Path: Path to the generated PDF file
        """
        logger.info(f"Converting Word document to PDF: {input_path} -> {output_path}")
        
        try:
            # Using python-docx-pdf library (requires docx2pdf)
            from docx2pdf import convert
            convert(str(input_path), str(output_path))
            logger.info(f"Successfully converted Word document to PDF: {output_path}")
            return output_path
        except ImportError:
            logger.warning("docx2pdf not installed, falling back to alternative method")
            # Alternative method using LibreOffice (if available)
            return self._convert_using_libreoffice(input_path, output_path)
    
    def _convert_excel_to_pdf(self, input_path: Path, output_path: Path) -> Path:
        """
        Convert an Excel spreadsheet to PDF.
        
        Args:
            input_path: Path to the Excel spreadsheet
            output_path: Path to the output PDF file
            
        Returns:
            Path: Path to the generated PDF file
        """
        logger.info(f"Converting Excel spreadsheet to PDF: {input_path} -> {output_path}")
        
        try:
            # Using xlwings for Excel to PDF conversion
            import xlwings as xw
            app = xw.App(visible=False)
            book = app.books.open(str(input_path))
            book.api.ExportAsFixedFormat(0, str(output_path))
            book.close()
            app.quit()
            logger.info(f"Successfully converted Excel spreadsheet to PDF: {output_path}")
            return output_path
        except ImportError:
            logger.warning("xlwings not installed, falling back to alternative method")
            # Alternative method using LibreOffice (if available)
            return self._convert_using_libreoffice(input_path, output_path)
    
    def _convert_text_to_pdf(self, input_path: Path, output_path: Path) -> Path:
        """
        Convert a text file to PDF.
        
        Args:
            input_path: Path to the text file
            output_path: Path to the output PDF file
            
        Returns:
            Path: Path to the generated PDF file
        """
        logger.info(f"Converting text file to PDF: {input_path} -> {output_path}")
        
        try:
            # Using ReportLab for text to PDF conversion
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            c = canvas.Canvas(str(output_path), pagesize=letter)
            text = input_path.read_text(encoding='utf-8')
            
            # Simple text rendering
            y = 750  # Starting Y position
            for line in text.split('\n'):
                if y < 50:  # New page if we're at the bottom
                    c.showPage()
                    y = 750
                c.drawString(50, y, line)
                y -= 15  # Move down for next line
            
            c.save()
            logger.info(f"Successfully converted text file to PDF: {output_path}")
            return output_path
        except ImportError:
            logger.warning("ReportLab not installed, falling back to alternative method")
            # Alternative method
            return self._convert_using_html_bridge(input_path, output_path)
    
    def _convert_html_to_pdf(self, input_path: Path, output_path: Path) -> Path:
        """
        Convert an HTML file to PDF.
        
        Args:
            input_path: Path to the HTML file
            output_path: Path to the output PDF file
            
        Returns:
            Path: Path to the generated PDF file
        """
        logger.info(f"Converting HTML file to PDF: {input_path} -> {output_path}")
        
        try:
            # Using WeasyPrint for HTML to PDF conversion
            from weasyprint import HTML
            HTML(filename=str(input_path)).write_pdf(str(output_path))
            logger.info(f"Successfully converted HTML file to PDF: {output_path}")
            return output_path
        except ImportError:
            logger.warning("WeasyPrint not installed, falling back to alternative method")
            # Alternative method using wkhtmltopdf (if available)
            return self._convert_using_wkhtmltopdf(input_path, output_path)
    
    def _convert_using_libreoffice(self, input_path: Path, output_path: Path) -> Path:
        """
        Convert a document to PDF using LibreOffice (if available).
        
        Args:
            input_path: Path to the input document
            output_path: Path to the output PDF file
            
        Returns:
            Path: Path to the generated PDF file
            
        Raises:
            RuntimeError: If conversion fails
        """
        logger.info(f"Attempting conversion using LibreOffice: {input_path}")
        
        # Determine LibreOffice command based on OS
        if os.name == 'nt':  # Windows
            libreoffice_cmd = 'soffice.exe'
        else:  # Linux/Mac
            libreoffice_cmd = 'libreoffice'
        
        try:
            # Run LibreOffice in headless mode to convert the document
            cmd = [
                libreoffice_cmd,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(output_path.parent),
                str(input_path)
            ]
            
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            # LibreOffice creates the PDF with the same name as the input file
            temp_pdf = input_path.with_suffix('.pdf')
            
            # Rename to the desired output name if different
            if temp_pdf != output_path:
                os.rename(temp_pdf, output_path)
            
            logger.info(f"Successfully converted document using LibreOffice: {output_path}")
            return output_path
        
        except subprocess.CalledProcessError as e:
            logger.error(f"LibreOffice conversion failed: {e.stderr}")
            raise RuntimeError(f"Failed to convert document using LibreOffice: {e}")
        
        except FileNotFoundError:
            logger.error("LibreOffice not found in system path")
            raise RuntimeError("LibreOffice not found. Please install LibreOffice or ensure it's in your system path.")
    
    def _convert_using_wkhtmltopdf(self, input_path: Path, output_path: Path) -> Path:
        """
        Convert an HTML file to PDF using wkhtmltopdf (if available).
        
        Args:
            input_path: Path to the HTML file
            output_path: Path to the output PDF file
            
        Returns:
            Path: Path to the generated PDF file
            
        Raises:
            RuntimeError: If conversion fails
        """
        logger.info(f"Attempting conversion using wkhtmltopdf: {input_path}")
        
        try:
            # Run wkhtmltopdf to convert HTML to PDF
            cmd = [
                'wkhtmltopdf',
                str(input_path),
                str(output_path)
            ]
            
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            logger.info(f"Successfully converted HTML using wkhtmltopdf: {output_path}")
            return output_path
        
        except subprocess.CalledProcessError as e:
            logger.error(f"wkhtmltopdf conversion failed: {e.stderr}")
            raise RuntimeError(f"Failed to convert HTML using wkhtmltopdf: {e}")
        
        except FileNotFoundError:
            logger.error("wkhtmltopdf not found in system path")
            raise RuntimeError("wkhtmltopdf not found. Please install wkhtmltopdf or ensure it's in your system path.")
    
    def _convert_using_html_bridge(self, input_path: Path, output_path: Path) -> Path:
        """
        Convert a text file to PDF by first converting to HTML, then to PDF.
        
        Args:
            input_path: Path to the text file
            output_path: Path to the output PDF file
            
        Returns:
            Path: Path to the generated PDF file
        """
        logger.info(f"Converting text to PDF via HTML bridge: {input_path}")
        
        # Create a temporary HTML file
        html_path = input_path.with_suffix('.html')
        
        try:
            # Read the text file
            text = input_path.read_text(encoding='utf-8')
            
            # Create a simple HTML version
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Converted Document</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        pre {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <pre>{text}</pre>
</body>
</html>"""
            
            # Write the HTML file
            html_path.write_text(html_content, encoding='utf-8')
            
            # Convert the HTML to PDF
            result = self._convert_html_to_pdf(html_path, output_path)
            
            return result
            
        finally:
            # Clean up the temporary HTML file
            if html_path.exists():
                html_path.unlink()


# Create a singleton instance
pdf_converter = PDFConverter()
