"""Helper functions for the ECG application."""

import numpy as np
from scipy.signal import butter, filtfilt
from .constants import SAMPLING_RATE, LOWPASS_CUTOFF_FREQUENCY, FILTER_ORDER


def filter_ecg(ecg_data):
    """
    Apply a low-pass Butterworth filter to ECG data.

    Parameters:
    ecg_data (numpy.ndarray): The raw ECG data.

    Returns:
    numpy.ndarray: The filtered ECG data.
    """
    # Calculate the Nyquist frequency
    nyquist_frequency = 0.5 * SAMPLING_RATE

    # Calculate the normalized cutoff frequency (Wn) for the filter
    normalized_cutoff_frequency = LOWPASS_CUTOFF_FREQUENCY / nyquist_frequency

    # Design a Butterworth low-pass filter
    b, a = butter(N=FILTER_ORDER, Wn=normalized_cutoff_frequency, btype='low')

    # Apply the filter to the ECG data using filtfilt (zero-phase filtering)
    filtered_ecg = filtfilt(b, a, ecg_data)

    return filtered_ecg


def process_24bit_data(data_bytes):
    """
    Process 24-bit data from BLE device.
    
    Parameters:
    data_bytes (bytes): Raw bytes from BLE device
    
    Returns:
    list: Processed data array
    """
    data_array = []
    for index in range(0, len(data_bytes), 3):
        if index + 3 <= len(data_bytes):
            byte1, byte2, byte3 = data_bytes[index:index+3]
            value_24bit = (byte1 << 16) | (byte2 << 8) | byte3
            if value_24bit & 0x800000:
                value_24bit = value_24bit - 0x1000000
            data_array.append(value_24bit)
    return data_array


def apply_baseline_wander_removal(data_array, samples_array, last_data_previous, last_y_previous, alpha=0.995):
    """
    Apply baseline wander removal to ECG data.
    
    Parameters:
    data_array (list): Input data array
    samples_array (numpy.ndarray): Output samples array
    last_data_previous (float): Last data value from previous buffer
    last_y_previous (float): Last y value from previous buffer
    alpha (float): Alpha parameter for filter
    
    Returns:
    tuple: (updated_samples_array, new_last_data_previous, new_last_y_previous)
    """
    for i in range(len(data_array)):
        if i == 0:
            samples_array[i] = data_array[i] - last_data_previous + alpha * last_y_previous
            last_data_previous = data_array[i]
            last_y_previous = samples_array[i]
        else:
            samples_array[i] = data_array[i] - data_array[i - 1] + alpha * samples_array[i - 1]
            data_array[i - 1] = data_array[i]
            samples_array[i - 1] = samples_array[i]
    
    return samples_array, data_array[-1], samples_array[-1]