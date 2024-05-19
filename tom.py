from ecgdetectors import Detectors
import matplotlib.pyplot as plt
import numpy as np

# Load ECG data
with open('data_record_ch1.txt', 'r') as file:
    lines = file.readlines()
    start_index = max(0, len(lines) - 1750)
    unfiltered_ecg = np.array([float(line.strip()) for line in lines[start_index:]])
    
# Initialize detectors with the sampling rate of your ECG signal
fs = 250
detectors = Detectors(fs)

# Use the Pan-Tompkins detector to find R-peaks
r_peaks = detectors.pan_tompkins_detector(unfiltered_ecg)

# Plot the unfiltered ECG signal
plt.figure(figsize=(10, 6))
plt.plot(unfiltered_ecg, label="ECG signal")

# Plot the R-peaks on the ECG signal
plt.plot(r_peaks, unfiltered_ecg[r_peaks], "ro", label="R-peaks")

plt.title("ECG signal with R-peaks")
plt.xlabel("Time (samples)")
plt.ylabel("Amplitude")
plt.legend()
plt.show()