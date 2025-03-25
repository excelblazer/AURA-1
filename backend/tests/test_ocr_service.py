"""
Tests for the OCR service.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path

from services.ocr_service import OCRService


@pytest.fixture
def ocr_service():
    """Create an OCR service instance for testing."""
    with patch('services.ocr_service.OCRService._initialize_ocr_engines') as mock_init:
        service = OCRService()
        # Mock available engines
        service.available_engines = ['tesseract']
        service.has_pdf2image = True
        service.has_pypdf2 = True
        return service


@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        # Write a minimal PDF content
        temp_file.write(b"%PDF-1.4\n%Sample PDF for testing OCR service")
        temp_path = temp_file.name
    
    yield temp_path
    
    # Clean up after test
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_ocr_service_initialization():
    """Test OCR service initialization."""
    with patch('services.ocr_service.OCRService._initialize_ocr_engines') as mock_init:
        service = OCRService()
        mock_init.assert_called_once()


def test_extract_text_from_pdf_pypdf2(ocr_service, sample_pdf):
    """Test extracting text from PDF using PyPDF2."""
    # Mock PyPDF2 extraction
    mock_text = "This is sample text extracted from the PDF using PyPDF2."
    
    with patch('PyPDF2.PdfReader') as mock_reader:
        # Configure the mock
        mock_page = MagicMock()
        mock_page.extract_text.return_value = mock_text
        mock_reader.return_value.pages = [mock_page]
        
        # Call the method
        result = ocr_service.extract_text_from_pdf(sample_pdf)
        
        # Verify the result
        assert result.strip() == mock_text
        mock_page.extract_text.assert_called_once()


def test_extract_text_from_pdf_tesseract(ocr_service, sample_pdf):
    """Test extracting text from PDF using Tesseract OCR."""
    # Mock PyPDF2 to return insufficient text
    with patch('PyPDF2.PdfReader') as mock_reader:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Short text"  # Too short to pass the threshold
        mock_reader.return_value.pages = [mock_page]
        
        # Mock pdf2image and pytesseract
        with patch('pdf2image.convert_from_path') as mock_convert:
            with patch('pytesseract.image_to_string') as mock_image_to_string:
                # Configure the mocks
                mock_image = MagicMock()
                mock_convert.return_value = [mock_image]
                mock_image_to_string.return_value = "This is sample text extracted using Tesseract OCR."
                
                # Call the method
                result = ocr_service.extract_text_from_pdf(sample_pdf)
                
                # Verify the result
                assert "Tesseract OCR" in result
                mock_convert.assert_called_once_with(sample_pdf)
                mock_image_to_string.assert_called_once_with(mock_image)


def test_extract_text_from_pdf_textract(ocr_service, sample_pdf):
    """Test extracting text from PDF using AWS Textract."""
    # Set up the OCR service to use Textract
    ocr_service.available_engines = ['textract']
    ocr_service.has_textract = True
    ocr_service.textract_client = MagicMock()
    
    # Mock Textract response
    mock_response = {
        'Blocks': [
            {'BlockType': 'LINE', 'Text': 'This is sample text'},
            {'BlockType': 'LINE', 'Text': 'extracted using AWS Textract.'}
        ]
    }
    ocr_service.textract_client.detect_document_text.return_value = mock_response
    
    # Call the method
    result = ocr_service.extract_text_from_pdf(sample_pdf)
    
    # Verify the result
    assert "This is sample text" in result
    assert "extracted using AWS Textract" in result
    ocr_service.textract_client.detect_document_text.assert_called_once()


def test_extract_text_from_nonexistent_pdf(ocr_service):
    """Test extracting text from a non-existent PDF file."""
    with pytest.raises(FileNotFoundError):
        ocr_service.extract_text_from_pdf("/path/to/nonexistent.pdf")


def test_parse_payroll_data(ocr_service, sample_pdf):
    """Test parsing payroll data from a PDF."""
    # Mock extract_text_from_pdf to return sample payroll text
    sample_payroll_text = """
    Period: January 1-15, 2023
    
    Tutor ID: ABC123
    Name: John Doe
    Total Hours: 10.5
    Rate: $25.00
    
    01/01/2023 9:00 AM - 11:30 AM 2.5 hours
    01/03/2023 2:00 PM - 4:00 PM 2.0 hours
    01/05/2023 10:00 AM - 12:00 PM 2.0 hours
    01/10/2023 1:00 PM - 5:00 PM 4.0 hours
    
    Tutor ID: XYZ789
    Name: Jane Smith
    Total Hours: 8.0
    Rate: $30.00
    
    01/02/2023 10:00 AM - 12:00 PM 2.0 hours
    01/04/2023 3:00 PM - 5:00 PM 2.0 hours
    01/09/2023 9:00 AM - 1:00 PM 4.0 hours
    """
    
    with patch.object(ocr_service, 'extract_text_from_pdf', return_value=sample_payroll_text):
        # Call the method
        result = ocr_service.parse_payroll_data(sample_pdf)
        
        # Verify the result
        assert result["period"] == "January 1-15, 2023"
        assert len(result["tutors"]) == 2
        
        # Check first tutor
        assert result["tutors"][0]["id"] == "ABC123"
        assert result["tutors"][0]["name"] == "John Doe"
        assert result["tutors"][0]["total_hours"] == 10.5
        assert result["tutors"][0]["hourly_rate"] == 25.0
        assert len(result["tutors"][0]["sessions"]) == 4
        
        # Check second tutor
        assert result["tutors"][1]["id"] == "XYZ789"
        assert result["tutors"][1]["name"] == "Jane Smith"
        assert result["tutors"][1]["total_hours"] == 8.0
        assert result["tutors"][1]["hourly_rate"] == 30.0
        assert len(result["tutors"][1]["sessions"]) == 3


def test_extract_table_from_pdf_textract(ocr_service, sample_pdf):
    """Test extracting a table from PDF using AWS Textract."""
    # Set up the OCR service to use Textract
    ocr_service.available_engines = ['textract']
    ocr_service.has_textract = True
    ocr_service.has_pdf2image = True
    ocr_service.textract_client = MagicMock()
    
    # Mock pdf2image
    with patch('pdf2image.convert_from_path') as mock_convert:
        mock_image = MagicMock()
        mock_convert.return_value = [mock_image]
        
        # Mock Textract response for table analysis
        mock_response = {
            'Blocks': [
                {
                    'BlockType': 'TABLE',
                    'Id': 'table1'
                },
                {
                    'BlockType': 'CELL',
                    'RowIndex': 1,
                    'ColumnIndex': 1,
                    'TableId': 'table1',
                    'Relationships': [
                        {
                            'Type': 'CHILD',
                            'Ids': ['word1']
                        }
                    ]
                },
                {
                    'BlockType': 'CELL',
                    'RowIndex': 1,
                    'ColumnIndex': 2,
                    'TableId': 'table1',
                    'Relationships': [
                        {
                            'Type': 'CHILD',
                            'Ids': ['word2']
                        }
                    ]
                },
                {
                    'BlockType': 'CELL',
                    'RowIndex': 2,
                    'ColumnIndex': 1,
                    'TableId': 'table1',
                    'Relationships': [
                        {
                            'Type': 'CHILD',
                            'Ids': ['word3']
                        }
                    ]
                },
                {
                    'BlockType': 'CELL',
                    'RowIndex': 2,
                    'ColumnIndex': 2,
                    'TableId': 'table1',
                    'Relationships': [
                        {
                            'Type': 'CHILD',
                            'Ids': ['word4']
                        }
                    ]
                },
                {
                    'BlockType': 'WORD',
                    'Id': 'word1',
                    'Text': 'Date'
                },
                {
                    'BlockType': 'WORD',
                    'Id': 'word2',
                    'Text': 'Hours'
                },
                {
                    'BlockType': 'WORD',
                    'Id': 'word3',
                    'Text': '01/01/2023'
                },
                {
                    'BlockType': 'WORD',
                    'Id': 'word4',
                    'Text': '2.5'
                }
            ]
        }
        ocr_service.textract_client.analyze_document.return_value = mock_response
        
        # Call the method
        result = ocr_service.extract_table_from_pdf(sample_pdf)
        
        # Verify the result
        assert len(result) == 2  # 2 rows
        assert len(result[0]) == 2  # 2 columns
        assert result[0][0] == 'Date'
        assert result[0][1] == 'Hours'
        assert result[1][0] == '01/01/2023'
        assert result[1][1] == '2.5'


def test_extract_table_from_pdf_tesseract(ocr_service, sample_pdf):
    """Test extracting a table from PDF using Tesseract OCR."""
    # Set up the OCR service to use Tesseract
    ocr_service.available_engines = ['tesseract']
    ocr_service.has_pdf2image = True
    
    # Mock pdf2image and pytesseract
    with patch('pdf2image.convert_from_path') as mock_convert:
        with patch('pytesseract.image_to_data', return_value=MagicMock()) as mock_image_to_data:
            # Configure the mocks
            mock_image = MagicMock()
            mock_convert.return_value = [mock_image]
            
            # Mock DataFrame-like result
            mock_df = MagicMock()
            mock_df.iterrows.return_value = [
                (0, MagicMock(line_num=1, text='Date')),
                (1, MagicMock(line_num=1, text='Hours')),
                (2, MagicMock(line_num=2, text='01/01/2023')),
                (3, MagicMock(line_num=2, text='2.5'))
            ]
            mock_image_to_data.return_value = mock_df
            
            # Call the method
            with patch.object(ocr_service, '_extract_table_with_tesseract') as mock_extract:
                mock_extract.return_value = [['Date', 'Hours'], ['01/01/2023', '2.5']]
                result = ocr_service.extract_table_from_pdf(sample_pdf)
                
                # Verify the result
                assert len(result) == 2
                assert result[0][0] == 'Date'
                assert result[0][1] == 'Hours'
                assert result[1][0] == '01/01/2023'
                assert result[1][1] == '2.5'
