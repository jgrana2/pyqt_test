"""BLE worker for handling Bluetooth communication."""

import asyncio
import json
import numpy as np
import websockets
from PyQt5.QtCore import QThread, pyqtSignal
from bleak import BleakClient

from ..utils.constants import (SAMPLES_PER_BUFFER, BASELINE_WANDER_ALPHA, 
                              WEBSOCKET_URL, WEBSOCKET_BUFFER_SIZE)
from ..utils.helpers import process_24bit_data, apply_baseline_wander_removal
from ..data.file_manager import ECGFileManager
from ..data.models import ECGData


class BLEWorker(QThread):
    """Worker thread for BLE communication and data processing."""
    
    connection_status_signal = pyqtSignal(bool)
    error_signal = pyqtSignal(str)
    
    def __init__(self, address, channel_uuids):
        super().__init__()
        self.address = address
        self.channel_uuids = channel_uuids
        
        # Initialize sample arrays for each channel
        self.samples_arrays = {}
        self.last_data_previous = {}
        self.last_y_previous = {}
        
        for i in range(1, 9):
            self.samples_arrays[i] = np.zeros(SAMPLES_PER_BUFFER)
            self.last_data_previous[i] = 0
            self.last_y_previous[i] = 0
        
        self.buffer_idx = 0
        self.ws_url = WEBSOCKET_URL
        self.ws = None
        self.channel_buffers = [[] for _ in range(8)]
        self.file_manager = ECGFileManager()
    
    def get_samples_array(self, channel: int) -> np.ndarray:
        """Get samples array for a specific channel."""
        return self.samples_arrays.get(channel, np.zeros(SAMPLES_PER_BUFFER))
    
    async def notification_handler(self, channel: int, sender, data):
        """Generic notification handler for any channel."""
        if self.buffer_idx == channel - 1:
            # Convert hex string to bytes
            hex_data = data.hex()
            data_bytes = bytes.fromhex(hex_data)
            data_array = process_24bit_data(data_bytes)

            # Apply baseline wander removal
            self.samples_arrays[channel], self.last_data_previous[channel], self.last_y_previous[channel] = \
                apply_baseline_wander_removal(
                    data_array, 
                    self.samples_arrays[channel],
                    self.last_data_previous[channel],
                    self.last_y_previous[channel],
                    BASELINE_WANDER_ALPHA
                )
            
            # Record the processed data to a file
            self.file_manager.write_channel_data(channel, self.samples_arrays[channel])
            
            self.buffer_idx += 1
            
            # Special handling for the last channel
            if channel == 8:
                await self.handle_final_channel()
    
    async def handle_final_channel(self):
        """Handle processing after the final channel data is received."""
        # Append samples to channel buffers
        for i in range(8):
            self.channel_buffers[i].extend(self.samples_arrays[i + 1].tolist())
        
        # Send when we have at least the required buffer size
        if len(self.channel_buffers[0]) >= WEBSOCKET_BUFFER_SIZE:
            ecg_data = ECGData()
            for i in range(8):
                ecg_data.set_channel_data(i + 1, self.channel_buffers[i][:WEBSOCKET_BUFFER_SIZE])
            
            data_packet = ecg_data.to_websocket_packet(WEBSOCKET_BUFFER_SIZE)
            await self.ws.send(json.dumps(data_packet))
            
            # Remove sent samples
            for i in range(8):
                self.channel_buffers[i] = self.channel_buffers[i][WEBSOCKET_BUFFER_SIZE:]
        
        self.buffer_idx = 0
    
    async def connect_to_ble_device(self):
        """Connect to BLE device and start data collection."""
        self.connection_status_signal.emit(False)
        try:
            # Connect to WebSocket if not already connected
            if self.ws is None or self.ws.closed:
                self.ws = await websockets.connect(self.ws_url)
                self.error_signal.emit(f"WebSocket connection established to {self.ws_url}")
            else:
                self.error_signal.emit(f"WebSocket already connected to {self.ws_url}")
                
            async with BleakClient(self.address) as client:
                await client.connect()
                if client.is_connected():
                    self.connection_status_signal.emit(True)
                    print(f"Connected to {self.address}")
                    
                    # Create specific handlers for each channel
                    handlers = {}
                    for channel, uuid in self.channel_uuids.items():
                        def make_handler(ch):
                            def handler(sender, data):
                                asyncio.create_task(self.notification_handler(ch, sender, data))
                            return handler
                        
                        handlers[channel] = make_handler(channel)
                        await client.start_notify(uuid, handlers[channel])
                        print(f"Notifications enabled for channel {channel}: {uuid}")
                    
                    # Keep connection alive
                    while True:
                        await asyncio.sleep(1)
                else:
                    self.error_signal.emit("Failed to connect.")
        except Exception as e:
            self.error_signal.emit(f"An error occurred: {e}")

    def run(self):
        """Run the BLE worker in its own event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect_to_ble_device())