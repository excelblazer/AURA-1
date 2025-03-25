import pandas as pd
import re
import os
import pdfplumber
from typing import Dict, List, Any
from datetime import datetime

def extract_from_payroll(file_path: str) -> Dict[str, Any]:
    """
    Extract data from Payroll Detail Sheet (PDF)
    
    Args:
        file_path: Path to the payroll PDF file
        
    Returns:
        Dictionary containing extracted tutor and payroll data
    """
    tutors_data = []
    
    try:
        # Use pdfplumber to extract text from PDF
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                
                # Extract tutor information using regex patterns
                tutor_pattern = r"([A-Za-z\s]+)\s+(\w+|Virtual)\s+(\d+\.?\d*)\s+(\d+\.?\d*)"
                for match in re.finditer(tutor_pattern, text):
                    tutor_name, assignment, regular_hours, total_hours = match.groups()
                    
                    # Extract day-wise clock in/out if available
                    clock_data = extract_clock_data(text, tutor_name)
                    
                    tutors_data.append({
                        "name": tutor_name.strip(),
                        "assignment": assignment,
                        "regular_hours": float(regular_hours),
                        "total_hours": float(total_hours),
                        "clock_data": clock_data
                    })
    
        return {
            "tutors": tutors_data,
            "extraction_date": datetime.now(),
            "source_file": os.path.basename(file_path)
        }
    
    except Exception as e:
        print(f"Error extracting data from payroll: {str(e)}")
        return {
            "tutors": [],
            "extraction_date": datetime.now(),
            "source_file": os.path.basename(file_path),
            "error": str(e)
        }

def extract_clock_data(text: str, tutor_name: str) -> List[Dict[str, Any]]:
    """Extract clock in/out data for a tutor from text"""
    # This would need a more sophisticated regex based on actual PDF structure
    clock_pattern = r"(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}\s*[AP]M)\s+-\s+(\d{1,2}:\d{2}\s*[AP]M)"
    clock_data = []
    
    for match in re.finditer(clock_pattern, text):
        date_str, clock_in, clock_out = match.groups()
        try:
            date = datetime.strptime(date_str, "%m/%d/%Y").date()
            clock_data.append({
                "date": date,
                "clock_in": clock_in,
                "clock_out": clock_out
            })
        except ValueError:
            # Skip invalid dates
            continue
    
    return clock_data

def extract_from_feedback(file_path: str) -> Dict[str, Any]:
    """
    Extract data from Daily Feedback Sheet (Excel)
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Dictionary containing extracted student and session data
    """
    try:
        # Load Excel file with pandas
        xls = pd.ExcelFile(file_path)
        
        # Extract main sheet with student overview
        overview_df = pd.read_excel(xls, sheet_name=0)
        
        # Process student data
        students_data = process_student_overview(overview_df)
        
        # Extract student tabs (individual sheets)
        student_sessions = []
        for sheet_name in xls.sheet_names:
            # Skip the main overview sheet
            if sheet_name.lower() in ['sheet1', 'overview', 'main']:
                continue
                
            # Process individual student sheet
            student_df = pd.read_excel(xls, sheet_name=sheet_name)
            sessions = process_student_sheet(student_df, sheet_name)
            student_sessions.extend(sessions)
        
        return {
            "students": students_data,
            "sessions": student_sessions,
            "extraction_date": datetime.now(),
            "source_file": os.path.basename(file_path)
        }
    
    except Exception as e:
        print(f"Error extracting data from feedback sheet: {str(e)}")
        return {
            "students": [],
            "sessions": [],
            "extraction_date": datetime.now(),
            "source_file": os.path.basename(file_path),
            "error": str(e)
        }

