"""Main application window."""

import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QLabel, QAction, QMessageBox)
from PyQt5.QtGui import QPixmap, QFont, QDesktopServices
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QUrl
import pyqtgraph as pg

from ..ui.dialogs import PatientDataForm, DeviceConnectionDialog
from ..bluetooth.ble_worker import BLEWorker
from ..plotting.ecg_plots import ECGReportGenerator
from ..data.file_manager import ECGFileManager
from ..data.models import PatientData
from ..utils.constants import (TARGET_ADDRESS, CHANNEL_UUIDS, PLOT_UPDATE_INTERVAL,
                              PLOT_LIMITS, LOGO_CUT_PATH)


class AppMainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.device_connection_dialog = DeviceConnectionDialog()
        self.patient_data = PatientData()
        self.file_manager = ECGFileManager()
        self.report_generator = ECGReportGenerator()
        self.ble_worker = None
        
        self.setup_ui()
        self.setup_plots()
        self.setup_timer()
        self.scan_devices()
    
    def setup_ui(self):
        """Set up the main window UI."""
        self.setWindowTitle('Generador de Reportes ECG v0.1')
        self.setGeometry(100, 100, 1024, 400)
        
        # Central widget setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        
        # Top layout with title and logo
        self.setup_header()
        
        # Grid layout for plots
        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)
        
        # Set layout
        self.central_widget.setLayout(self.layout)
        
        # Create toolbar
        self.create_toolbar()
    
    def setup_header(self):
        """Set up the header with title and logo."""
        self.top_layout = QHBoxLayout()
        
        # Title
        self.label_title = QLabel('Generador de Reportes ECG', self)
        self.label_title.setAlignment(Qt.AlignLeft)
        font = QFont()
        font.setPointSize(18)
        self.label_title.setFont(font)
        
        # Logo
        self.label_image = QLabel(self)
        try:
            self.pixmap = QPixmap(LOGO_CUT_PATH)
            self.label_image.setPixmap(self.pixmap)
        except:
            pass  # Logo file not found, continue without it
        self.label_image.setAlignment(Qt.AlignRight)
        
        self.top_layout.addWidget(self.label_title)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.label_image)
        self.layout.addLayout(self.top_layout)
    
    def setup_plots(self):
        """Set up the ECG plot widgets."""
        self.plot_widgets = []
        self.ecg_lines = []
        
        for i in range(4):  # First 4 channels for display
            plot_widget = pg.PlotWidget()
            plot_widget.setLimits(
                xMin=PLOT_LIMITS['x'][0], 
                xMax=PLOT_LIMITS['x'][1],
                yMin=PLOT_LIMITS['y'][0], 
                yMax=PLOT_LIMITS['y'][1]
            )
            plot_widget.showGrid(x=True, y=True)
            plot_widget.setBackground('w')
            
            ecg_line = plot_widget.plot(np.zeros(PLOT_LIMITS['x'][1]), pen=pg.mkPen('k', width=2))
            
            # Add to grid layout
            row = 0
            col = i
            self.grid_layout.addWidget(plot_widget, row, col)
            
            self.plot_widgets.append(plot_widget)
            self.ecg_lines.append(ecg_line)
    
    def setup_timer(self):
        """Set up the plot update timer."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(PLOT_UPDATE_INTERVAL)
    
    def create_toolbar(self):
        """Create the application toolbar."""
        self.toolbar = self.addToolBar('Tools')
        
        # Connect to device action
        connect_action = QAction('Conectarse al Dispositivo', self)
        connect_action.triggered.connect(self.scan_devices)
        self.toolbar.addAction(connect_action)

        # Patient data action
        patient_data_action = QAction('Datos del Paciente', self)
        patient_data_action.triggered.connect(self.input_patient_data)
        self.toolbar.addAction(patient_data_action)

        # Generate report action
        report_action = QAction('Generar Reporte', self)
        report_action.triggered.connect(self.generate_report)
        self.toolbar.addAction(report_action)

    def update_plots(self):
        """Update the ECG plots with new data."""
        if self.ble_worker is not None:
            for i in range(4):  # Update first 4 channels
                try:
                    current_data = self.ecg_lines[i].getData()[1]
                    updated_data = np.roll(current_data, -28)  # Shift data left by 28 samples
                    
                    # Get new samples from BLE worker
                    new_samples = self.ble_worker.get_samples_array(i + 1)
                    updated_data[-28:] = new_samples
                    
                    self.ecg_lines[i].setData(updated_data)
                    self.plot_widgets[i].update()
                except (AttributeError, IndexError):
                    pass  # Handle cases where data might not be available yet

    @pyqtSlot()
    def scan_devices(self):
        """Scan and connect to BLE devices."""
        if self.ble_worker is not None:
            self.ble_worker.terminate()
            self.ble_worker.wait()
        
        self.ble_worker = BLEWorker(TARGET_ADDRESS, CHANNEL_UUIDS)
        self.ble_worker.connection_status_signal.connect(self.handle_connection_status)
        self.ble_worker.error_signal.connect(self.handle_error_message)
        self.ble_worker.start()

    @pyqtSlot(bool)
    def handle_connection_status(self, is_connected):
        """Handle BLE connection status changes."""
        if is_connected:
            self.device_connection_dialog.close()
        else:
            self.device_connection_dialog.show()

    @pyqtSlot(str)
    def handle_error_message(self, message):
        """Handle error messages from BLE worker."""
        self.device_connection_dialog.update_status(message)
        QTimer.singleShot(3000, self.device_connection_dialog.close)

    @pyqtSlot()
    def generate_report(self):
        """Generate ECG report."""
        try:
            # Read latest data from all channels
            channel_data = self.file_manager.read_all_last_values()
            
            # Generate report
            output_path = self.file_manager.get_report_output_path("output.pdf")
            self.report_generator.generate_report(output_path, channel_data, self.patient_data)
            
            # Show success message and open PDF
            QMessageBox.information(self, "Success", "Reporte generado exitosamente", QMessageBox.Ok)
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generando reporte: {str(e)}")

    @pyqtSlot()
    def input_patient_data(self):
        """Open patient data input dialog."""
        patient_form = PatientDataForm(self)
        if patient_form.exec_() == patient_form.Accepted:
            self.patient_data = patient_form.get_patient_data()
    
    def closeEvent(self, event):
        """Handle application close event."""
        if self.ble_worker is not None:
            self.ble_worker.terminate()
            self.ble_worker.wait()
        event.accept()