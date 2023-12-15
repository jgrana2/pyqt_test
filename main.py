import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QGridLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QThread
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator
import numpy as np
import asyncio
from bleak import BleakScanner, BleakClient
from ecg_report_generator import generate_ecg_report

class BLEWorker(QThread):
    def __init__(self, address, channel1_uuid, channel2_uuid, channel3_uuid, channel4_uuid, channel5_uuid, channel6_uuid, channel7_uuid, channel8_uuid):
        super().__init__()
        self.address = address
        self.channel1_uuid = channel1_uuid
        self.channel2_uuid = channel2_uuid
        self.channel3_uuid = channel3_uuid
        self.channel4_uuid = channel4_uuid
        self.channel5_uuid = channel5_uuid
        self.channel6_uuid = channel6_uuid
        self.channel7_uuid = channel7_uuid
        self.channel8_uuid = channel8_uuid
        self.samples_array1 = np.zeros(28)
        self.samples_array2 = np.zeros(28)
        self.samples_array3 = np.zeros(28)
        self.samples_array4 = np.zeros(28)
        self.samples_array5 = np.zeros(28)
        self.samples_array6 = np.zeros(28)
        self.samples_array7 = np.zeros(28)
        self.samples_array8 = np.zeros(28)
        self.last_data_previous1 = 0
        self.last_y_previous1 = 0 
        self.last_data_previous2 = 0
        self.last_y_previous2 = 0 
        self.last_data_previous3 = 0
        self.last_y_previous3 = 0
        self.last_data_previous4 = 0
        self.last_y_previous4 = 0
        self.last_data_previous5 = 0
        self.last_y_previous5 = 0
        self.last_data_previous6 = 0
        self.last_y_previous6 = 0
        self.last_data_previous7 = 0
        self.last_y_previous7 = 0
        self.last_data_previous8 = 0
        self.last_y_previous8 = 0

    async def notification_handler(self, sender, data):
        # Convert hex string to bytes
        hex_data = data.hex()
        data_bytes = bytes.fromhex(hex_data)
        data_array = []
        for index in range(0, len(data_bytes), 3):
            if index + 3 <= len(data_bytes):
                byte1, byte2, byte3 = data_bytes[index:index+3]
                value_24bit = (byte1 << 16) | (byte2 << 8) | byte3
                if value_24bit & 0x800000:
                    value_24bit = value_24bit - 0x1000000
                data_array.append(value_24bit)

        # Baseline wander removal
        for i in range(len(data_array)):
            if i == 0:
                self.samples_array1[i] = data_array[i] - self.last_data_previous1 + 0.995 * self.last_y_previous1
                self.last_data_previous1 = data_array[i]
                self.last_y_previous1 = self.samples_array1[i]
            else:
                self.samples_array1[i] = data_array[i] - data_array[i - 1] + 0.995 * self.samples_array1[i - 1]
                data_array[i - 1] = data_array[i]
                self.samples_array1[i - 1] = self.samples_array1[i]
        self.last_data_previous1 = data_array[-1]
        self.last_y_previous1 = self.samples_array1[-1]
   
        # Record the processed data to a file
        file_path = 'data_record_ch1.txt'  # Specify your file path here
        with open(file_path, 'a') as file:
            for value in self.samples_array1:
                file.write(f'{value}\n')  # Write each value on a new line
             
    async def notification_handler2(self, sender, data):
        # Convert hex string to bytes
        hex_data = data.hex()
        data_bytes = bytes.fromhex(hex_data)
        data_array = []
        for index in range(0, len(data_bytes), 3):
            if index + 3 <= len(data_bytes):
                byte1, byte2, byte3 = data_bytes[index:index+3]
                value_24bit = (byte1 << 16) | (byte2 << 8) | byte3
                if value_24bit & 0x800000:
                    value_24bit = value_24bit - 0x1000000
                data_array.append(value_24bit)

        # Baseline wander removal
        for i in range(len(data_array)):
            if i == 0:
                self.samples_array2[i] = data_array[i] - self.last_data_previous2 + 0.995 * self.last_y_previous2
                self.last_data_previous2 = data_array[i]
                self.last_y_previous2 = self.samples_array2[i]
            else:
                self.samples_array2[i] = data_array[i] - data_array[i - 1] + 0.995 * self.samples_array2[i - 1]
                data_array[i - 1] = data_array[i]
                self.samples_array2[i - 1] = self.samples_array2[i]
        self.last_data_previous2 = data_array[-1]
        self.last_y_previous2 = self.samples_array2[-1]
        
         # Record the processed data to a file
        file_path = 'data_record_ch2.txt'  # Specify your file path here
        with open(file_path, 'a') as file:
            for value in self.samples_array2:
                file.write(f'{value}\n')  # Write each value on a new line
                
    async def notification_handler3(self, sender, data):
        # Convert hex string to bytes
        hex_data = data.hex()
        data_bytes = bytes.fromhex(hex_data)
        data_array = []
        for index in range(0, len(data_bytes), 3):
            if index + 3 <= len(data_bytes):
                byte1, byte2, byte3 = data_bytes[index:index+3]
                value_24bit = (byte1 << 16) | (byte2 << 8) | byte3
                if value_24bit & 0x800000:
                    value_24bit = value_24bit - 0x1000000
                data_array.append(value_24bit)

        # Baseline wander removal
        for i in range(len(data_array)):
            if i == 0:
                self.samples_array3[i] = data_array[i] - self.last_data_previous3 + 0.995 * self.last_y_previous3
                self.last_data_previous3 = data_array[i]
                self.last_y_previous3 = self.samples_array3[i]
            else:
                self.samples_array3[i] = data_array[i] - data_array[i - 1] + 0.995 * self.samples_array3[i - 1]
                data_array[i - 1] = data_array[i]
                self.samples_array3[i - 1] = self.samples_array3[i]
        self.last_data_previous3 = data_array[-1]
        self.last_y_previous3 = self.samples_array3[-1]
        
         # Record the processed data to a file
        file_path = 'data_record_ch3.txt'  # Specify your file path here
        with open(file_path, 'a') as file:
            for value in self.samples_array3:
                file.write(f'{value}\n')  # Write each value on a new line
        
    async def notification_handler4(self, sender, data):
        # Convert hex string to bytes
        hex_data = data.hex()
        data_bytes = bytes.fromhex(hex_data)
        data_array = []
        for index in range(0, len(data_bytes), 3):
            if index + 3 <= len(data_bytes):
                byte1, byte2, byte3 = data_bytes[index:index+3]
                value_24bit = (byte1 << 16) | (byte2 << 8) | byte3
                if value_24bit & 0x800000:
                    value_24bit = value_24bit - 0x1000000
                data_array.append(value_24bit)

        # Baseline wander removal
        for i in range(len(data_array)):
            if i == 0:
                self.samples_array4[i] = data_array[i] - self.last_data_previous4 + 0.995 * self.last_y_previous4
                self.last_data_previous4 = data_array[i]
                self.last_y_previous4 = self.samples_array4[i]
            else:
                self.samples_array4[i] = data_array[i] - data_array[i - 1] + 0.995 * self.samples_array4[i - 1]
                data_array[i - 1] = data_array[i]
                self.samples_array4[i - 1] = self.samples_array4 [i]
        self.last_data_previous4 = data_array[-1]
        self.last_y_previous4 = self.samples_array4[-1]
        
         # Record the processed data to a file
        file_path = 'data_record_ch4.txt'  # Specify your file path here
        with open(file_path, 'a') as file:
            for value in self.samples_array4:
                file.write(f'{value}\n')  # Write each value on a new line
        
    async def notification_handler5(self, sender, data):
        # Convert hex string to bytes
        hex_data = data.hex()
        data_bytes = bytes.fromhex(hex_data)
        data_array = []
        for index in range(0, len(data_bytes), 3):
            if index + 3 <= len(data_bytes):
                byte1, byte2, byte3 = data_bytes[index:index+3]
                value_24bit = (byte1 << 16) | (byte2 << 8) | byte3
                if value_24bit & 0x800000:
                    value_24bit = value_24bit - 0x1000000
                data_array.append(value_24bit)

        # Baseline wander removal
        for i in range(len(data_array)):
            if i == 0:
                self.samples_array5[i] = data_array[i] - self.last_data_previous5 + 0.995 * self.last_y_previous5
                self.last_data_previous5 = data_array[i]
                self.last_y_previous5 = self.samples_array5[i]
            else:
                self.samples_array5[i] = data_array[i] - data_array[i - 1] + 0.995 * self.samples_array5[i - 1]
                data_array[i - 1] = data_array[i]
                self.samples_array5[i - 1] = self.samples_array5[i]
        self.last_data_previous5 = data_array[-1]
        self.last_y_previous5 = self.samples_array5[-1]
        
         # Record the processed data to a file
        file_path = 'data_record_ch5.txt'  # Specify your file path here
        with open(file_path, 'a') as file:
            for value in self.samples_array5:
                file.write(f'{value}\n')  # Write each value on a new line
                
    async def notification_handler6(self, sender, data):
        # Convert hex string to bytes
        hex_data = data.hex()
        data_bytes = bytes.fromhex(hex_data)
        data_array = []
        for index in range(0, len(data_bytes), 3):
            if index + 3 <= len(data_bytes):
                byte1, byte2, byte3 = data_bytes[index:index+3]
                value_24bit = (byte1 << 16) | (byte2 << 8) | byte3
                if value_24bit & 0x800000:
                    value_24bit = value_24bit - 0x1000000
                data_array.append(value_24bit)

        # Baseline wander removal
        for i in range(len(data_array)):
            if i == 0:
                self.samples_array6[i] = data_array[i] - self.last_data_previous6 + 0.995 * self.last_y_previous6
                self.last_data_previous6 = data_array[i]
                self.last_y_previous6 = self.samples_array6[i]
            else:
                self.samples_array6[i] = data_array[i] - data_array[i - 1] + 0.995 * self.samples_array6[i - 1]
                data_array[i - 1] = data_array[i]
                self.samples_array6[i - 1] = self.samples_array6[i]
        self.last_data_previous6 = data_array[-1]
        self.last_y_previous6 = self.samples_array6[-1]
        
         # Record the processed data to a file
        file_path = 'data_record_ch6.txt'  # Specify your file path here
        with open(file_path, 'a') as file:
            for value in self.samples_array6:
                file.write(f'{value}\n')  # Write each value on a new line
                
    async def notification_handler7(self, sender, data):
        # Convert hex string to bytes
        hex_data = data.hex()
        data_bytes = bytes.fromhex(hex_data)
        data_array = []
        for index in range(0, len(data_bytes), 3):
            if index + 3 <= len(data_bytes):
                byte1, byte2, byte3 = data_bytes[index:index+3]
                value_24bit = (byte1 << 16) | (byte2 << 8) | byte3
                if value_24bit & 0x800000:
                    value_24bit = value_24bit - 0x1000000
                data_array.append(value_24bit)

        # Baseline wander removal
        for i in range(len(data_array)):
            if i == 0:
                self.samples_array7[i] = data_array[i] - self.last_data_previous7 + 0.995 * self.last_y_previous7
                self.last_data_previous7 = data_array[i]
                self.last_y_previous7 = self.samples_array7[i]
            else:
                self.samples_array7[i] = data_array[i] - data_array[i - 1] + 0.995 * self.samples_array7[i - 1]
                data_array[i - 1] = data_array[i]
                self.samples_array7[i - 1] = self.samples_array7 [i]
        self.last_data_previous7 = data_array[-1]
        self.last_y_previous7 = self.samples_array7[-1]
        
         # Record the processed data to a file
        file_path = 'data_record_ch7.txt'  # Specify your file path here
        with open(file_path, 'a') as file:
            for value in self.samples_array7:
                file.write(f'{value}\n')  # Write each value on a new line
                
    async def notification_handler8(self, sender, data):
        # Convert hex string to bytes
        hex_data = data.hex()
        data_bytes = bytes.fromhex(hex_data)
        data_array = []
        for index in range(0, len(data_bytes), 3):
            if index + 3 <= len(data_bytes):
                byte1, byte2, byte3 = data_bytes[index:index+3]
                value_24bit = (byte1 << 16) | (byte2 << 8) | byte3
                if value_24bit & 0x800000:
                    value_24bit = value_24bit - 0x1000000
                data_array.append(value_24bit)

        # Baseline wander removal
        for i in range(len(data_array)):
            if i == 0:
                self.samples_array8[i] = data_array[i] - self.last_data_previous8 + 0.995 * self.last_y_previous8
                self.last_data_previous8 = data_array[i]
                self.last_y_previous8 = self.samples_array8[i]
            else:
                self.samples_array8[i] = data_array[i] - data_array[i - 1] + 0.995 * self.samples_array8[i - 1]
                data_array[i - 1] = data_array[i]
                self.samples_array8[i - 1] = self.samples_array8 [i]
        self.last_data_previous8 = data_array[-1]
        self.last_y_previous8 = self.samples_array8[-1]
        
         # Record the processed data to a file
        file_path = 'data_record_ch8.txt'  # Specify your file path here
        with open(file_path, 'a') as file:
            for value in self.samples_array8:
                file.write(f'{value}\n')  # Write each value on a new line 
        
    async def connect_to_ble_device(self):
        try:
            async with BleakClient(self.address) as client:
                if await client.is_connected():
                    print(f"Connected to {self.address}")
                    await client.start_notify(self.channel1_uuid, self.notification_handler)
                    print(f"Notifications enabled for characteristic {self.channel1_uuid}")
                    await client.start_notify(self.channel2_uuid, self.notification_handler2)
                    print(f"Notifications enabled for characteristic {self.channel2_uuid}")
                    await client.start_notify(self.channel3_uuid, self.notification_handler3)
                    print(f"Notifications enabled for characteristic {self.channel3_uuid}")
                    await client.start_notify(self.channel4_uuid, self.notification_handler4)
                    print(f"Notifications enabled for characteristic {self.channel4_uuid}")
                    await client.start_notify(self.channel5_uuid, self.notification_handler5)
                    print(f"Notifications enabled for characteristic {self.channel5_uuid}")
                    await client.start_notify(self.channel6_uuid, self.notification_handler6)
                    print(f"Notifications enabled for characteristic {self.channel6_uuid}")
                    await client.start_notify(self.channel7_uuid, self.notification_handler7)
                    print(f"Notifications enabled for characteristic {self.channel7_uuid}")
                    await client.start_notify(self.channel8_uuid, self.notification_handler8)
                    print(f"Notifications enabled for characteristic {self.channel8_uuid}")
                    while True:
                        await asyncio.sleep(1)
                else:
                    print(f"Failed to connect to {self.address}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect_to_ble_device())

class AppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set up the main window
        self.setWindowTitle('Horizon Medical ECG Report Generator v0.1')
        self.setGeometry(100, 100, 1024, 400)  # Increased size for ECG plots
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        self.label_title = QLabel('ECG Report Generator', self)
        self.label_title.setAlignment(Qt.AlignLeft)
        font = QFont()
        font.setPointSize(18)
        self.label_title.setFont(font)
        self.label_image = QLabel(self)
        self.pixmap = QPixmap('logocut.png')
        self.label_image.setPixmap(self.pixmap)
        self.label_image.setAlignment(Qt.AlignRight)
        self.top_layout.addWidget(self.label_title)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.label_image)
        self.button_scan = QPushButton('CONNECT TO DEVICE', self)
        self.button_scan.clicked.connect(self.scan_devices)
        self.button_generate = QPushButton('GENERATE REPORT', self)
        self.button_generate.clicked.connect(self.read_last_values)
        self.layout.addLayout(self.top_layout)
        self.layout.addWidget(self.button_scan)
        self.layout.addWidget(self.button_generate)
        self.grid_layout = QGridLayout()
        self.fig = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.fig)
        
        self.ax = self.fig.add_subplot(141)
        self.ecg_line1, = self.ax.plot(np.zeros(375), 'k-', linewidth=0.5)  # Initialize with zeros
        self.ax.set_xlim(0, 375)
        self.ax.set_ylim(-16000, 16000)
        self.ax.grid(True, which='major', linestyle='-', linewidth=0.1, color='lightgray')
        self.ax.grid(True, which='minor', linestyle=':', linewidth=0.05, color='lightgray')
        self.ax.xaxis.set_major_locator(MultipleLocator(25))
        self.ax.xaxis.set_minor_locator(MultipleLocator(5))
        self.ax.yaxis.set_major_locator(MultipleLocator(4000))
        self.ax.yaxis.set_minor_locator(MultipleLocator(1000))
        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])
        
        self.ax2 = self.fig.add_subplot(142)  # Second subplot in the first row
        self.ecg_line2, = self.ax2.plot(np.zeros(375), 'k-', linewidth=0.5)  # Initialize with zeros
        self.ax2.set_xlim(0, 375)  # Set x-axis limits
        self.ax2.set_ylim(-16000, 16000)  # Set y-axis limits
        self.ax2.grid(True, which='major', linestyle='-', linewidth=0.1, color='lightgray')
        self.ax2.grid(True, which='minor', linestyle=':', linewidth=0.05, color='lightgray')
        self.ax2.xaxis.set_major_locator(MultipleLocator(25))
        self.ax2.xaxis.set_minor_locator(MultipleLocator(5))
        self.ax2.yaxis.set_major_locator(MultipleLocator(4000))
        self.ax2.yaxis.set_minor_locator(MultipleLocator(1000))
        self.ax2.set_yticklabels([])
        self.ax2.set_xticklabels([])
        
        self.ax3 = self.fig.add_subplot(143)  # Second subplot in the first row
        self.ecg_line3, = self.ax3.plot(np.zeros(375), 'k-', linewidth=0.5)  # Initialize with zeros
        self.ax3.set_xlim(0, 375)  # Set x-axis limits
        self.ax3.set_ylim(-16000, 16000)  # Set y-axis limits
        self.ax3.grid(True, which='major', linestyle='-', linewidth=0.1, color='lightgray')
        self.ax3.grid(True, which='minor', linestyle=':', linewidth=0.05, color='lightgray')
        self.ax3.xaxis.set_major_locator(MultipleLocator(25))
        self.ax3.xaxis.set_minor_locator(MultipleLocator(5))
        self.ax3.yaxis.set_major_locator(MultipleLocator(4000))
        self.ax3.yaxis.set_minor_locator(MultipleLocator(1000))
        self.ax3.set_yticklabels([])
        self.ax3.set_xticklabels([])
        
        self.ax4 = self.fig.add_subplot(144)  # Second subplot in the first row
        self.ecg_line4, = self.ax4.plot(np.zeros(375), 'k-', linewidth=0.5)  # Initialize with zeros
        self.ax4.set_ylim(-16000, 16000)  # Set y-axis limits
        self.ax4.set_xlim(0, 375)  # Set x-axis limits
        self.ax4.grid(True, which='major', linestyle='-', linewidth=0.1, color='lightgray')
        self.ax4.grid(True, which='minor', linestyle=':', linewidth=0.05, color='lightgray')
        self.ax4.xaxis.set_major_locator(MultipleLocator(25))
        self.ax4.xaxis.set_minor_locator(MultipleLocator(5))
        self.ax4.yaxis.set_major_locator(MultipleLocator(4000))
        self.ax4.yaxis.set_minor_locator(MultipleLocator(1000))
        self.ax4.set_yticklabels([])
        self.ax4.set_xticklabels([])
        
        self.grid_layout.addWidget(self.canvas, 0, 0)  # Single plot
        self.layout.addLayout(self.grid_layout)
        self.central_widget.setLayout(self.layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(112)  # Update interval in milliseconds, 112 ms for 28 samples at 250 SPS

    def update_plots(self):
       # Check if the BLE worker has been initialized and started
        if hasattr(self, 'ble_worker'):
            current_data1 = self.ecg_line1.get_ydata()
            updated_data1 = np.concatenate((current_data1[28:], self.ble_worker.samples_array1))
            self.ecg_line1.set_ydata(updated_data1)
            current_data2 = self.ecg_line2.get_ydata()
            updated_data2 = np.concatenate((current_data2[28:], self.ble_worker.samples_array2))
            self.ecg_line2.set_ydata(updated_data2)
            current_data3 = self.ecg_line3.get_ydata()
            updated_data3 = np.concatenate((current_data3[28:], self.ble_worker.samples_array3))
            self.ecg_line3.set_ydata(updated_data3)
            current_data4 = self.ecg_line4.get_ydata()
            updated_data4 = np.concatenate((current_data4[28:], self.ble_worker.samples_array4))
            self.ecg_line4.set_ydata(updated_data4)
            self.canvas.draw()
        else:
            pass

    @pyqtSlot()
    def scan_devices(self):
        target_address = "6614D41F-1CB3-77FA-3E35-C5A446EA4E3F"
        channel1_uuid = "00008171-0000-1000-8000-00805f9b34fb"
        channel2_uuid = "00008172-0000-1000-8000-00805f9b34fb"
        channel3_uuid = "00008173-0000-1000-8000-00805f9b34fb"
        channel4_uuid = "00008174-0000-1000-8000-00805f9b34fb"
        channel5_uuid = "00008175-0000-1000-8000-00805f9b34fb"
        channel6_uuid = "00008176-0000-1000-8000-00805f9b34fb"
        channel7_uuid = "00008177-0000-1000-8000-00805f9b34fb"
        channel8_uuid = "00008178-0000-1000-8000-00805f9b34fb"
        self.ble_worker = BLEWorker(target_address, channel1_uuid, channel2_uuid, channel3_uuid, channel4_uuid, channel5_uuid, channel6_uuid, channel7_uuid, channel8_uuid)
        self.ble_worker.start()
    
    def read_last_values(self):
        last_values_ch1 = []
        last_values_ch2 = []
        last_values_ch3 = []
        last_values_ch4 = []
        last_values_ch5 = []
        last_values_ch6 = []
        last_values_ch7 = []
        last_values_ch8 = []
        try:
            with open('data_record_ch1.txt', 'r') as file:
                lines = file.readlines()
                start_index = max(0, len(lines) - 750)
                last_values_ch1 = [float(line.strip()) for line in lines[start_index:]]
            with open('data_record_ch2.txt', 'r') as file:
                lines = file.readlines()
                start_index = max(0, len(lines) - 750)
                last_values_ch2 = [float(line.strip()) for line in lines[start_index:]]
            with open('data_record_ch3.txt', 'r') as file:
                lines = file.readlines()
                start_index = max(0, len(lines) - 750)
                last_values_ch3 = [float(line.strip()) for line in lines[start_index:]]
            with open('data_record_ch4.txt', 'r') as file:
                lines = file.readlines()
                start_index = max(0, len(lines) - 750)
                last_values_ch4 = [float(line.strip()) for line in lines[start_index:]]
            with open('data_record_ch5.txt', 'r') as file:
                lines = file.readlines()
                start_index = max(0, len(lines) - 750)
                last_values_ch5 = [float(line.strip()) for line in lines[start_index:]]
            with open('data_record_ch6.txt', 'r') as file:
                lines = file.readlines()
                start_index = max(0, len(lines) - 750)
                last_values_ch6 = [float(line.strip()) for line in lines[start_index:]]
            with open('data_record_ch7.txt', 'r') as file:
                lines = file.readlines()
                start_index = max(0, len(lines) - 750)
                last_values_ch7 = [float(line.strip()) for line in lines[start_index:]]
            with open('data_record_ch8.txt', 'r') as file:
                lines = file.readlines()
                start_index = max(0, len(lines) - 750)
                last_values_ch8 = [float(line.strip()) for line in lines[start_index:]]
        except FileNotFoundError:
            print("The data file was not found.")
        except ValueError as e:
            print(f"Error processing the file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        generate_ecg_report("output.pdf", last_values_ch1, last_values_ch2, last_values_ch3, last_values_ch4, last_values_ch5, last_values_ch6, last_values_ch7, last_values_ch8)
 
# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppMainWindow()
    window.show()
    sys.exit(app.exec_())
