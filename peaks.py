import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_prominences

# Load ECG data
with open('data_record_ch2.txt', 'r') as file:
    lines = file.readlines()
    start_index = max(0, len(lines) - 1750)
    ecg = np.array([float(line.strip()) for line in lines[start_index:]])

# Define the sampling rate (in Hz)
sampling_rate = 250 

# Find peaks
peaks, _ = find_peaks(ecg, height=0, distance=200)

# Calculate prominences
prominences = peak_prominences(ecg, peaks)[0]

# Calculate heart rate
if len(peaks) > 1:
    # Calculate the differences between successive peaks (inter-beat intervals)
    inter_beat_intervals = np.diff(peaks) / sampling_rate
    
    # Calculate the average inter-beat interval
    avg_ibi = np.mean(inter_beat_intervals)
    
    # Calculate heart rate in beats per minute
    heart_rate = 60 / avg_ibi
    print(f"Heart Rate: {heart_rate:.2f} BPM")
else:
    print("Not enough peaks detected to calculate heart rate.")
    
# Plot ECG data
plt.plot(ecg)
plt.plot(peaks, ecg[peaks], "x")
plt.show()


