"""Dialog components for the ECG application."""

from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QSpinBox, QPushButton, QLabel, QVBoxLayout)
from PyQt5.QtCore import Qt
from ..data.models import PatientData


class PatientDataForm(QDialog):
    """Dialog for inputting patient data."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_data = PatientData()
        self.setWindowTitle("Datos del Paciente")
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the form layout."""
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
        """Gather form data and save to patient data model."""
        self.patient_data.first_name = self.first_name_input.text()
        self.patient_data.last_name = self.last_name_input.text()
        self.patient_data.gender = self.gender_input.currentText()
        self.patient_data.age = self.age_input.value()
        self.patient_data.height = self.height_input.value()
        self.patient_data.weight = self.weight_input.value()
        self.accept()
    
    def get_patient_data(self) -> PatientData:
        """Get the patient data model."""
        return self.patient_data


class DeviceConnectionDialog(QDialog):
    """Dialog showing device connection status."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Estado de la Conexión")
        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog layout."""
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Conectándose al dispositivo...", self)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
    
    def update_status(self, message: str):
        """Update the status message."""
        self.label.setText(message)