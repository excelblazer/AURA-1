"""
OCR Service Module

This module provides functionality to extract text and structured data from PDF documents
using Optical Character Recognition (OCR) techniques.
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import tempfile
import json

logger = logging.getLogger(__name__)

class OCRService:
    """
    Service for extracting text and structured data from PDF documents using OCR.
    
    This service provides methods to:
    1. Extract raw text from PDF documents
    2. Parse payroll information from PDF documents
    3. Extract tabular data from PDF documents
    """
    
    def __init__(self):
        """Initialize the OCR service."""
        logger.info("OCR service initialized")
        self._initialize_ocr_engines()
    
    def _initialize_ocr_engines(self):
        """Initialize OCR engines based on available libraries."""
        self.available_engines = []
        
        # Check for pytesseract
        try:
            import pytesseract
            self.available_engines.append('tesseract')
            logger.info("Tesseract OCR engine initialized")
        except ImportError:
            logger.warning("pytesseract not installed, Tesseract OCR engine unavailable")
        
        # Check for pdf2image (required for PDF processing)
        try:
            import pdf2image
            self.has_pdf2image = True
            logger.info("pdf2image library initialized")
        except ImportError:
            self.has_pdf2image = False
            logger.warning("pdf2image not installed, PDF to image conversion unavailable")
        
        # Check for PyPDF2 (for text extraction from PDF)
        try:
            import PyPDF2
            self.has_pypdf2 = True
            logger.info("PyPDF2 library initialized")
        except ImportError:
            self.has_pypdf2 = False
            logger.warning("PyPDF2 not installed, basic PDF text extraction unavailable")
        
        # Check for AWS Textract integration
        self.has_textract = False
        try:
            import boto3
            # Check if AWS credentials are available
            if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
                self.textract_client = boto3.client('textract')
                self.has_textract = True
                self.available_engines.append('textract')
                logger.info("AWS Textract OCR engine initialized")
            else:
                logger.warning("AWS credentials not found, Textract OCR engine unavailable")
        except ImportError:
            logger.warning("boto3 not installed, AWS Textract OCR engine unavailable")
        
        if not self.available_engines:
            logger.warning("No OCR engines available. Install pytesseract or configure AWS Textract.")
    
    def extract_text_from_pdf(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract raw text from a PDF document.
        
        Args:
            pdf_path: Path to the PDF document
            
        Returns:
            str: Extracted text from the PDF
            
        Raises:
            ValueError: If no OCR engines are available
            FileNotFoundError: If the PDF file does not exist
        """
        pdf_path = Path(pdf_path)
        
        # Check if file exists
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Check if OCR engines are available
        if not self.available_engines and not self.has_pypdf2:
            raise ValueError("No OCR engines or PDF text extraction libraries available")
        
        # Try basic text extraction first (if PyPDF2 is available)
        extracted_text = ""
        if self.has_pypdf2:
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(reader.pages)):
                        page = reader.pages[page_num]
                        extracted_text += page.extract_text() + "\n\n"
                
                # If we got meaningful text, return it
                if len(extracted_text.strip()) > 100:  # Arbitrary threshold
                    logger.info(f"Successfully extracted text from PDF using PyPDF2: {pdf_path}")
                    return extracted_text
                else:
                    logger.info("Basic text extraction yielded insufficient results, trying OCR")
            except Exception as e:
                logger.warning(f"Error extracting text with PyPDF2: {e}")
        
        # If basic extraction failed or yielded insufficient results, try OCR
        if 'tesseract' in self.available_engines and self.has_pdf2image:
            try:
                import pytesseract
                from pdf2image import convert_from_path
                
                logger.info(f"Extracting text from PDF using Tesseract OCR: {pdf_path}")
                
                # Convert PDF to images
                images = convert_from_path(pdf_path)
                
                # Extract text from each image
                full_text = ""
                for i, image in enumerate(images):
                    text = pytesseract.image_to_string(image)
                    full_text += text + "\n\n"
                
                logger.info(f"Successfully extracted text from PDF using Tesseract OCR: {pdf_path}")
                return full_text
                
            except Exception as e:
                logger.warning(f"Error extracting text with Tesseract OCR: {e}")
        
        # If Tesseract failed or is unavailable, try AWS Textract
        if 'textract' in self.available_engines:
            try:
                logger.info(f"Extracting text from PDF using AWS Textract: {pdf_path}")
                
                with open(pdf_path, 'rb') as file:
                    file_bytes = file.read()
                
                response = self.textract_client.detect_document_text(Document={'Bytes': file_bytes})
                
                # Extract text from Textract response
                full_text = ""
                for item in response['Blocks']:
                    if item['BlockType'] == 'LINE':
                        full_text += item['Text'] + "\n"
                
                logger.info(f"Successfully extracted text from PDF using AWS Textract: {pdf_path}")
                return full_text
                
            except Exception as e:
                logger.warning(f"Error extracting text with AWS Textract: {e}")
        
        # If we got here, all methods failed
        if extracted_text:
            logger.warning("All OCR methods failed, returning basic extracted text")
            return extracted_text
        else:
            raise RuntimeError(f"Failed to extract text from PDF: {pdf_path}")
    
    def parse_payroll_data(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse payroll information from a PDF document.
        
        Args:
            pdf_path: Path to the PDF document
            
        Returns:
            dict: Structured payroll data extracted from the PDF
        """
        logger.info(f"Parsing payroll data from PDF: {pdf_path}")
        
        # Extract raw text from PDF
        raw_text = self.extract_text_from_pdf(pdf_path)
        
        # Parse payroll data from the extracted text
        payroll_data = self._parse_payroll_text(raw_text)
        
        logger.info(f"Successfully parsed payroll data from PDF: {pdf_path}")
        return payroll_data
    
    def _parse_payroll_text(self, text: str) -> Dict[str, Any]:
        """
        Parse payroll information from extracted text.
        
        Args:
            text: Raw text extracted from a payroll PDF
            
        Returns:
            dict: Structured payroll data
        """
        # Initialize payroll data structure
        payroll_data = {
            "period": None,
            "tutors": []
        }
        
        # Extract payroll period
        period_match = re.search(r'Period[:\s]+([A-Za-z0-9\s,]+)', text)
        if period_match:
            payroll_data["period"] = period_match.group(1).strip()
        
        # Extract tutor information
        # This is a simplified example - actual implementation would be more robust
        tutor_sections = re.split(r'Tutor ID[:\s]+', text)[1:]
        
        for section in tutor_sections:
            tutor = {}
            
            # Extract tutor ID
            id_match = re.search(r'^([A-Z0-9]+)', section)
            if id_match:
                tutor["id"] = id_match.group(1).strip()
            
            # Extract tutor name
            name_match = re.search(r'Name[:\s]+([A-Za-z\s,]+)', section)
            if name_match:
                tutor["name"] = name_match.group(1).strip()
            
            # Extract total hours
            hours_match = re.search(r'Total Hours[:\s]+([\d.]+)', section)
            if hours_match:
                tutor["total_hours"] = float(hours_match.group(1))
            
            # Extract hourly rate
            rate_match = re.search(r'Rate[:\s]+\$([\d.]+)', section)
            if rate_match:
                tutor["hourly_rate"] = float(rate_match.group(1))
            
            # Extract sessions
            tutor["sessions"] = []
            session_matches = re.finditer(
                r'(\d{1,2}/\d{1,2}/\d{2,4})\s+(\d{1,2}:\d{2}\s*[AP]M)\s*-\s*(\d{1,2}:\d{2}\s*[AP]M)\s+([\d.]+)\s+hours',
                section
            )
            
            for match in session_matches:
                session = {
                    "date": match.group(1),
                    "start_time": match.group(2),
                    "end_time": match.group(3),
                    "hours": float(match.group(4))
                }
                tutor["sessions"].append(session)
            
            # Add tutor to payroll data
            if tutor.get("id") and tutor.get("name"):
                payroll_data["tutors"].append(tutor)
        
        return payroll_data
    
    def extract_table_from_pdf(
        self,
        pdf_path: Union[str, Path],
        page_number: int = 0
    ) -> List[List[str]]:
        """
        Extract tabular data from a PDF document.
        
        Args:
            pdf_path: Path to the PDF document
            page_number: Page number to extract table from (0-indexed)
            
        Returns:
            list: Extracted table as a list of rows, where each row is a list of cell values
        """
        logger.info(f"Extracting table from PDF page {page_number}: {pdf_path}")
        
        # Check if AWS Textract is available (best for table extraction)
        if 'textract' in self.available_engines:
            try:
                return self._extract_table_with_textract(pdf_path, page_number)
            except Exception as e:
                logger.warning(f"Error extracting table with AWS Textract: {e}")
        
        # Fallback to Tesseract (less accurate for tables)
        if 'tesseract' in self.available_engines and self.has_pdf2image:
            try:
                return self._extract_table_with_tesseract(pdf_path, page_number)
            except Exception as e:
                logger.warning(f"Error extracting table with Tesseract: {e}")
        
        # If all methods failed
        raise RuntimeError(f"Failed to extract table from PDF: {pdf_path}")
    
    def _extract_table_with_textract(
        self,
        pdf_path: Union[str, Path],
        page_number: int = 0
    ) -> List[List[str]]:
        """
        Extract table from PDF using AWS Textract.
        
        Args:
            pdf_path: Path to the PDF document
            page_number: Page number to extract table from (0-indexed)
            
        Returns:
            list: Extracted table as a list of rows
        """
        logger.info(f"Extracting table with AWS Textract from page {page_number}: {pdf_path}")
        
        # Convert PDF page to image if needed
        if self.has_pdf2image:
            import tempfile
            from pdf2image import convert_from_path
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_image_path = temp_file.name
            
            # Convert specific page to image
            images = convert_from_path(pdf_path, first_page=page_number+1, last_page=page_number+1)
            if images:
                images[0].save(temp_image_path, 'PNG')
                
                # Use the image with Textract
                with open(temp_image_path, 'rb') as file:
                    file_bytes = file.read()
                
                try:
                    # Analyze document with table analysis
                    response = self.textract_client.analyze_document(
                        Document={'Bytes': file_bytes},
                        FeatureTypes=['TABLES']
                    )
                    
                    # Process Textract table results
                    tables = []
                    for block in response['Blocks']:
                        if block['BlockType'] == 'TABLE':
                            table = []
                            # Get all cells in this table
                            table_cells = [b for b in response['Blocks'] 
                                          if b['BlockType'] == 'CELL' and 
                                          b.get('TableId') == block['Id']]
                            
                            # Determine table dimensions
                            max_row = max(cell['RowIndex'] for cell in table_cells)
                            max_col = max(cell['ColumnIndex'] for cell in table_cells)
                            
                            # Initialize empty table
                            for _ in range(max_row):
                                table.append([''] * max_col)
                            
                            # Fill in cell values
                            for cell in table_cells:
                                row_idx = cell['RowIndex'] - 1
                                col_idx = cell['ColumnIndex'] - 1
                                
                                # Get cell content
                                cell_content = ''
                                if 'Relationships' in cell:
                                    for relationship in cell['Relationships']:
                                        if relationship['Type'] == 'CHILD':
                                            for child_id in relationship['Ids']:
                                                child_block = next((b for b in response['Blocks'] 
                                                                  if b['Id'] == child_id), None)
                                                if child_block and child_block['BlockType'] == 'WORD':
                                                    cell_content += child_block['Text'] + ' '
                                
                                table[row_idx][col_idx] = cell_content.strip()
                            
                            tables.append(table)
                    
                    # Clean up temporary image file
                    os.unlink(temp_image_path)
                    
                    if tables:
                        logger.info(f"Successfully extracted table with AWS Textract: {pdf_path}")
                        return tables[0]  # Return the first table found
                    else:
                        logger.warning(f"No tables found in PDF page {page_number}: {pdf_path}")
                        return []
                        
                except Exception as e:
                    # Clean up temporary image file
                    os.unlink(temp_image_path)
                    raise e
            else:
                logger.warning(f"Failed to convert PDF page {page_number} to image: {pdf_path}")
                return []
        else:
            logger.warning("pdf2image not installed, cannot extract table with Textract")
            return []
    
    def _extract_table_with_tesseract(
        self,
        pdf_path: Union[str, Path],
        page_number: int = 0
    ) -> List[List[str]]:
        """
        Extract table from PDF using Tesseract OCR.
        
        Args:
            pdf_path: Path to the PDF document
            page_number: Page number to extract table from (0-indexed)
            
        Returns:
            list: Extracted table as a list of rows
        """
        logger.info(f"Extracting table with Tesseract from page {page_number}: {pdf_path}")
        
        import pytesseract
        from pdf2image import convert_from_path
        
        # Convert specific page to image
        images = convert_from_path(pdf_path, first_page=page_number+1, last_page=page_number+1)
        
        if not images:
            logger.warning(f"Failed to convert PDF page {page_number} to image: {pdf_path}")
            return []
        
        # Use Tesseract's data table output format
        try:
            # Extract data in TSV format
            tsv_output = pytesseract.image_to_data(images[0], output_type=pytesseract.Output.DATAFRAME)
            
            # Process TSV to reconstruct table
            # This is a simplified approach - a real implementation would be more sophisticated
            lines = []
            current_line = []
            current_line_number = -1
            
            for _, row in tsv_output.iterrows():
                if row['text'].strip():
                    if row['line_num'] != current_line_number:
                        if current_line:
                            lines.append(current_line)
                        current_line = []
                        current_line_number = row['line_num']
                    
                    current_line.append(row['text'])
            
            if current_line:
                lines.append(current_line)
            
            # Convert lines to a table structure
            # This is a heuristic approach - assumes consistent column positions
            if not lines:
                return []
            
            # Determine number of columns based on the line with the most elements
            max_cols = max(len(line) for line in lines)
            
            # Create table with proper structure
            table = []
            for line in lines:
                # Pad line to have consistent number of columns
                padded_line = line + [''] * (max_cols - len(line))
                table.append(padded_line)
            
            logger.info(f"Successfully extracted table with Tesseract: {pdf_path}")
            return table
            
        except Exception as e:
            logger.warning(f"Error processing table with Tesseract: {e}")
            return []


# Create a singleton instance
ocr_service = OCRService()
