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

class BLEWorker(QThread):
    def __init__(self, address, channel1_uuid, channel2_uuid):
        super().__init__()
        self.address = address
        self.channel1_uuid = channel1_uuid
        self.channel2_uuid = channel2_uuid
        self.samples_array1 = np.zeros(28)
        self.samples_array2 = np.zeros(28)
        self.last_data_previous1 = 0
        self.last_y_previous1 = 0 
        self.last_data_previous2 = 0
        self.last_y_previous2 = 0 

    async def notification_handler(self, sender, data):
        hex_data = data.hex()

        # Convert hex string to bytes
        data_bytes = bytes.fromhex(hex_data)

        # Prepare an empty list to store the converted 24-bit integers
        data_array = []

        # Iterate over each 3-byte sequence in the data
        for index in range(0, len(data_bytes), 3):
            # Make sure there are enough bytes left to form a complete 24-bit integer
            if index + 3 <= len(data_bytes):
                # Extract 3 bytes
                byte1, byte2, byte3 = data_bytes[index:index+3]
                
                # Convert them to a 24-bit integer assuming incoming data is big-endian
                value_24bit = (byte1 << 16) | (byte2 << 8) | byte3

                # Check if the 24-bit integer should be negative
                if value_24bit & 0x800000:
                    # Sign extend to 32 bits by setting the upper 8 bits
                    value_24bit = value_24bit - 0x1000000

                # Append the result to the data_array
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
                self.samples_array1[i - 1] = self.samples_array1 [i]
                
        self.last_data_previous1 = data_array[-1]
        self.last_y_previous1 = self.samples_array1[-1]
    
    async def notification_handler2(self, sender, data):
        hex_data = data.hex()

        # Convert hex string to bytes
        data_bytes = bytes.fromhex(hex_data)

        # Prepare an empty list to store the converted 24-bit integers
        data_array = []

        # Iterate over each 3-byte sequence in the data
        for index in range(0, len(data_bytes), 3):
            # Make sure there are enough bytes left to form a complete 24-bit integer
            if index + 3 <= len(data_bytes):
                # Extract 3 bytes
                byte1, byte2, byte3 = data_bytes[index:index+3]
                
                # Convert them to a 24-bit integer assuming incoming data is big-endian
                value_24bit = (byte1 << 16) | (byte2 << 8) | byte3

                # Check if the 24-bit integer should be negative
                if value_24bit & 0x800000:
                    # Sign extend to 32 bits by setting the upper 8 bits
                    value_24bit = value_24bit - 0x1000000

                # Append the result to the data_array
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
                self.samples_array2[i - 1] = self.samples_array2 [i]
                
        self.last_data_previous2 = data_array[-1]
        self.last_y_previous2 = self.samples_array2[-1]
        
    async def connect_to_ble_device(self):
        try:
            async with BleakClient(self.address) as client:
                if await client.is_connected():
                    print(f"Connected to {self.address}")
                    
                    await client.start_notify(self.channel1_uuid, self.notification_handler)
                    print(f"Notifications enabled for characteristic {self.channel1_uuid}")
                    await client.start_notify(self.channel2_uuid, self.notification_handler2)
                    print(f"Notifications enabled for characteristic {self.channel2_uuid}")
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

        # Create a grid layout for the ECG plot
        self.grid_layout = QGridLayout()

        # Generate and add a single Matplotlib figure to the grid layout
        self.fig = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(121)
        self.ecg_line1, = self.ax.plot(np.zeros(375), 'k-', linewidth=0.5)  # Initialize with zeros
        self.ax.set_xlim(0, 375)
        self.ax.set_ylim(-15000, 15000)
        self.ax.grid(True, which='major', linestyle='-', linewidth=0.1, color='lightgray')
        self.ax.grid(True, which='minor', linestyle=':', linewidth=0.05, color='lightgray')
        self.ax.xaxis.set_major_locator(MultipleLocator(25))
        self.ax.xaxis.set_minor_locator(MultipleLocator(5))
        self.ax.yaxis.set_major_locator(MultipleLocator(4000))
        self.ax.yaxis.set_minor_locator(MultipleLocator(1000))

        # Remove y and x axis labels
        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])

        # Second plot (Additional Plot)
        self.ax2 = self.fig.add_subplot(122)  # Second subplot in the first row
        self.ecg_line2, = self.ax2.plot(np.zeros(375), 'k-', linewidth=0.5)  # Initialize with zeros
        self.ax2.set_xlim(0, 375)  # Set x-axis limits
        self.ax2.set_ylim(-15000, 15000)  # Set y-axis limits
        self.ax2.grid(True, which='major', linestyle='-', linewidth=0.1, color='lightgray')
        self.ax2.grid(True, which='minor', linestyle=':', linewidth=0.05, color='lightgray')
        self.ax2.xaxis.set_major_locator(MultipleLocator(25))
        self.ax2.xaxis.set_minor_locator(MultipleLocator(5))
        self.ax2.yaxis.set_major_locator(MultipleLocator(4000))
        self.ax2.yaxis.set_minor_locator(MultipleLocator(1000))

        # Remove y and x axis labels for the second plot
        self.ax2.set_yticklabels([])
        self.ax2.set_xticklabels([])

        # Add the canvas to the grid layout
        self.grid_layout.addWidget(self.canvas, 0, 0)  # Single plot

        # Add the grid layout to the main layout
        self.layout.addLayout(self.grid_layout)

        # Set the layout for the central widget
        self.central_widget.setLayout(self.layout)

        # Timer for updating the plot
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(112)  # Update interval in milliseconds, 112 ms for 28 samples at 250 SPS

    def update_plots(self):
       # Check if the BLE worker has been initialized and started
        if hasattr(self, 'ble_worker'):
            # Ensure that samples_array has exactly 28 samples
            if len(self.ble_worker.samples_array1) != 28:
                raise ValueError("samples_array must contain exactly 28 samples")

            current_data1 = self.ecg_line1.get_ydata()
            updated_data1 = np.concatenate((current_data1[28:], self.ble_worker.samples_array1))
            self.ecg_line1.set_ydata(updated_data1)

            current_data2 = self.ecg_line2.get_ydata()
            updated_data2 = np.concatenate((current_data2[28:], self.ble_worker.samples_array2))
            self.ecg_line2.set_ydata(updated_data2)
            
            self.canvas.draw()
        else:
            # The ble_worker does not exist yet, so we can't update the plots.
            # This would be a good place to handle this case, such as by logging a message or initializing the plot with zeros.
            pass

    @pyqtSlot()
    def scan_devices(self):
        target_address = "6614D41F-1CB3-77FA-3E35-C5A446EA4E3F"
        channel1_uuid = "00008171-0000-1000-8000-00805f9b34fb"
        channel2_uuid = "00008172-0000-1000-8000-00805f9b34fb"
        self.ble_worker = BLEWorker(target_address, channel1_uuid, channel2_uuid)
        self.ble_worker.start()

# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppMainWindow()
    window.show()
    sys.exit(app.exec_())
