import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_prominences, butter, filtfilt

# Load ECG data
with open('data_record_ch2.txt', 'r') as file:
    lines = file.readlines()
    start_index = max(0, len(lines) - 1750)
    ecg = np.array([float(line.strip()) for line in lines[start_index:]])

# Define the sampling rate (in Hz)
sampling_rate = 250

# Define the cutoff frequency for the low-pass filter (in Hz)
cutoff_frequency = 20

# Calculate the Nyquist frequency
nyquist_frequency = 0.5 * sampling_rate

# Calculate the normalized cutoff frequency (Wn) for the filter
normalized_cutoff_frequency = cutoff_frequency / nyquist_frequency

# Design a Butterworth low-pass filter
b, a = butter(N=4, Wn=normalized_cutoff_frequency, btype='low')

# Apply the filter to the ECG data using filtfilt (zero-phase filtering)
filtered_ecg = filtfilt(b, a, ecg)

# Plot the original and filtered ECG data
plt.figure(figsize=(12, 6))
plt.plot(ecg, label='Original ECG')
plt.plot(filtered_ecg, label='Filtered ECG')
plt.legend()
plt.title('ECG Data Before and After Low-Pass Filtering')
plt.xlabel('Sample Number')
plt.ylabel('Amplitude')
plt.show()