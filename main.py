import sys
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QSpinBox, QComboBox, QMessageBox,
                             QWidget, QPushButton, QGridLayout, QAction, QFormLayout, QLineEdit, QDialog)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QDesktopServices
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QThread, QUrl, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator
import numpy as np
import asyncio
from bleak import BleakScanner, BleakClient
from ecg_report_generator import generate_ecg_report
import pyqtgraph as pg
import json
import websockets

class PatientDataForm(QDialog):
    def __init__(self):
        super().__init__()
        self.patient_data = {}
        
        # Set up the form layout
        self.layout = QFormLayout()

        # First Name
        self.first_name_label = QLabel('Nombres:')
        self.first_name_input = QLineEdit()
        self.layout.addRow(self.first_name_label, self.first_name_input)

        # Last Name
        self.last_name_label = QLabel('Apellidos:')
        self.last_name_input = QLineEdit()
        self.layout.addRow(self.last_name_label, self.last_name_input)

        # Gender
        self.gender_label = QLabel('Género:')
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Masculino", "Femenino", "Otro"])
        self.layout.addRow(self.gender_label, self.gender_input)

        # Age
        self.age_label = QLabel('Edad:')
        self.age_input = QSpinBox()
        self.age_input.setRange(0, 150)
        self.age_input.setValue(31)
        self.layout.addRow(self.age_label, self.age_input)

        # Height
        self.height_label = QLabel('Estatura (cm):')
        self.height_input = QSpinBox()
        self.height_input.setRange(0, 300)
        self.height_input.setValue(156)
        self.layout.addRow(self.height_label, self.height_input)

        # Weight
        self.weight_label = QLabel('Peso (kg):')
        self.weight_input = QSpinBox()
        self.weight_input.setRange(0, 500)
        self.weight_input.setValue(60)
        self.layout.addRow(self.weight_label, self.weight_input)

        # Submit Button
        self.submit_button = QPushButton('Guardar')
        self.submit_button.clicked.connect(self.submit_form)
        self.layout.addRow(self.submit_button)

        # Set the layout on the form
        self.setLayout(self.layout)

    def submit_form(self):
        # Gather form data and save to dictionary
        self.patient_data['first_name'] = self.first_name_input.text()
        self.patient_data['last_name'] = self.last_name_input.text()
        self.patient_data['gender'] = self.gender_input.currentText()
        self.patient_data['age'] = self.age_input.value()
        self.patient_data['height'] = self.height_input.value()
        self.patient_data['weight'] = self.weight_input.value()

        self.accept()  # Close the form dialog
    
    def get_patient_data(self):
        return self.patient_data

class DeviceConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super(DeviceConnectionDialog, self).__init__(parent)
        self.setWindowTitle("Estado de la Conexión")
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Conectándose al dispositivo...", self)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

class BLEWorker(QThread):
    connection_status_signal = pyqtSignal(bool)
    error_signal = pyqtSignal(str)
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
        self.buffer_idx = 0
        self.ws_url = "wss://hrzmed.org"
        self.ws = None
        self.channel_buffers = [[] for _ in range(8)]

    async def notification_handler(self, sender, data):
        if self.buffer_idx == 0:
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
            
            self.buffer_idx += 1
             
    async def notification_handler2(self, sender, data):
        if self.buffer_idx == 1:
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
            
            self.buffer_idx += 1
                
    async def notification_handler3(self, sender, data):
        if self.buffer_idx == 2:
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
            
            self.buffer_idx += 1
        
    async def notification_handler4(self, sender, data):
        if self.buffer_idx == 3:
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
                    
            self.buffer_idx += 1
        
    async def notification_handler5(self, sender, data):
        if self.buffer_idx == 4:
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
            
            self.buffer_idx += 1
                
    async def notification_handler6(self, sender, data):
        if self.buffer_idx == 5:
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
            
            self.buffer_idx += 1
                
    async def notification_handler7(self, sender, data):
        if self.buffer_idx == 6:
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
            
            self.buffer_idx += 1
            
    async def notification_handler8(self, sender, data):
        if self.buffer_idx == 7:
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
                    
            # Append samples to channel buffers
            self.channel_buffers[0].extend(self.samples_array1.tolist())
            self.channel_buffers[1].extend(self.samples_array2.tolist())
            self.channel_buffers[2].extend(self.samples_array3.tolist())
            self.channel_buffers[3].extend(self.samples_array4.tolist())
            self.channel_buffers[4].extend(self.samples_array5.tolist())
            self.channel_buffers[5].extend(self.samples_array6.tolist())
            self.channel_buffers[6].extend(self.samples_array7.tolist())
            self.channel_buffers[7].extend(self.samples_array8.tolist())
            # Send when we have at least 250 samples
            if len(self.channel_buffers[0]) >= 250:
                data_packet = {
                    "type": "ecg_chunk",
                    "data": {
                        "channel1": self.channel_buffers[0][:250],
                        "channel2": self.channel_buffers[1][:250],
                        "channel3": self.channel_buffers[2][:250],
                        "channel4": self.channel_buffers[3][:250],
                        "channel5": self.channel_buffers[4][:250],
                        "channel6": self.channel_buffers[5][:250],
                        "channel7": self.channel_buffers[6][:250],
                        "channel8": self.channel_buffers[7][:250],
                    }
                }
                await self.ws.send(json.dumps(data_packet))
                # Remove sent samples
                for i in range(8):
                    self.channel_buffers[i] = self.channel_buffers[i][250:]
            self.buffer_idx = 0
        
    async def connect_to_ble_device(self):
        self.connection_status_signal.emit(False)
        try:
            # Only connect if not already connected
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
                    self.error_signal.emit("Failed to connect.")
        except Exception as e:
            self.error_signal.emit(f"An error occurred: {e}")

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect_to_ble_device())

class AppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.device_connection_dialog = DeviceConnectionDialog()
        # Set up the main window
        self.setWindowTitle('Generador de Reportes ECG v0.1')
        self.setGeometry(100, 100, 1024, 400)  # Increased size for ECG plots
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        self.label_title = QLabel('Generador de Reportes ECG', self)
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
        self.layout.addLayout(self.top_layout)
        self.grid_layout = QGridLayout()
        self.create_toolbar()

        self.plot_widget1 = pg.PlotWidget()
        self.plot_widget1.setLimits(xMin=0, xMax=375, yMin=-16000, yMax=16000)
        self.plot_widget1.showGrid(x=True, y=True)
        self.plot_widget1.setBackground('w')
        self.ecg_line1 = self.plot_widget1.plot(np.zeros(375), pen=pg.mkPen('k', width=2))
        self.grid_layout.addWidget(self.plot_widget1, 0, 0)

        self.plot_widget2 = pg.PlotWidget()
        self.plot_widget2.setLimits(xMin=0, xMax=375, yMin=-16000, yMax=16000)
        self.plot_widget2.showGrid(x=True, y=True)
        self.plot_widget2.setBackground('w')
        self.ecg_line2 = self.plot_widget2.plot(np.zeros(375), pen=pg.mkPen('k', width=2))
        self.grid_layout.addWidget(self.plot_widget2, 0, 1)

        self.plot_widget3 = pg.PlotWidget()
        self.plot_widget3.setLimits(xMin=0, xMax=375, yMin=-16000, yMax=16000)
        self.plot_widget3.showGrid(x=True, y=True)
        self.plot_widget3.setBackground('w')
        self.ecg_line3 = self.plot_widget3.plot(np.zeros(375), pen=pg.mkPen('k', width=2))
        self.grid_layout.addWidget(self.plot_widget3, 0, 2)

        self.plot_widget4 = pg.PlotWidget()
        self.plot_widget4.setLimits(xMin=0, xMax=375, yMin=-16000, yMax=16000)
        self.plot_widget4.showGrid(x=True, y=True)
        self.plot_widget4.setBackground('w')
        self.ecg_line4 = self.plot_widget4.plot(np.zeros(375), pen=pg.mkPen('k', width=2))
        self.grid_layout.addWidget(self.plot_widget4, 0, 3)

        self.layout.addLayout(self.grid_layout)
        self.central_widget.setLayout(self.layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(112)  # Update interval in milliseconds, 112 ms for 28 samples at 250 SPS

        self.scan_devices()
    def create_toolbar(self):
        # Initialize the toolbar
        self.toolbar = self.addToolBar('Tools')
        
        # Create actions for the toolbar (without icons)
        connect_action = QAction('Conectarse al Dispositivo', self)
        connect_action.triggered.connect(self.scan_devices)
        self.toolbar.addAction(connect_action)

        patient_data_action = QAction('Datos del Paciente', self)
        patient_data_action.triggered.connect(self.input_patient_data)
        self.toolbar.addAction(patient_data_action)

        report_action = QAction('Generar Reporte', self)
        report_action.triggered.connect(self.read_last_values)
        self.toolbar.addAction(report_action)

    def update_plots(self):
        # Check if the BLE worker has been initialized and started
        if hasattr(self, 'ble_worker'):
            current_data1 = self.ecg_line1.getData()[1]
            updated_data1 = np.roll(current_data1, -28)
            updated_data1[-28:] = self.ble_worker.samples_array1
            self.ecg_line1.setData(updated_data1)
            self.plot_widget1.update()
            
            current_data2 = self.ecg_line2.getData()[1]
            updated_data2 = np.roll(current_data2, -28)
            updated_data2[-28:] = self.ble_worker.samples_array2
            self.ecg_line2.setData(updated_data2)
            self.plot_widget2.update()

            current_data3 = self.ecg_line3.getData()[1]
            updated_data3 = np.roll(current_data3, -28)
            updated_data3[-28:] = self.ble_worker.samples_array3
            self.ecg_line3.setData(updated_data3)
            self.plot_widget3.update()
            
            current_data4 = self.ecg_line4.getData()[1]
            updated_data4 = np.roll(current_data4, -28)
            updated_data4[-28:] = self.ble_worker.samples_array4
            self.ecg_line4.setData(updated_data4)
            self.plot_widget4.update()
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
        self.ble_worker.connection_status_signal.connect(self.handle_connection_status)
        self.ble_worker.error_signal.connect(self.handle_error_message)
        self.ble_worker.start()

    @pyqtSlot(bool)
    def handle_connection_status(self, is_connected):
        if is_connected:
            self.device_connection_dialog.close()
        else:
            self.device_connection_dialog.show()

    @pyqtSlot(str)
    def handle_error_message(self, message):
        self.device_connection_dialog.label.setText(message)
        QTimer.singleShot(3000, self.device_connection_dialog.close)  # Close dialog after 3 seconds

    @pyqtSlot()
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

        generate_ecg_report("output.pdf", last_values_ch1, last_values_ch2, last_values_ch3, last_values_ch4, last_values_ch5, last_values_ch6, last_values_ch7, last_values_ch8, self.patient_data_form.patient_data)
        # Show success dialog box and open PDF file
        QMessageBox.information(self, "Success", "Reporte generado exitosamente", QMessageBox.Ok)
        QDesktopServices.openUrl(QUrl.fromLocalFile("output.pdf"))

    @pyqtSlot()
    def input_patient_data(self):
        self.patient_data_form = PatientDataForm()
        if self.patient_data_form.exec_() == QDialog.Accepted:
            pass


# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppMainWindow()
    window.show()
    sys.exit(app.exec_())
