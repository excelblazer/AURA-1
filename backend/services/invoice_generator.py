import os
import xlsxwriter
from datetime import datetime
from typing import Dict, Any, List, Optional

def generate_invoice(month: str, year: int, payroll_data: Dict = None, feedback_data: Dict = None) -> str:
    """
    Generate Invoice for all students in a specific month
    
    Args:
        month (str): Month name
        year (int): Year
        payroll_data (Dict): Data extracted from the Payroll Detail Sheet
        feedback_data (Dict): Data extracted from the Daily Feedback Sheet
        
    Returns:
        str: Path to the generated invoice file
    """
    # Create output directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    # In a real app, this data would come from the database
    # For demonstration, we'll use a simplified example
    if payroll_data is None or feedback_data is None:
        # Mock data for demonstration
        student_sessions = [
            {"student_id": "S001", "student_first_name": "John", "student_last_name": "Doe", "hours": 8.25},
            {"student_id": "S002", "student_first_name": "Emma", "student_last_name": "Johnson", "hours": 6.5},
            {"student_id": "S003", "student_first_name": "Michael", "student_last_name": "Smith", "hours": 10.0},
            {"student_id": "S004", "student_first_name": "Olivia", "student_last_name": "Brown", "hours": 7.75},
            {"student_id": "S005", "student_first_name": "William", "student_last_name": "Davis", "hours": 9.25}
        ]
    else:
        # Extract student sessions from feedback data
        # This is a placeholder - in a real app, you would
        # process the actual feedback data to get session hours
        student_sessions = []
        for student in feedback_data.get('students', []):
            total_hours = sum(session.get('hours', 0) for session in student.get('sessions', []))
            student_sessions.append({
                "student_id": student.get('id'),
                "student_first_name": student.get('first_name'),
                "student_last_name": student.get('last_name'),
                "hours": total_hours
            })
    
    # Month as a number for file naming
    month_num = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 
                 'May': '05', 'June': '06', 'July': '07', 'August': '08', 
                 'September': '09', 'October': '10', 'November': '11', 'December': '12'}.get(month, '01')
    
    # Create Excel file
    filename = f"Client1_Invoice_{month}_{year}.xlsx"
    filepath = os.path.join("outputs", filename)
    
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet('Invoice')
    
    # Add header formats
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': '#DDEBF7'  # Light blue
    })
    
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 16,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    date_format = workbook.add_format({
        'align': 'right',
        'valign': 'vcenter',
        'font_size': 11
    })
    
    cell_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    amount_format = workbook.add_format({
        'align': 'right',
        'valign': 'vcenter',
        'border': 1,
        'num_format': '$#,##0.00'
    })
    
    total_format = workbook.add_format({
        'align': 'right',
        'valign': 'vcenter',
        'bold': True,
        'border': 1,
        'num_format': '$#,##0.00'
    })
    
    # Set column widths
    worksheet.set_column('A:A', 30)  # Student Name
    worksheet.set_column('B:B', 15)  # Hours
    worksheet.set_column('C:C', 15)  # Rate
    worksheet.set_column('D:D', 15)  # Total
    
    # Add title and date
    worksheet.merge_range('A1:D1', 'Client1 Invoice', title_format)
    worksheet.merge_range('A2:D2', f'For the Month of {month} {year}', date_format)
    
    # Add company information
    worksheet.merge_range('A4:B4', 'Client1', workbook.add_format({'bold': True}))
    worksheet.merge_range('A5:B5', '123 Education Street')
    worksheet.merge_range('A6:B6', 'Learning City, ST 12345')
    worksheet.merge_range('A7:B7', 'Phone: (555) 123-4567')
    
    # Add invoice details
    worksheet.merge_range('C4:D4', f'Invoice #: C1-{month_num}{str(year)[-2:]}', workbook.add_format({'align': 'right'}))
    worksheet.merge_range('C5:D5', f'Date: {datetime.now().strftime("%m/%d/%Y")}', workbook.add_format({'align': 'right'}))
    worksheet.merge_range('C6:D6', f'Due Date: {datetime.now().strftime("%m/%d/%Y")}', workbook.add_format({'align': 'right'}))
    
    # Add headers at row 9
    headers = ['Student Name', 'Hours', 'Rate', 'Total']
    for col, header in enumerate(headers):
        worksheet.write(9, col, header, header_format)
    
    # Fill data starting at row 10
    row = 10
    total_amount = 0
    hourly_rate = 55  # From SOP
    
    for student in student_sessions:
        student_name = f"{student['student_last_name']}, {student['student_first_name']}"
        hours = student['hours']
        amount = hours * hourly_rate
        total_amount += amount
        
        worksheet.write(row, 0, student_name, cell_format)
        worksheet.write(row, 1, hours, cell_format)
        worksheet.write(row, 2, hourly_rate, amount_format)
        worksheet.write(row, 3, amount, amount_format)
        
        row += 1
    
    # Add total row
    worksheet.merge_range(f'A{row+1}:C{row+1}', 'Total', workbook.add_format({'bold': True, 'align': 'right', 'border': 1}))
    worksheet.write(row+1, 3, total_amount, total_format)
    
    # Add payment information
    payment_row = row + 4
    worksheet.merge_range(f'A{payment_row}:D{payment_row}', 'Payment Information', workbook.add_format({'bold': True}))
    worksheet.merge_range(f'A{payment_row+1}:D{payment_row+1}', 'Please make checks payable to Client1')
    worksheet.merge_range(f'A{payment_row+2}:D{payment_row+2}', 'Bank Transfer: Bank Name, Account #: 123456789, Routing #: 987654321')
    
    # Add notes section
    notes_row = payment_row + 4
    worksheet.merge_range(f'A{notes_row}:D{notes_row}', 'Notes', workbook.add_format({'bold': True}))
    worksheet.merge_range(f'A{notes_row+1}:D{notes_row+3}', 'Thank you for your business. This invoice covers tutoring services provided during the month specified above.', 
                          workbook.add_format({'text_wrap': True}))
    
    # Close the workbook
    workbook.close()
    
    # In a real app, you would convert to PDF here
    # pdf_filepath = os.path.join("outputs", f"Client1_Invoice_{month}_{year}.pdf")
    # convert_to_pdf(filepath, pdf_filepath)
    # return pdf_filepath
    
    return filepath

def convert_to_pdf(excel_path, pdf_path):
    """
    Convert an Excel document to PDF
    In a real application, you would use a library like xlsxwriter with a PDF converter or an external service
    
    For this example, we'll just pass
    """
    # Placeholder for PDF conversion functionality
    pass