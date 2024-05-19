# ecg_report_generator.py

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import io
import matplotlib.image as mpimg
from lowpass import filter_ecg
import datetime

# Define the user information and the leads
user_info = {
    "First Name": "Ashish",
    "Last Name": "Yadav",
    "Gender": "Male",
    "Age": "31 years",
    "Height": "156 cm",
    "Weight": "60 kg",
    "Heart Rate": "60 bpm",
    "Blood Pressure": "105/70 mmHg"
}

leads = ["I", "aVR", "II", "aVF", "III", "aVL", "V1", "V4", "V2", "V5", "V3", "V6"]

output_path = "output.pdf"

def generate_ecg_report(output_path, last_values_ch1, last_values_ch2, last_values_ch3, last_values_ch4, last_values_ch5, last_values_ch6, last_values_ch7, last_values_ch8, patient_data):
    """
    Generates a PDF report of ECG leads with user information.

    Parameters:
    - user_info: dict containing user's personal information
    - leads: list of lead names to be included in the report
    - logo_path: path to the logo image file
    - output_path: path where the generated PDF will be saved
    """
    # Extract patient data
    first_name = patient_data.get('first_name', 'N/A')
    last_name = patient_data.get('last_name', 'N/A')
    gender = patient_data.get('gender', 'N/A')
    age = patient_data.get('age', 'N/A')
    height = patient_data.get('height', 'N/A')
    weight = patient_data.get('weight', 'N/A')

    # Set up the PDF buffer
    pdf_buffer = io.BytesIO()
    pdf = PdfPages(pdf_buffer)

    # Set up the figure layout
    fig = plt.figure(figsize=(8.27, 11.69))  # A4 size

    # Define logo image
    logo = mpimg.imread("logoreport.png")

    # Place the logo on the figure at the specified location
    fig.figimage(logo, xo=690, yo=1085)

    # Add the title and logo
    plt.figtext(0.045, 0.95, '12 Lead Report', ha='left', va='center', fontsize=16, fontname='DIN Alternate')

    # Combine patient data
    user_info = {
        "First Name": first_name,
        "Last Name": last_name,
        "Gender": gender,
        "Age": f"{age} years",
        "Height": f"{height} cm",
        "Weight": f"{weight} kg",
        "Heart Rate": "60 bpm",  # Assuming heart rate is not provided in patient_data
        "Blood Pressure": "105/70 mmHg",  # Assuming blood pressure is not provided in patient_data
    }

    # Split user information into two parts
    left_user_info = {k: user_info[k] for k in list(user_info)[:4]}
    right_user_info = {k: user_info[k] for k in list(user_info)[4:]}
    
    # Get the current date
    current_date = datetime.datetime.now().strftime("%B %d, %Y")

    # Add the user information on the left
    plt.figtext(0.05, 0.90, '\n'.join(f"{k}: {v}" for k, v in left_user_info.items()), ha='left', va='top', fontsize=10, fontname='DIN Alternate')

    # Add the user information on the right
    plt.figtext(0.955, 0.90, '\n'.join(f"{k}: {v}" for k, v in right_user_info.items()), ha='right', va='top', fontsize=10, fontname='DIN Alternate')

    plt.figtext(0.5, 0.83, "Speed: 25 mm/sec, Amplitude: 10 mm/mV", ha='center', va='center', fontsize=8, fontname='DIN Alternate', color='gray')
    plt.figtext(0.05, 0.93, f"Date: {current_date}", ha='left', va='top', fontsize=10, fontname='DIN Alternate')

    # Define the grid for the plots
    grid_size = (6, 2)
    plot_positions = [(i, j) for i in range(6) for j in range(2)]

    # Define the font properties using a dictionary
    title_font = {
        'family': 'DIN Alternate',
        'color': 'black',
        'weight': 'normal',
        'size': 10,
    }

    # Define common x and y-axis limits
    x_limit = (0, 750)
    y_limit = (-12000, 12000)

    # Define colors for major and minor grid lines
    major_grid_color = 'lightgray'   # Change to your preferred color for major grid lines
    minor_grid_color = 'lightgray' # Change to your preferred color for minor grid lines

    for i, lead in enumerate(leads):
        row, col = plot_positions[i]
        ax = plt.subplot2grid(grid_size, (row, col), colspan=1)
        if lead == "I":
            ax.plot(filter_ecg(last_values_ch1), 'k-', linewidth=0.5)
            ax.set_title(lead, fontdict=title_font)
        if lead == "II":
            ax.plot(filter_ecg(last_values_ch2), 'k-', linewidth=0.5)
            ax.set_title(lead, fontdict=title_font)
        if lead == "III":
            # Convert lists to NumPy arrays and perform element-wise subtraction
            derived_ecg_data = filter_ecg(np.array(last_values_ch2) - np.array(last_values_ch1))
            ax.plot(derived_ecg_data, 'k-', linewidth=0.5)  # Derived ECG data
            ax.set_title(lead, fontdict=title_font)
        if lead == "aVR":
            # Convert lists to NumPy arrays and perform element-wise subtraction
            derived_ecg_data = filter_ecg((np.array(last_values_ch1) + np.array(last_values_ch2))/2)
            ax.plot(derived_ecg_data, 'k-', linewidth=0.5)  # Derived ECG data
            ax.set_title(lead, fontdict=title_font)
        if lead == "aVL":
            # Convert lists to NumPy arrays and perform element-wise subtraction
            derived_ecg_data = filter_ecg(np.array(last_values_ch1) - np.array(last_values_ch2)/2)
            ax.plot(derived_ecg_data, 'k-', linewidth=0.5)  # Derived ECG data
            ax.set_title(lead, fontdict=title_font)
        if lead == "aVF":
            # Convert lists to NumPy arrays and perform element-wise subtraction
            derived_ecg_data = filter_ecg(np.array(last_values_ch2) - np.array(last_values_ch1)/2)
            ax.plot(derived_ecg_data, 'k-', linewidth=0.5)  # Derived ECG data
            ax.set_title(lead, fontdict=title_font)
        if lead == "V1":
            ax.plot(filter_ecg(last_values_ch3), 'k-', linewidth=0.5)
            ax.set_title(lead, fontdict=title_font)
        if lead == "V2":
            ax.plot(filter_ecg(last_values_ch4), 'k-', linewidth=0.5)
            ax.set_title(lead, fontdict=title_font)
        if lead == "V3":
            ax.plot(filter_ecg(last_values_ch5), 'k-', linewidth=0.5)
            ax.set_title(lead, fontdict=title_font)
        if lead == "V4":
            ax.plot(filter_ecg(last_values_ch6), 'k-', linewidth=0.5)
            ax.set_title(lead, fontdict=title_font)
        if lead == "V5":
            ax.plot(filter_ecg(last_values_ch7), 'k-', linewidth=0.5)
            ax.set_title(lead, fontdict=title_font)
        if lead == "V6":
            ax.plot(filter_ecg(last_values_ch8), 'k-', linewidth=0.5)
            ax.set_title(lead, fontdict=title_font)
        
        # Set the same x and y-axis limits for all plots
        ax.set_xlim(x_limit)
        ax.set_ylim(y_limit) 
        
        # Remove the tick labels for both axes
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
        # Enable and customize the major grid
        ax.grid(True, which='major', linestyle='-', linewidth=0.1, color=major_grid_color)
        
        # Enable and customize the minor grid
        ax.grid(True, which='minor', linestyle=':', linewidth=0.05, color=minor_grid_color)
        
        # Set major locator for x and y axis
        ax.xaxis.set_major_locator(plt.MultipleLocator(50))
        ax.xaxis.set_minor_locator(plt.MultipleLocator(10))
        ax.yaxis.set_major_locator(plt.MultipleLocator(4000))
        ax.yaxis.set_minor_locator(plt.MultipleLocator(1000))
        
        # Customize border width and color
        border_width = 0.5  # Specify the desired border width here
        border_color = 'lightgray'
        for spine in ax.spines.values():
            spine.set_linewidth(border_width)
            spine.set_edgecolor(border_color)
        
    # Adjust layout
    plt.tight_layout(w_pad=1, h_pad=0.5, rect=[0.03, 0.02, 0.97, 0.85])

    # Save the figure to the PDF and close the object
    pdf.savefig(fig)
    pdf.close()

    # Write buffer to file for download
    pdf_buffer.seek(0)
    with open(output_path, "wb") as f:
        f.write(pdf_buffer.read())

# Example usage:
# user_info = {...}  # User information dictionary
# leads = [...]      # List of lead names
# generate_ecg_report(user_info, leads, 'logocut.png', 'output.pdf')
