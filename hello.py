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

samples_array = np.zeros(28)

class BLEWorker(QThread):
    def __init__(self, address, characteristic_uuid):
        super().__init__()
        self.address = address
        self.characteristic_uuid = characteristic_uuid

    async def notification_handler(self, sender, data):
        hex_data = data.hex()
        # print(f"Notification from {sender}: Value (hex): {hex_data}")

        # Convert hex string to bytes
        data_bytes = bytes.fromhex(hex_data)

        # Prepare an empty list to store the converted 16-bit integers
        data_array = []

        # Iterate over each 3-byte sequence in the data
        for index in range(0, len(data_bytes), 3):
            # Extract 3 bytes and convert them to a 24-bit integer
            value_24bit = (data_bytes[index] << 16) | (data_bytes[index + 1] << 8) | data_bytes[index + 2]

            # Sign extend to 32 bits to get a negative number if the sign bit is set
            # Then right shift to discard the lower 8 bits, effectively converting to 16-bit signed integer
            value_16bit = ((value_24bit & 0xFFFFFF) ^ 0x800000) - 0x800000
            value_16bit >>= 8

            # Append the result to the data_array
            data_array.append(value_16bit)

        # Print the resulting array of 16-bit signed integers
        samples_array = data_array
        print(samples_array)
        

    async def connect_to_ble_device(self):
        try:
            async with BleakClient(self.address) as client:
                if await client.is_connected():
                    print(f"Connected to {self.address}")
                    
                    await client.start_notify(self.characteristic_uuid, self.notification_handler)
                    print(f"Notifications enabled for characteristic {self.characteristic_uuid}")

                    print("Listening for notifications...")
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
        self.setGeometry(100, 100, 800, 600)  # Increased size for ECG plots

        # Create a central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout
        self.layout = QVBoxLayout()

        # Create a horizontal layout for the title and logo
        self.top_layout = QHBoxLayout()

        # Create a label for the title
        self.label_title = QLabel('ECG Report Generator', self)
        self.label_title.setAlignment(Qt.AlignLeft)

        # Set the font size for the title
        font = QFont()
        font.setPointSize(18)
        self.label_title.setFont(font)

        # Create a label for the image (logo)
        self.label_image = QLabel(self)
        self.pixmap = QPixmap('logocut.png')
        self.label_image.setPixmap(self.pixmap)
        self.label_image.setAlignment(Qt.AlignRight)

        # Add the title and image to the top layout
        self.top_layout.addWidget(self.label_title)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.label_image)

        # Create a button for scanning devices
        self.button_scan = QPushButton('CONNECT TO DEVICE', self)
        self.button_scan.clicked.connect(self.scan_devices)

        # Add the top layout and button to the main layout
        self.layout.addLayout(self.top_layout)
        self.layout.addWidget(self.button_scan)

        # Create a grid layout for the ECG plots
        self.grid_layout = QGridLayout()

        # Generate and add 12 Matplotlib figures to the grid layout
        self.leads = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
        self.figures = []
        self.canvases = []
        self.axes = []
        self.ecg_data = []  # Store initial random ECG data for each plot
        for i, lead in enumerate(self.leads):
            fig = Figure(figsize=(5, 3))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ecg_line, = ax.plot(np.zeros(375), 'k-', linewidth=0.5)  # Initialize with zeros
            ax.set_title(lead, y=1.02, x=0.05, pad=-10, fontsize=10)
            ax.set_xlim(0, 375)
            ax.set_ylim(-30, 30)
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.grid(True, which='major', linestyle='-', linewidth=0.1, color='lightgray')
            ax.grid(True, which='minor', linestyle=':', linewidth=0.05, color='lightgray')
            ax.xaxis.set_major_locator(MultipleLocator(25))
            ax.xaxis.set_minor_locator(MultipleLocator(5))
            ax.yaxis.set_major_locator(MultipleLocator(10))
            ax.yaxis.set_minor_locator(MultipleLocator(2))
            for spine in ax.spines.values():
                spine.set_linewidth(0.5)
                spine.set_edgecolor('lightgray')
            self.figures.append(fig)
            self.canvases.append(canvas)
            self.axes.append(ax)
            self.ecg_data.append(ecg_line)
            self.grid_layout.addWidget(canvas, i // 2, i % 2)  # 6 rows, 2 columns

        # Add the grid layout to the main layout
        self.layout.addLayout(self.grid_layout)

        # Set the layout for the central widget
        self.central_widget.setLayout(self.layout)

        # Timer for updating the plots
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(250)  # Update interval in milliseconds

    def scan_devices(self):
        # Placeholder for the method to scan devices
        print("Scanning for devices...")

    def update_plots(self):
       # Indicate that we are using the global samples_array variable
        global samples_array

        # Ensure that samples_array has exactly 28 samples
        if len(samples_array) != 28:
            raise ValueError("samples_array must contain exactly 28 samples")

        # Shift data to the left and append new samples from samples_array on the right
        for ecg_line in self.ecg_data:
            current_data = ecg_line.get_ydata()
            updated_data = np.concatenate((current_data[28:], samples_array))  # Remove the first 28 and append new ones
            ecg_line.set_ydata(updated_data)
            ecg_line.figure.canvas.draw()
            
    @pyqtSlot()
    def scan_devices(self):
        target_address = "6614D41F-1CB3-77FA-3E35-C5A446EA4E3F"
        characteristic_uuid = "00008171-0000-1000-8000-00805f9b34fb"
        self.ble_worker = BLEWorker(target_address, characteristic_uuid)
        self.ble_worker.start()

# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppMainWindow()
    window.show()
    sys.exit(app.exec_())
