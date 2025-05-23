"""ECG plotting functionality."""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
import numpy as np
import datetime
import io
import os

from ..utils.constants import ECG_LEADS, LOGO_REPORT_PATH, GRID_COLORS
from ..bluetooth.data_processor import ECGDataProcessor
from ..data.models import PatientData


class ECGReportGenerator:
    """Generates PDF reports of ECG data."""
    
    def __init__(self):
        self.data_processor = ECGDataProcessor()
    
    def generate_report(self, output_path: str, channel_data: dict, patient_data: PatientData):
        """
        Generate a PDF report of ECG leads with patient information.
        
        Parameters:
        output_path (str): Path where the generated PDF will be saved
        channel_data (dict): Dictionary containing all channel data
        patient_data (PatientData): Patient information
        """
        # Set up the PDF buffer
        pdf_buffer = io.BytesIO()
        pdf = PdfPages(pdf_buffer)

        # Set up the figure layout
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 size

        # Load and place logo
        self._add_logo(fig)
        
        # Add title and patient information
        self._add_header_info(fig, patient_data)
        
        # Generate ECG plots
        self._generate_ecg_plots(fig, channel_data)

        # Adjust layout
        plt.tight_layout(w_pad=1, h_pad=0.5, rect=[0.03, 0.02, 0.97, 0.85])

        # Save the figure to the PDF and close
        pdf.savefig(fig)
        pdf.close()

        # Write buffer to file
        pdf_buffer.seek(0)
        with open(output_path, "wb") as f:
            f.write(pdf_buffer.read())
    
    def _add_logo(self, fig):
        """Add logo to the figure."""
        if os.path.exists(LOGO_REPORT_PATH):
            logo = mpimg.imread(LOGO_REPORT_PATH)
            fig.figimage(logo, xo=690, yo=1085)
    
    def _add_header_info(self, fig, patient_data: PatientData):
        """Add header information to the figure."""
        # Add title
        plt.figtext(0.045, 0.95, 'Reporte de 12 Derivadas', ha='left', va='center', 
                   fontsize=16, fontname='DIN Alternate')
        
        # Prepare patient information
        user_info = {
            "Nombres": patient_data.first_name,
            "Apellido": patient_data.last_name,
            "Género": patient_data.gender,
            "Edad": f"{patient_data.age} años",
            "Estatura": f"{patient_data.height} cm",
            "Peso": f"{patient_data.weight} kg",
            "Ritmo Cardíaco": "60 bpm",
            "Presión Sanguínea": "105/70 mmHg",
        }

        # Split user information into two columns
        left_user_info = {k: user_info[k] for k in list(user_info)[:4]}
        right_user_info = {k: user_info[k] for k in list(user_info)[4:]}
        
        # Get current date
        current_date = datetime.datetime.now().strftime("%B %d, %Y").title()

        # Add information to figure
        plt.figtext(0.05, 0.90, '\n'.join(f"{k}: {v}" for k, v in left_user_info.items()), 
                   ha='left', va='top', fontsize=10, fontname='DIN Alternate')
        plt.figtext(0.955, 0.90, '\n'.join(f"{k}: {v}" for k, v in right_user_info.items()), 
                   ha='right', va='top', fontsize=10, fontname='DIN Alternate')
        plt.figtext(0.5, 0.83, "Velocidad: 25 mm/sec, Amplitud: 10 mm/mV", 
                   ha='center', va='center', fontsize=8, fontname='DIN Alternate', color='gray')
        plt.figtext(0.05, 0.93, f"Fecha: {current_date}", 
                   ha='left', va='top', fontsize=10, fontname='DIN Alternate')
    
    def _generate_ecg_plots(self, fig, channel_data: dict):
        """Generate ECG plots for all leads."""
        # Define the grid for the plots
        grid_size = (6, 2)
        plot_positions = [(i, j) for i in range(6) for j in range(2)]

        # Define font properties
        title_font = {
            'family': 'DIN Alternate',
            'color': 'black',
            'weight': 'normal',
            'size': 10,
        }

        # Define common axis limits
        x_limit = (0, 750)
        y_limit = (-12000, 12000)

        for i, lead in enumerate(ECG_LEADS):
            row, col = plot_positions[i]
            ax = plt.subplot2grid(grid_size, (row, col), colspan=1)
            
            # Get lead data using the data processor
            lead_data = self.data_processor.get_lead_data(lead, channel_data)
            
            # Plot the data
            ax.plot(lead_data, 'k-', linewidth=0.5)
            ax.set_title(lead, fontdict=title_font)
            
            # Set axis limits
            ax.set_xlim(x_limit)
            ax.set_ylim(y_limit)
            
            # Remove tick labels
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            
            # Configure grid
            ax.grid(True, which='major', linestyle='-', linewidth=0.1, color=GRID_COLORS['major'])
            ax.grid(True, which='minor', linestyle=':', linewidth=0.05, color=GRID_COLORS['minor'])
            
            # Set grid locators
            ax.xaxis.set_major_locator(plt.MultipleLocator(50))
            ax.xaxis.set_minor_locator(plt.MultipleLocator(10))
            ax.yaxis.set_major_locator(plt.MultipleLocator(4000))
            ax.yaxis.set_minor_locator(plt.MultipleLocator(1000))
            
            # Customize borders
            border_width = 0.5
            border_color = 'lightgray'
            for spine in ax.spines.values():
                spine.set_linewidth(border_width)
                spine.set_edgecolor(border_color)