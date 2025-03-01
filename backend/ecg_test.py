import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import pandas as pd
import os

# Function to load ECG data from a CSV file
def load_ecg_data(file_path):
    data = pd.read_csv(file_path)
    timestamps = data.iloc[:, 0].values
    ecg_values = data.iloc[:, 1].values
    return timestamps, ecg_values

# Function to load formulas from a CSV file
def load_formulas(file_path):
    formulas = pd.read_csv(file_path)
    return formulas

# Function to compute ECG features using the provided formulas
def compute_ecg_features(timestamps, ecg_values):
    # Normalize timestamps (shift so the first time starts at zero)
    timestamps = timestamps - timestamps[0]

    # Find R-peaks (highest points in ECG)
    r_peaks, _ = find_peaks(ecg_values, height=np.mean(ecg_values) + 20)

    # Find Q-peaks (local minima before each R-peak)
    q_peaks = []
    for r_idx in r_peaks:
        search_window = range(max(0, r_idx - 10), r_idx)
        if len(search_window) > 0:
            q_idx = search_window[np.argmin(ecg_values[search_window])]
            q_peaks.append(q_idx)

    q_peaks = np.array(q_peaks)

    # Find P-peaks (local maxima before Q-peak)
    p_peaks = []
    for q_idx in q_peaks:
        search_window = range(max(0, q_idx - 15), q_idx)
        if len(search_window) > 0:
            p_idx = search_window[np.argmax(ecg_values[search_window])]
            p_peaks.append(p_idx)

    p_peaks = np.array(p_peaks)

    # Find S-peaks (local minima after R-peak)
    s_peaks = []
    for r_idx in r_peaks:
        search_window = range(r_idx, min(len(ecg_values), r_idx + 10))
        if len(search_window) > 0:
            s_idx = search_window[np.argmin(ecg_values[search_window])]
            s_peaks.append(s_idx)

    s_peaks = np.array(s_peaks)

    # Find T-peaks (local maxima after S-peak)
    t_peaks = []
    for s_idx in s_peaks:
        search_window = range(s_idx, min(len(ecg_values), s_idx + 20))
        if len(search_window) > 0:
            t_idx = search_window[np.argmax(ecg_values[search_window])]
            t_peaks.append(t_idx)

    t_peaks = np.array(t_peaks)

    # Convert time to milliseconds (ms)
    p_peak_times = timestamps[p_peaks] * 1000  # Convert seconds to ms
    q_peak_times = timestamps[q_peaks] * 1000
    r_peak_times = timestamps[r_peaks] * 1000
    s_peak_times = timestamps[s_peaks] * 1000
    t_peak_times = timestamps[t_peaks] * 1000

    # Calculate intervals (in ms)
    pr_intervals = (r_peak_times - p_peak_times)  # PR interval
    qrs_durations = (s_peak_times - q_peak_times)  # QRS duration
    qt_intervals = (t_peak_times - q_peak_times)  # QT interval

    # Calculate average values
    avg_p_peak_time = np.mean(p_peak_times)
    avg_q_peak_time = np.mean(q_peak_times)
    avg_r_peak_time = np.mean(r_peak_times)
    avg_s_peak_time = np.mean(s_peak_times)
    avg_t_peak_time = np.mean(t_peak_times)

    avg_p_value = np.mean(ecg_values[p_peaks])
    avg_q_value = np.mean(ecg_values[q_peaks])
    avg_r_value = np.mean(ecg_values[r_peaks])
    avg_s_value = np.mean(ecg_values[s_peaks])
    avg_t_value = np.mean(ecg_values[t_peaks])

    avg_pr_interval = np.mean(pr_intervals)
    avg_qrs_duration = np.mean(qrs_durations)
    avg_qt_interval = np.mean(qt_intervals)

    # Calculate Heart Rate (HR)
    rr_intervals = np.diff(r_peak_times)  # Time between consecutive R-peaks (in ms)
    heart_rate = 60000 / np.mean(rr_intervals) if len(rr_intervals) > 0 else None  # bpm

    # Calculate P wave duration (assuming P wave lasts a few ms before and after peak)
    p_wave_durations = []
    for p_idx in p_peaks:
        search_window = range(max(0, p_idx - 5), min(len(ecg_values), p_idx + 5))  # Small window around P peak
        start_p_idx = search_window[0]  # Start of P wave
        end_p_idx = search_window[-1]   # End of P wave
        p_wave_durations.append((timestamps[end_p_idx] - timestamps[start_p_idx]) * 1000)  # Convert to ms

    p_wave_durations = np.array(p_wave_durations)
    avg_p_wave_duration = np.mean(p_wave_durations)

    # Calculate QTc interval using Bazett’s formula
    if len(rr_intervals) > 0:
        avg_rr_interval = np.mean(rr_intervals) / 1000  # Convert ms to seconds
        avg_qt_interval_sec = avg_qt_interval / 1000  # Convert ms to seconds
        qt_corrected = avg_qt_interval_sec / np.sqrt(avg_rr_interval)  # Bazett’s formula
        qt_corrected_ms = qt_corrected * 1000  # Convert back to ms
    else:
        qt_corrected_ms = None  # If no RR intervals are found

    # Return all computed features
    return {
        "heart_rate": heart_rate,
        "avg_p_peak_time": avg_p_peak_time,
        "avg_q_peak_time": avg_q_peak_time,
        "avg_r_peak_time": avg_r_peak_time,
        "avg_s_peak_time": avg_s_peak_time,
        "avg_t_peak_time": avg_t_peak_time,
        "avg_p_value": avg_p_value,
        "avg_q_value": avg_q_value,
        "avg_r_value": avg_r_value,
        "avg_s_value": avg_s_value,
        "avg_t_value": avg_t_value,
        "avg_pr_interval": avg_pr_interval,
        "avg_qrs_duration": avg_qrs_duration,
        "avg_qt_interval": avg_qt_interval,
        "avg_p_wave_duration": avg_p_wave_duration,
        "qt_corrected_ms": qt_corrected_ms
    }

