"""
Utility functions for attendance time calculations.
"""
from datetime import timedelta


def format_duration_as_hms(duration):
    """
    Format a timedelta as "HH:MM:SS" string.
    
    Args:
        duration: timedelta object
        
    Returns:
        str: Formatted duration string (e.g., "08:30:00")
    """
    if not duration:
        return "00:00:00"
    
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
