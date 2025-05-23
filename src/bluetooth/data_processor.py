"""Data processing logic for ECG signals."""

import numpy as np
from ..utils.helpers import filter_ecg


class ECGDataProcessor:
    """Handles processing of ECG data for different leads."""
    
    @staticmethod
    def derive_lead_iii(channel1_data: list, channel2_data: list) -> np.ndarray:
        """Derive Lead III from channels I and II."""
        return filter_ecg(np.array(channel2_data) - np.array(channel1_data))
    
    @staticmethod
    def derive_lead_avr(channel1_data: list, channel2_data: list) -> np.ndarray:
        """Derive Lead aVR from channels I and II."""
        return filter_ecg((np.array(channel1_data) + np.array(channel2_data)) / 2)
    
    @staticmethod
    def derive_lead_avl(channel1_data: list, channel2_data: list) -> np.ndarray:
        """Derive Lead aVL from channels I and II."""
        return filter_ecg(np.array(channel1_data) - np.array(channel2_data) / 2)
    
    @staticmethod
    def derive_lead_avf(channel1_data: list, channel2_data: list) -> np.ndarray:
        """Derive Lead aVF from channels I and II."""
        return filter_ecg(np.array(channel2_data) - np.array(channel1_data) / 2)
    
    @staticmethod
    def process_channel_data(channel_data: list) -> np.ndarray:
        """Process raw channel data with filtering."""
        return filter_ecg(channel_data)
    
    def get_lead_data(self, lead_name: str, channel_data: dict) -> np.ndarray:
        """
        Get processed data for a specific ECG lead.
        
        Parameters:
        lead_name (str): Name of the ECG lead
        channel_data (dict): Dictionary containing channel data
        
        Returns:
        np.ndarray: Processed ECG data for the lead
        """
        lead_mapping = {
            "I": lambda: self.process_channel_data(channel_data['channel1']),
            "II": lambda: self.process_channel_data(channel_data['channel2']),
            "III": lambda: self.derive_lead_iii(channel_data['channel1'], channel_data['channel2']),
            "aVR": lambda: self.derive_lead_avr(channel_data['channel1'], channel_data['channel2']),
            "aVL": lambda: self.derive_lead_avl(channel_data['channel1'], channel_data['channel2']),
            "aVF": lambda: self.derive_lead_avf(channel_data['channel1'], channel_data['channel2']),
            "V1": lambda: self.process_channel_data(channel_data['channel3']),
            "V2": lambda: self.process_channel_data(channel_data['channel4']),
            "V3": lambda: self.process_channel_data(channel_data['channel5']),
            "V4": lambda: self.process_channel_data(channel_data['channel6']),
            "V5": lambda: self.process_channel_data(channel_data['channel7']),
            "V6": lambda: self.process_channel_data(channel_data['channel8']),
        }
        
        if lead_name in lead_mapping:
            return lead_mapping[lead_name]()
        else:
            raise ValueError(f"Unknown lead: {lead_name}")