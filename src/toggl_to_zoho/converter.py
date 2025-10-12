"""Core conversion logic for Toggl to Zoho CSV transformation."""

import csv
from datetime import time, date, datetime, timedelta
from typing import Dict, List


def required_headers(toggl_reader: csv.DictReader) -> bool:
    """Validate that all required headers are present in the Toggl CSV.
    
    Args:
        toggl_reader: CSV DictReader for the Toggl export file
        
    Returns:
        True if all required headers are present
        
    Raises:
        Exception: If any required header is missing
    """
    headers = ['Project', 'Task', 'Description', 'Start date', 'Start time', 
               'End date', 'End time', 'Duration', 'Tags']
    for header in headers:
        if header not in toggl_reader.fieldnames:
            raise Exception(f"Header '{header}' not found in the CSV file.")
    return True


def required_data(toggl_row: Dict[str, str]) -> bool:
    """Validate that all required data fields are present in a row.
    
    Args:
        toggl_row: Dictionary representing a single row from Toggl CSV
        
    Returns:
        True if all required fields have values
        
    Raises:
        Exception: If any required field is empty
    """
    required_fields = ['Project', 'Task', 'Start date', 'Start time', 'End date', 'End time']
    for field in required_fields:
        if not toggl_row.get(field):
            raise Exception(f"Missing required data in the CSV file.")
    return True


def getDuration(start_time: str, end_time: str) -> str:
    """Calculate duration between two times in HH:MM:SS format.
    
    Handles midnight crossings by adding a day if end time is before start time.
    
    Args:
        start_time: Start time in HH:MM:SS format
        end_time: End time in HH:MM:SS format
        
    Returns:
        Duration string in HH:MM:SS format
    """
    start_time_obj = datetime.strptime(start_time, '%H:%M:%S').time()
    end_time_obj = datetime.strptime(end_time, '%H:%M:%S').time()
    
    duration = datetime.combine(datetime.min, end_time_obj) - datetime.combine(datetime.min, start_time_obj)
    duration = duration + timedelta(days=1) if duration.total_seconds() < 0 else duration
    
    hours = duration.seconds // 3600
    minutes = (duration.seconds // 60) % 60
    seconds = duration.seconds % 60
    
    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return duration_str


def splitDates(toggl_row: Dict[str, str]) -> List[Dict[str, str]]:
    """Split multi-day time entries into separate single-day entries.
    
    If a time entry spans multiple days (start date != end date), it will be
    split into separate entries for each day, with appropriate time adjustments.
    
    Args:
        toggl_row: Dictionary representing a single row from Toggl CSV
        
    Returns:
        List of dictionaries, one for each day covered by the entry
    """
    rows = []
    start_date = datetime.strptime(toggl_row['Start date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(toggl_row['End date'], '%Y-%m-%d').date()
    
    if start_date == end_date:
        rows.append(toggl_row)
    else:
        while start_date < end_date:
            new_row = toggl_row.copy()
            new_row['Start date'] = start_date
            new_row['End date'] = start_date
            new_row['End time'] = '23:59:59'
            new_row['Duration'] = getDuration(new_row['Start time'], new_row['End time'])
            rows.append(new_row)
            start_date = start_date + timedelta(days=1)
            toggl_row['Start time'] = '00:00:00'
        
        new_row = toggl_row.copy()
        new_row['Start date'] = start_date
        new_row['End date'] = start_date
        new_row['End time'] = toggl_row['End time']
        new_row['Duration'] = getDuration(new_row['Start time'], new_row['End time'])
        rows.append(new_row)
    
    return rows


def reformatTime(toggl_row: Dict[str, str]) -> Dict[str, str]:
    """Convert time format from HH:MM:SS to HH:MM.
    
    Args:
        toggl_row: Dictionary representing a single row from Toggl CSV
        
    Returns:
        Modified toggl_row with reformatted times
    """
    start_time = time.fromisoformat(toggl_row['Start time'])
    end_time = time.fromisoformat(toggl_row['End time'])
    
    toggl_row['Start time'] = start_time.strftime("%H:%M")
    toggl_row['End time'] = end_time.strftime("%H:%M")
    
    duration = getDuration(toggl_row['Start time'] + ":00", toggl_row['End time'] + ":00")
    # clip the seconds
    duration = duration[:5]
    toggl_row['Duration'] = duration
    
    return toggl_row


def renameBillable(toggl_row: Dict[str, str]) -> Dict[str, str]:
    """Convert Yes/No billable status to Billable/Non Billable.
    
    Args:
        toggl_row: Dictionary representing a single row from Toggl CSV
        
    Returns:
        Modified toggl_row with converted billable status
    """
    if toggl_row['Billable'] == 'Yes':
        toggl_row['Billable'] = 'Billable'
    else:
        toggl_row['Billable'] = 'Non Billable'
    return toggl_row


def renameHeaders(toggl_row: Dict[str, str]) -> Dict[str, str]:
    """Map Toggl column names to Zoho column names.
    
    Args:
        toggl_row: Dictionary representing a single row from Toggl CSV
        
    Returns:
        Dictionary with Zoho-formatted column names
    """
    zoho_row = {}
    zoho_row['Project Name'] = toggl_row['Project']
    zoho_row['Notes'] = toggl_row['Description']
    zoho_row['Email'] = toggl_row['Email']
    zoho_row['Task Name'] = toggl_row['Task']
    zoho_row['Time Spent'] = toggl_row['Duration']
    zoho_row['Begin Time'] = toggl_row['Start time']
    zoho_row['End Time'] = toggl_row['End time']
    zoho_row['Date'] = toggl_row['Start date']
    zoho_row['Billable Status'] = toggl_row['Billable']
    return zoho_row


def convert_toggl_to_zoho(input_file, output_file) -> None:
    """Convert a Toggl CSV export to Zoho-compatible format.
    
    Args:
        input_file: File object, path, or string path for the Toggl CSV export
        output_file: File object, path, or string path for the Zoho CSV output
    """
    # Check if input_file is a file-like object or a path
    input_is_file_object = hasattr(input_file, 'read')
    output_is_file_object = hasattr(output_file, 'write')
    
    # Handle input
    if input_is_file_object:
        toggl_file = input_file
        should_close_input = False
    else:
        toggl_file = open(input_file, newline='', mode='r', encoding='utf-8-sig')
        should_close_input = True
    
    try:
        toggl_reader = csv.DictReader(toggl_file)
        
        if not required_headers(toggl_reader):
            return
        
        zoho_rows = []
        for toggl_row in toggl_reader:
            if not required_data(toggl_row):
                return
            
            rows = splitDates(toggl_row)
            for r in rows:
                r = reformatTime(r)
                r = renameBillable(r)
                zoho_row = renameHeaders(r)
                zoho_rows.append(zoho_row)
        
        # Handle output
        if output_is_file_object:
            zoho_file = output_file
            should_close_output = False
        else:
            zoho_file = open(output_file, mode='w', newline='', encoding='utf-8-sig')
            should_close_output = True
        
        try:
            zoho_writer = csv.DictWriter(zoho_file, fieldnames=zoho_rows[0].keys())
            zoho_writer.writeheader()
            for zoho_row in zoho_rows:
                zoho_writer.writerow(zoho_row)
            
            # Flush file-like objects (don't flush file paths)
            if output_is_file_object and hasattr(zoho_file, 'flush'):
                zoho_file.flush()
        finally:
            if should_close_output:
                zoho_file.close()
    
    finally:
        if should_close_input:
            toggl_file.close()
