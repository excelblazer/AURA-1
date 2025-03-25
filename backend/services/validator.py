from typing import Dict, List, Any
from datetime import datetime, time, timedelta

def validate_data(payroll_data: Dict[str, Any], feedback_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate extracted data according to SOP requirements
    
    Args:
        payroll_data: Dictionary containing payroll data
        feedback_data: Dictionary containing feedback sheet data
        
    Returns:
        Dictionary with validation results and issues
    """
    issues = []
    
    # Run all validation checks
    issues.extend(validate_tutor_hours(payroll_data, feedback_data))
    issues.extend(validate_working_hours(feedback_data))
    issues.extend(validate_student_hours(feedback_data))
    issues.extend(validate_no_shows(feedback_data))
    
    return {
        "status": "invalid" if issues else "valid",
        "issues": issues,
        "validation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_issues": len(issues)
    }

def validate_tutor_hours(payroll_data: Dict[str, Any], feedback_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate that tutor hours in payroll match feedback data"""
    issues = []
    
    # Extract tutor names from feedback sessions
    feedback_tutors = {}
    for student in feedback_data.get("students", []):
        tutor_name = student.get("tutor_assigned", "").strip()
        if tutor_name:
            if tutor_name not in feedback_tutors:
                feedback_tutors[tutor_name] = {"students": [], "total_hours": 0}
            feedback_tutors[tutor_name]["students"].append(student.get("full_name"))
    
    # Sum hours by tutor from sessions
    for session in feedback_data.get("sessions", []):
        student_name = session.get("student_name", "")
        student = next((s for s in feedback_data.get("students", []) if s.get("full_name") == student_name), None)
        if student:
            tutor_name = student.get("tutor_assigned", "").strip()
            if tutor_name in feedback_tutors:
                feedback_tutors[tutor_name]["total_hours"] += session.get("hours", 0)
    
    # Compare with payroll data
    for tutor in payroll_data.get("tutors", []):
        tutor_name = tutor.get("name", "").strip()
        payroll_hours = tutor.get("total_hours", 0)
        
        if tutor_name in feedback_tutors:
            feedback_hours = feedback_tutors[tutor_name]["total_hours"]
            difference = abs(payroll_hours - feedback_hours)
            
            # Flag if difference exceeds 0.5 hours
            if difference > 0.5:
                issues.append({
                    "issue_type": "tutor_hours_mismatch",
                    "severity": "high" if difference > 2 else "medium",
                    "description": f"Tutor hours mismatch for {tutor_name}",
                    "details": {
                        "tutor_name": tutor_name,
                        "payroll_hours": payroll_hours,
                        "feedback_hours": feedback_hours,
                        "difference": difference,
                        "students": feedback_tutors[tutor_name]["students"]
                    }
                })
        else:
            # Tutor in payroll but not found in feedback data
            issues.append({
                "issue_type": "tutor_not_found",
                "severity": "high",
                "description": f"Tutor {tutor_name} found in payroll but not in feedback data",
                "details": {
                    "tutor_name": tutor_name,
                    "payroll_hours": payroll_hours
                }
            })
    
    # Check for tutors in feedback but not in payroll
    for tutor_name, data in feedback_tutors.items():
        if not any(t.get("name", "").strip() == tutor_name for t in payroll_data.get("tutors", [])):
            issues.append({
                "issue_type": "tutor_missing_from_payroll",
                "severity": "high",
                "description": f"Tutor {tutor_name} found in feedback data but not in payroll",
                "details": {
                    "tutor_name": tutor_name,
                    "feedback_hours": data["total_hours"],
                    "students": data["students"]
                }
            })
    
    return issues

def validate_working_hours(feedback_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate that tutoring sessions are within allowed working hours (10am to 7pm)"""
    issues = []
    
    work_start = time(10, 0)  # 10:00 AM
    work_end = time(19, 0)    # 7:00 PM
    
    for session in feedback_data.get("sessions", []):
        # Skip no-shows
        if session.get("is_no_show", False):
            continue
        
        try:
            # Parse time strings to datetime.time objects
            time_in_str = session.get("time_in", "")
            time_out_str = session.get("time_out", "")
            
            if not time_in_str or not time_out_str:
                continue
                
            time_in = datetime.strptime(time_in_str, "%I:%M %p").time()
            time_out = datetime.strptime(time_out_str, "%I:%M %p").time()
            
            # Check if session starts before allowed time
            if time_in < work_start:
                issues.append({
                    "issue_type": "invalid_start_time",
                    "severity": "medium",
                    "description": f"Session for {session.get('student_name')} starts before 10:00 AM",
                    "details": {
                        "student_name": session.get("student_name"),
                        "date": session.get("date"),
                        "time_in": time_in_str,
                        "time_out": time_out_str
                    }
                })
            
            # Check if session ends after allowed time
            if time_out > work_end:
                issues.append({
                    "issue_type": "invalid_end_time",
                    "severity": "medium",
                    "description": f"Session for {session.get('student_name')} ends after 7:00 PM",
                    "details": {
                        "student_name": session.get("student_name"),
                        "date": session.get("date"),
                        "time_in": time_in_str,
                        "time_out": time_out_str
                    }
                })
        
        except Exception as e:
            # Add issue for unparseable times
            issues.append({
                "issue_type": "unparseable_time",
                "severity": "low",
                "description": f"Unable to parse time for {session.get('student_name')}",
                "details": {
                    "student_name": session.get("student_name"),
                    "date": session.get("date"),
                    "time_in": session.get("time_in"),
                    "time_out": session.get("time_out"),
                    "error": str(e)
                }
            })
    
    return issues

def validate_student_hours(feedback_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate that students don't exceed 4 hours per week"""
    issues = []
    
    # Group sessions by student and week
    student_weekly_hours = {}
    
    for session in feedback_data.get("sessions", []):
        # Skip no-shows
        if session.get("is_no_show", False):
            continue
            
        student_id = session.get("student_id")
        date_str = session.get("date")
        hours = session.get("hours", 0)
        
        if not student_id or not date_str:
            continue
            
        try:
            # Parse date and get week number
            session_date = datetime.strptime(date_str, "%m/%d/%Y")
            year = session_date.year
            week = session_date.isocalendar()[1]  # Get ISO week number
            week_key = f"{year}-W{week}"
            
            # Initialize student weekly tracking
            if student_id not in student_weekly_hours:
                student_weekly_hours[student_id] = {}
            
            if week_key not in student_weekly_hours[student_id]:
                student_weekly_hours[student_id][week_key] = {
                    "hours": 0,
                    "sessions": []
                }
            
            # Add hours and session info
            student_weekly_hours[student_id][week_key]["hours"] += hours
            student_weekly_hours[student_id][week_key]["sessions"].append({
                "date": date_str,
                "hours": hours
            })
        
        except Exception:
            # Skip sessions with invalid dates
            continue
    
    # Check for weeks exceeding 4 hours
    for student_id, weeks in student_weekly_hours.items():
        student_name = next((session.get("student_name") for session in feedback_data.get("sessions", []) 
                           if session.get("student_id") == student_id), "Unknown Student")
        
        for week_key, data in weeks.items():
            if data["hours"] > 4:
                issues.append({
                    "issue_type": "excess_weekly_hours",
                    "severity": "high",
                    "description": f"Student {student_name} exceeds 4 hours in week {week_key}",
                    "details": {
                        "student_id": student_id,
                        "student_name": student_name,
                        "week": week_key,
                        "total_hours": data["hours"],
                        "excess_hours": data["hours"] - 4,
                        "sessions": data["sessions"]
                    }
                })
    
    return issues

def validate_no_shows(feedback_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate that students don't exceed 2 no-shows per month"""
    issues = []
    
    # Group no-shows by student and month
    student_monthly_no_shows = {}
    
    for session in feedback_data.get("sessions", []):
        if not session.get("is_no_show", False):
            continue
            
        student_id = session.get("student_id")
        date_str = session.get("date")
        
        if not student_id or not date_str:
            continue
            
        try:
            # Parse date and get month
            session_date = datetime.strptime(date_str, "%m/%d/%Y")
            year = session_date.year
            month = session_date.month
            month_key = f"{year}-{month:02d}"
            
            # Initialize student monthly tracking
            if student_id not in student_monthly_no_shows:
                student_monthly_no_shows[student_id] = {}
            
            if month_key not in student_monthly_no_shows[student_id]:
                student_monthly_no_shows[student_id][month_key] = {
                    "count": 0,
                    "dates": []
                }
            
            # Increment no-show count and track date
            student_monthly_no_shows[student_id][month_key]["count"] += 1
            student_monthly_no_shows[student_id][month_key]["dates"].append(date_str)
        
        except Exception:
            # Skip sessions with invalid dates
            continue
    
    # Check for months exceeding 2 no-shows
    for student_id, months in student_monthly_no_shows.items():
        student_name = next((session.get("student_name") for session in feedback_data.get("sessions", []) 
                           if session.get("student_id") == student_id), "Unknown Student")
        
        for month_key, data in months.items():
            if data["count"] > 2:
                issues.append({
                    "issue_type": "excess_no_shows",
                    "severity": "medium",
                    "description": f"Student {student_name} has {data['count']} no-shows in month {month_key}",
                    "details": {
                        "student_id": student_id,
                        "student_name": student_name,
                        "month": month_key,
                        "no_show_count": data["count"],
                        "excess_count": data["count"] - 2,
                        "no_show_dates": data["dates"]
                    }
                })
    
    return issues