def process_student_overview(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Process the main overview sheet to extract student information"""
    students = []
    
    # Clean up column names
    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
    
    # Required columns based on SOP
    required_cols = ['student_name', 'grade', 'subjects', 'caretaker_name', 
                     'phone_number', 'email_address', 'tutor_assigned']
    
    # Check if required columns exist (different naming conventions possible)
    col_mapping = {}
    for req_col in required_cols:
        for col in df.columns:
            if req_col in col:
                col_mapping[req_col] = col
                break
    
    # Process each row
    for _, row in df.iterrows():
        # Skip rows with no student name
        if pd.isnull(row.get(col_mapping.get('student_name', ''))):
            continue
            
        # Get color code (status) if available
        status = 'unknown'
        if 'color_code' in df.columns:
            status_val = row['color_code']
            if pd.notnull(status_val):
                if status_val.lower() == 'green':
                    status = 'active'
                elif status_val.lower() == 'red':
                    status = 'terminated'
                elif status_val.lower() == 'yellow':
                    status = 'initial_call'
                elif status_val.lower() == 'orange':
                    status = 'assign_tutor'
                elif status_val.lower() == 'pink':
                    status = 'on_hold'
                elif status_val.lower() == 'blue':
                    status = 'language_request'
        
        # Extract student name components
        full_name = str(row.get(col_mapping.get('student_name', ''))).strip()
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Build student record
        student = {
            "id": generate_student_id(full_name),
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "grade": row.get(col_mapping.get('grade', ''), ''),
            "subjects": row.get(col_mapping.get('subjects', ''), ''),
            "caregiver_name": row.get(col_mapping.get('caretaker_name', ''), ''),
            "caregiver_phone": row.get(col_mapping.get('phone_number', ''), ''),
            "caregiver_email": row.get(col_mapping.get('email_address', ''), ''),
            "tutor_assigned": row.get(col_mapping.get('tutor_assigned', ''), ''),
            "status": status,
            # Case number may be in different columns
            "case_number": extract_case_number(row),
            "tutor_start_date": extract_start_date(row)
        }
        
        students.append(student)
    
    return students

def extract_case_number(row: pd.Series) -> str:
    """Extract case number from row, checking various possible column names"""
    possible_columns = ['case', 'case_number', 'case_#', 'case_no', 'case_num']
    
    for col in possible_columns:
        for actual_col in row.index:
            if col in actual_col.lower():
                val = row[actual_col]
                if pd.notnull(val):
                    return str(val).strip()
    
    return ''

def extract_start_date(row: pd.Series) -> str:
    """Extract tutor start date from row, checking various possible column names"""
    possible_columns = ['start_date', 'tutor_start_date', 'tutoring_start']
    
    for col in possible_columns:
        for actual_col in row.index:
            if col in actual_col.lower():
                val = row[actual_col]
                if pd.notnull(val):
                    # Try to parse as date
                    try:
                        if isinstance(val, str):
                            return datetime.strptime(val, "%m/%d/%Y").strftime("%m/%d/%Y")
                        elif isinstance(val, datetime):
                            return val.strftime("%m/%d/%Y")
                        else:
                            return str(val)
                    except:
                        return str(val)
    
    return ''

def generate_student_id(name: str) -> str:
    """Generate a consistent student ID based on name"""
    import hashlib
    return hashlib.md5(name.lower().encode()).hexdigest()[:8]

def process_student_sheet(df: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
    """Process individual student sheet to extract tutoring sessions"""
    sessions = []
    
    # Clean column names
    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
    
    # Expected columns (adjust based on actual data)
    date_col = next((col for col in df.columns if 'date' in col.lower()), None)
    time_in_col = next((col for col in df.columns if 'time_in' in col.lower() or 'clock_in' in col.lower()), None)
    time_out_col = next((col for col in df.columns if 'time_out' in col.lower() or 'clock_out' in col.lower()), None)
    hours_col = next((col for col in df.columns if 'hours' in col.lower() or 'duration' in col.lower()), None)
    goal_col = next((col for col in df.columns if 'goal' in col.lower() or 'objective' in col.lower() or 'notes' in col.lower()), None)
    
    # Skip if essential columns missing
    if not all([date_col, time_in_col, time_out_col, hours_col]):
        return []
    
    # Process each row
    for _, row in df.iterrows():
        # Skip rows with no date
        if pd.isnull(row[date_col]):
            continue
        
        # Try to parse date
        try:
            session_date = parse_date(row[date_col])
        except:
            # Skip rows with invalid dates
            continue
        
        # Try to parse times
        try:
            time_in = parse_time(row[time_in_col])
            time_out = parse_time(row[time_out_col])
        except:
            # Use empty strings if time parsing fails
            time_in = str(row[time_in_col]) if pd.notnull(row[time_in_col]) else ''
            time_out = str(row[time_out_col]) if pd.notnull(row[time_out_col]) else ''
        
        # Get hours
        hours = float(row[hours_col]) if pd.notnull(row[hours_col]) else 0
        
        # Get goal/notes if available
        goal = str(row[goal_col]) if goal_col and pd.notnull(row[goal_col]) else ''
        
        # Check for no-show
        is_no_show = False
        for col in df.columns:
            if 'no_show' in col.lower() or 'noshow' in col.lower():
                val = row[col]
                if pd.notnull(val) and (val == True or str(val).lower() in ['yes', 'y', 'true', '1']):
                    is_no_show = True
                    break
        
        # Create session record
        session = {
            "student_id": generate_student_id(sheet_name),
            "student_name": sheet_name,
            "date": session_date,
            "time_in": time_in,
            "time_out": time_out,
            "hours": hours,
            "goal": goal,
            "is_no_show": is_no_show
        }
        
        sessions.append(session)
    
    return sessions

def parse_date(date_val) -> str:
    """Parse date from various formats"""
    if isinstance(date_val, datetime):
        return date_val.strftime("%m/%d/%Y")
    elif isinstance(date_val, str):
        # Try different date formats
        for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"]:
            try:
                return datetime.strptime(date_val, fmt).strftime("%m/%d/%Y")
            except ValueError:
                continue
    
    # If all parsing attempts fail, return as string
    return str(date_val)

def parse_time(time_val) -> str:
    """Parse time from various formats"""
    if isinstance(time_val, datetime):
        return time_val.strftime("%I:%M %p")
    elif isinstance(time_val, str):
        # Try different time formats
        for fmt in ["%I:%M %p", "%H:%M", "%I:%M%p", "%I:%M"]:
            try:
                return datetime.strptime(time_val, fmt).strftime("%I:%M %p")
            except ValueError:
                continue
    
    # If all parsing attempts fail, return as string
    return str(time_val)