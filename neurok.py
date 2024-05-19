import neurokit2 as nk
import matplotlib.pyplot as plt
import numpy as np

# Load ECG data
with open('data_record_ch2.txt', 'r') as file:
    lines = file.readlines()
    start_index = max(0, len(lines) - 1750)
    ecg = np.array([float(line.strip()) for line in lines[start_index:]])

# Preprocess ECG signal
signals, info = nk.ecg_process(ecg, sampling_rate=250)

# Extracting the cleaned ECG and the R-peaks
cleaned_ecg = signals['ECG_Clean']
rpeaks = info['ECG_R_Peaks']
ppeaks = info['ECG_P_Peaks']
qpeaks = info['ECG_Q_Peaks']
tpeaks = info['ECG_T_Peaks']
speaks = info['ECG_S_Peaks']
# Print the attributes of 'info'
print("# Attributes of 'info':")
for key, value in info.items():
    print(f"{key}: {value}")
# Create a figure and a subplot
fig, ax = plt.subplots(figsize=(12, 4))

# Plot the cleaned ECG signal
ax.plot(cleaned_ecg, label='Cleaned ECG', color='blue')

# Mark R-peaks on the ECG
ax.scatter(rpeaks, cleaned_ecg.iloc[rpeaks], color='red', label='R-peaks')
ax.scatter(ppeaks, cleaned_ecg.iloc[ppeaks], color='green', label='P-peaks')
ax.scatter(qpeaks, cleaned_ecg.iloc[qpeaks], color='orange', label='Q-peaks')
ax.scatter(tpeaks, cleaned_ecg.iloc[tpeaks], color='purple', label='T-peaks')
ax.scatter(speaks, cleaned_ecg.iloc[speaks], color='cyan', label='S-peaks')

# Enhance the plot
ax.set_title('Lead II ECG Signal with Peaks')
ax.set_xlabel('Samples')
ax.set_ylabel('Amplitude')
ax.legend()

# Show the plot
plt.show()
