import numpy as np
from scipy.signal import butter, filtfilt

def filter_ecg(ecg_data):
    """
    Apply a low-pass Butterworth filter to ECG data with a fixed sampling rate of 250 Hz
    and a cutoff frequency of 40 Hz.

    Parameters:
    ecg_data (numpy.ndarray): The raw ECG data.

    Returns:
    numpy.ndarray: The filtered ECG data.
    """
    # Define the sampling rate and cutoff frequency
    sampling_rate = 250  # in Hz
    cutoff_frequency = 40  # in Hz

    # Calculate the Nyquist frequency
    nyquist_frequency = 0.5 * sampling_rate

    # Calculate the normalized cutoff frequency (Wn) for the filter
    normalized_cutoff_frequency = cutoff_frequency / nyquist_frequency

    # Design a Butterworth low-pass filter
    b, a = butter(N=4, Wn=normalized_cutoff_frequency, btype='low')

    # Apply the filter to the ECG data using filtfilt (zero-phase filtering)
    filtered_ecg = filtfilt(b, a, ecg_data)

    return filtered_ecg

# Example usage:
if __name__ == "__main__":
    # Load ECG data
    with open('data_record_ch2.txt', 'r') as file:
        lines = file.readlines()
        start_index = max(0, len(lines) - 1750)
        ecg = np.array([float(line.strip()) for line in lines[start_index:]])

    # Filter the ECG data
    filtered_ecg = filter_ecg(ecg)

    # Plot the original and filtered ECG data
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 6))
    plt.plot(ecg, label='Original ECG')
    plt.plot(filtered_ecg, label='Filtered ECG')
    plt.legend()
    plt.title('ECG Data Before and After Low-Pass Filtering')
    plt.xlabel('Sample Number')
    plt.ylabel('Amplitude')
    plt.show()
