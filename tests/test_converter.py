"""Tests for the core conversion logic."""

import pytest
from datetime import datetime, timedelta
from toggl_to_zoho.converter import (
    getDuration,
    splitDates,
    reformatTime,
    renameBillable,
    renameHeaders,
)


class TestGetDuration:
    """Tests for duration calculation."""
    
    def test_simple_duration(self):
        """Test basic duration calculation."""
        result = getDuration("10:00:00", "11:30:00")
        assert result == "01:30:00"
    
    def test_midnight_crossing(self):
        """Test duration that crosses midnight."""
        result = getDuration("23:00:00", "01:00:00")
        assert result == "02:00:00"
    
    def test_same_time(self):
        """Test zero duration."""
        result = getDuration("10:00:00", "10:00:00")
        assert result == "00:00:00"
    
    def test_almost_full_day(self):
        """Test duration close to 24 hours."""
        result = getDuration("00:00:00", "23:59:00")
        assert result == "23:59:00"


class TestSplitDates:
    """Tests for multi-day entry splitting."""
    
    def test_same_day_entry(self):
        """Test that same-day entries are not split."""
        row = {
            'Start date': '2025-04-02',
            'End date': '2025-04-02',
            'Start time': '10:00:00',
            'End time': '11:00:00',
            'Duration': '01:00:00',
        }
        result = splitDates(row)
        assert len(result) == 1
        assert result[0]['Start date'] == row['Start date']
    
    def test_two_day_entry(self):
        """Test splitting an entry that spans two days."""
        row = {
            'Start date': '2025-04-08',
            'End date': '2025-04-09',
            'Start time': '23:00:00',
            'End time': '01:00:00',
            'Duration': '02:00:00',
            'Project': 'Test',
        }
        result = splitDates(row)
        assert len(result) == 2
        
        # First day should end at 23:59:59
        assert result[0]['Start date'].isoformat() == '2025-04-08'
        assert result[0]['End date'].isoformat() == '2025-04-08'
        assert result[0]['Start time'] == '23:00:00'
        assert result[0]['End time'] == '23:59:59'
        
        # Second day should start at 00:00:00
        assert result[1]['Start date'].isoformat() == '2025-04-09'
        assert result[1]['End date'].isoformat() == '2025-04-09'
        assert result[1]['Start time'] == '00:00:00'
        assert result[1]['End time'] == '01:00:00'
    
    def test_three_day_entry(self):
        """Test splitting an entry that spans three days."""
        row = {
            'Start date': '2025-04-08',
            'End date': '2025-04-10',
            'Start time': '22:00:00',
            'End time': '02:00:00',
            'Duration': '28:00:00',
            'Project': 'Test',
        }
        result = splitDates(row)
        assert len(result) == 3


class TestReformatTime:
    """Tests for time format conversion."""
    
    def test_reformat_basic(self):
        """Test basic time reformatting from HH:MM:SS to HH:MM."""
        row = {
            'Start time': '10:30:45',
            'End time': '11:45:30',
        }
        result = reformatTime(row)
        assert result['Start time'] == '10:30'
        assert result['End time'] == '11:45'
        assert result['Duration'] == '01:15'
    
    def test_reformat_midnight(self):
        """Test time reformatting with midnight times."""
        row = {
            'Start time': '00:00:00',
            'End time': '01:30:00',
        }
        result = reformatTime(row)
        assert result['Start time'] == '00:00'
        assert result['End time'] == '01:30'
        assert result['Duration'] == '01:30'


class TestRenameBillable:
    """Tests for billable status conversion."""
    
    def test_yes_to_billable(self):
        """Test converting 'Yes' to 'Billable'."""
        row = {'Billable': 'Yes'}
        result = renameBillable(row)
        assert result['Billable'] == 'Billable'
    
    def test_no_to_non_billable(self):
        """Test converting 'No' to 'Non Billable'."""
        row = {'Billable': 'No'}
        result = renameBillable(row)
        assert result['Billable'] == 'Non Billable'
    
    def test_empty_to_non_billable(self):
        """Test converting empty string to 'Non Billable'."""
        row = {'Billable': ''}
        result = renameBillable(row)
        assert result['Billable'] == 'Non Billable'


class TestRenameHeaders:
    """Tests for header mapping."""
    
    def test_header_mapping(self):
        """Test that all Toggl headers map correctly to Zoho headers."""
        toggl_row = {
            'Project': 'Project Alpha',
            'Description': 'Test work',
            'Email': 'test@example.com',
            'Task': 'Task A',
            'Duration': '01:30',
            'Start time': '10:00',
            'End time': '11:30',
            'Start date': '2025-04-02',
            'Billable': 'Billable',
        }
        
        zoho_row = renameHeaders(toggl_row)
        
        assert zoho_row['Project Name'] == 'Project Alpha'
        assert zoho_row['Notes'] == 'Test work'
        assert zoho_row['Email'] == 'test@example.com'
        assert zoho_row['Task Name'] == 'Task A'
        assert zoho_row['Time Spent'] == '01:30'
        assert zoho_row['Begin Time'] == '10:00'
        assert zoho_row['End Time'] == '11:30'
        assert zoho_row['Date'] == '2025-04-02'
        assert zoho_row['Billable Status'] == 'Billable'
