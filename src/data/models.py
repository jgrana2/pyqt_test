"""Data models for the ECG application."""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class PatientData:
    """Patient information data model."""
    first_name: str = ""
    last_name: str = ""
    gender: str = "Masculino"
    age: int = 31
    height: int = 156
    weight: int = 60
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'gender': self.gender,
            'age': self.age,
            'height': self.height,
            'weight': self.weight
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatientData':
        """Create PatientData from dictionary."""
        return cls(
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            gender=data.get('gender', 'Masculino'),
            age=data.get('age', 31),
            height=data.get('height', 156),
            weight=data.get('weight', 60)
        )


@dataclass
class ECGData:
    """ECG data container for all channels."""
    channel1: list = None
    channel2: list = None
    channel3: list = None
    channel4: list = None
    channel5: list = None
    channel6: list = None
    channel7: list = None
    channel8: list = None
    
    def __post_init__(self):
        """Initialize empty lists if None."""
        for i in range(1, 9):
            if getattr(self, f'channel{i}') is None:
                setattr(self, f'channel{i}', [])
    
    def get_channel_data(self, channel: int) -> list:
        """Get data for specific channel."""
        return getattr(self, f'channel{channel}', [])
    
    def set_channel_data(self, channel: int, data: list):
        """Set data for specific channel."""
        setattr(self, f'channel{channel}', data)
    
    def to_websocket_packet(self, sample_count: int = 250) -> Dict[str, Any]:
        """Convert to WebSocket packet format."""
        return {
            "type": "ecg_chunk",
            "data": {
                f"channel{i}": getattr(self, f'channel{i}')[:sample_count]
                for i in range(1, 9)
            }
        }