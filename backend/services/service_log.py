import os
import xlsxwriter
from datetime import datetime
from typing import Dict, Any, List, Optional

def generate_agency_service_log(month: str, year: int, feedback_data: Dict = None) -> str:
    """
    Generate Agency Service Log for the specified month and year
    
    Args:
        month (str): Month name
        year (int): Year
        feedback_data (Dict): Data extracted from the Daily Feedback Sheet
        
    Returns:
        str: Path to the generated service log file
    """
    # Create output directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    # In a real app, this data would come from the database
    # For demonstration, we'll use a simplified example
    if feedback_data is None:
        # Mock data for demonstration
        session_data = [
            {
                "student_id": "S001", 
                "student_name": "Doe, John", 
                "tutor_name": "Smith, Jane",
                "case_number": "CN12345",
                "session_date": datetime(year, {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}.get(month, 1), 5),
                "start_time": "3:00 PM",
                "end_time": "5:00 PM",
                "hours": 2.0,
                "service_type": "Academic Tutoring",
                "goal": "Improve math skills",
                "notes": "Worked on algebra equations"
            },
            {
                "student_id": "S001", 
                "student_name": "Doe, John", 
                "tutor_name": "Smith, Jane",
                "case_number": "CN12345",
                "session_date": datetime(year, {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}.get(month, 1), 12),
                "start_time": "4:00 PM",
                "end_time": "6:00 PM",
                "hours": 2.0,
                "service_type": "Academic Tutoring",
                "goal": "Reading comprehension",
                "notes": "Reviewed reading strategies"
            },
            {
                "student_id": "S002", 
                "student_name": "Johnson, Emma", 
                "tutor_name": "Brown, Michael",
                "case_number": "CN67890",
                "session_date": datetime(year, {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}.get(month, 1), 8),
                "start_time": "2:30 PM",
                "end_time": "4:00 PM",
                "hours": 1.5,
                "service_type": "Academic Tutoring",
                "goal": "Improve writing skills",
                "notes": "Worked on essay structure"
            }
        ]
    else:
        # Extract session data from feedback data
        # This is a placeholder - in a real app, you would
        # process the actual feedback data to get session details
        session_data = []
        for student in feedback_data.get('students', []):
            student_name = f"{student.get('last_name')}, {student.get('first_name')}"
            tutor_name = f"{student.get('tutor_last_name')}, {student.get('tutor_first_name')}"
            
            for session in student.get('sessions', []):
                session_data.append({
                    "student_id": student.get('id'),
                    "student_name": student_name,
                    "tutor_name": tutor_name,
                    "case_number": student.get('case_number'),
                    "session_date": session.get('date'),
                    "start_time": session.get('start_time'),
                    "end_time": session.get('end_time'),
                    "hours": session.get('hours', 0),
                    "service_type": "Academic Tutoring",
                    "goal": session.get('goal', ''),
                    "notes": session.get('feedback', '')
                })
    
    # Month as a number for file naming
    month_num = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 
                 'May': '05', 'June': '06', 'July': '07', 'August': '08', 
                 'September': '09', 'October': '10', 'November': '11', 'December': '12'}.get(month, '01')
    
    # Create Excel file
    filename = f"Client1_Gain_ServiceLog_{month}_{year}.xlsx"
    filepath = os.path.join("outputs", filename)
    
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet('Service Log')
    
    # Add header formats
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': '#E2EFDA'  # Light green
    })
    
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 16,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    cell_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    date_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'num_format': 'mm/dd/yyyy'
    })
    
    # Set column widths
    worksheet.set_column('A:A', 25)  # Student Name
    worksheet.set_column('B:B', 20)  # Case Number
    worksheet.set_column('C:C', 25)  # Tutor Name
    worksheet.set_column('D:D', 15)  # Date
    worksheet.set_column('E:E', 10)  # Start Time
    worksheet.set_column('F:F', 10)  # End Time
    worksheet.set_column('G:G', 10)  # Hours
    worksheet.set_column('H:H', 20)  # Service Type
    worksheet.set_column('I:I', 30)  # Goal
    worksheet.set_column('J:J', 40)  # Notes
    
    # Add title
    worksheet.merge_range('A1:J1', 'Client1 Agency Service Log', title_format)
    worksheet.merge_range('A2:J2', f'For the Month of {month} {year}')
    
    # Add headers at row 4
    headers = ['Student Name', 'Case Number', 'Tutor Name', 'Date', 'Start Time', 
               'End Time', 'Hours', 'Service Type', 'Goal', 'Notes']
    
    for col, header in enumerate(headers):
        worksheet.write(3, col, header, header_format)
    
    # Fill data starting at row 4
    row = 4
    total_hours = 0
    
    for session in session_data:
        worksheet.write(row, 0, session["student_name"], cell_format)
        worksheet.write(row, 1, session["case_number"], cell_format)
        worksheet.write(row, 2, session["tutor_name"], cell_format)
        
        # Handle date conversion if it's a string
        if isinstance(session["session_date"], str):
            try:
                date_obj = datetime.strptime(session["session_date"], "%Y-%m-%d")
            except ValueError:
                date_obj = datetime.now()  # Fallback
        else:
            date_obj = session["session_date"]
            
        worksheet.write(row, 3, date_obj, date_format)
        worksheet.write(row, 4, session["start_time"], cell_format)
        worksheet.write(row, 5, session["end_time"], cell_format)
        worksheet.write(row, 6, session["hours"], cell_format)
        worksheet.write(row, 7, session["service_type"], cell_format)
        worksheet.write(row, 8, session["goal"], cell_format)
        worksheet.write(row, 9, session["notes"], cell_format)
        
        total_hours += session["hours"]
        row += 1
    
    # Add summary section
    summary_row = row + 2
    worksheet.merge_range(f'A{summary_row}:C{summary_row}', 'Summary', workbook.add_format({'bold': True}))
    
    worksheet.merge_range(f'A{summary_row+1}:B{summary_row+1}', 'Total Students:')
    worksheet.write(f'C{summary_row+1}', len(set(session["student_id"] for session in session_data)))
    
    worksheet.merge_range(f'A{summary_row+2}:B{summary_row+2}', 'Total Sessions:')
    worksheet.write(f'C{summary_row+2}', len(session_data))
    
    worksheet.merge_range(f'A{summary_row+3}:B{summary_row+3}', 'Total Hours:')
    worksheet.write(f'C{summary_row+3}', total_hours)
    
    # Add signature section
    signature_row = summary_row + 5
    worksheet.merge_range(f'A{signature_row}:C{signature_row}', 'Agency Representative Signature:', workbook.add_format({'bold': True}))
    worksheet.merge_range(f'D{signature_row}:F{signature_row}', '_______________________')
    
    worksheet.merge_range(f'G{signature_row}:H{signature_row}', 'Date:', workbook.add_format({'bold': True}))
    worksheet.merge_range(f'I{signature_row}:J{signature_row}', '_______________________')
    
    # Close the workbook
    workbook.close()
    
    return filepath