# Function to apply formulas from the CSV file
def apply_formulas(features, formulas):
    results = {}
    for index, row in formulas.iterrows():
        wave_name = row['wave']
        formula = row['formula']
        try:
            # Pass the 'features' dictionary to eval
            results[wave_name] = eval(formula, {'features': features})
        except Exception as e:
            results[wave_name] = f"Error: {e}"
    return results

# Main function to run the ECG analysis
def run_ecg_analysis(ecg_file_path, formulas_file_path):
    # Load ECG data
    timestamps, ecg_values = load_ecg_data(ecg_file_path)

    # Load formulas
    formulas = load_formulas(formulas_file_path)

    # Compute ECG features
    features = compute_ecg_features(timestamps, ecg_values)

    # Apply formulas
    results = apply_formulas(features, formulas)

    # Print results
    print("ECG Analysis Results:")
    for wave, value in results.items():
        print(f"{wave}: {value}")

    # Plot ECG signal with P, Q, R, S, and T peaks
    plt.figure(figsize=(12, 5))
    plt.plot(timestamps * 1000, ecg_values, label="ECG Signal", color="blue")  # Convert x-axis to ms

    plt.scatter(features["avg_r_peak_time"], features["avg_r_value"], color='red', label="Avg R Peak", marker="^")
    plt.scatter(features["avg_q_peak_time"], features["avg_q_value"], color='green', label="Avg Q Peak", marker="v")
    plt.scatter(features["avg_p_peak_time"], features["avg_p_value"], color='purple', label="Avg P Peak", marker="o")
    plt.scatter(features["avg_s_peak_time"], features["avg_s_value"], color='orange', label="Avg S Peak", marker="s")
    plt.scatter(features["avg_t_peak_time"], features["avg_t_value"], color='cyan', label="Avg T Peak", marker="D")

    plt.xlabel("Time (ms)")
    plt.ylabel("ECG Amplitude")
    plt.title("ECG Waveform with Average P, Q, R, S, and T Peaks")
    plt.legend()
    plt.grid()
    plt.show()

# Example usage
ecg_file_path = r"C:\Users\Varsha K\ECG_WEB\backend\ecg_data.csv"  # Replace with your ECG data file path
formulas_file_path = r"C:\Users\Varsha K\ECG_WEB\backend\formulas.csv"  # Replace with your formulas file path
run_ecg_analysis(ecg_file_path, formulas_file_path)