"""File I/O operations for ECG data."""

import os
from typing import List
from ..utils.constants import DATA_RECORD_DIR, REPORTS_DIR, REPORT_SAMPLES_COUNT


class ECGFileManager:
    """Handles file operations for ECG data."""
    
    def __init__(self):
        """Initialize file manager and ensure directories exist."""
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs(DATA_RECORD_DIR, exist_ok=True)
        os.makedirs(REPORTS_DIR, exist_ok=True)
    
    def write_channel_data(self, channel: int, data: List[float]):
        """
        Write channel data to file.
        
        Parameters:
        channel (int): Channel number (1-8)
        data (List[float]): Data values to write
        """
        file_path = os.path.join(DATA_RECORD_DIR, f'data_record_ch{channel}.txt')
        with open(file_path, 'a') as file:
            for value in data:
                file.write(f'{value}\n')
    
    def read_last_channel_values(self, channel: int, count: int = REPORT_SAMPLES_COUNT) -> List[float]:
        """
        Read the last N values from a channel file.
        
        Parameters:
        channel (int): Channel number (1-8)
        count (int): Number of values to read from the end
        
        Returns:
        List[float]: Last N values from the file
        """
        file_path = os.path.join(DATA_RECORD_DIR, f'data_record_ch{channel}.txt')
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                start_index = max(0, len(lines) - count)
                return [float(line.strip()) for line in lines[start_index:]]
        except FileNotFoundError:
            print(f"Data file for channel {channel} not found.")
            return []
        except ValueError as e:
            print(f"Error processing file for channel {channel}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error reading channel {channel}: {e}")
            return []
    
    def read_all_last_values(self, count: int = REPORT_SAMPLES_COUNT) -> dict:
        """
        Read the last N values from all channel files.
        
        Parameters:
        count (int): Number of values to read from the end of each file
        
        Returns:
        dict: Dictionary with channel numbers as keys and data lists as values
        """
        all_data = {}
        for channel in range(1, 9):
            all_data[f'channel{channel}'] = self.read_last_channel_values(channel, count)
        return all_data
    
    def get_report_output_path(self, filename: str = "output.pdf") -> str:
        """
        Get the full path for a report file.
        
        Parameters:
        filename (str): Report filename
        
        Returns:
        str: Full path to the report file
        """
        return os.path.join(REPORTS_DIR, filename)