"""Pure numerical analysis for phase-stepping calibration."""

from dataclasses import dataclass, field
from typing import Callable, Iterable, List, Tuple

import numpy as np
from scipy.fft import rfft, rfftfreq

MOTOR_PERIOD = 1024


@dataclass
class PhaseCorrection:
    spectrum: List[Tuple[float, float]] = field(
        default_factory=lambda: [(0, 0) for _ in range(17)])

    def phaseShift(self) -> List[float]:
        phaseSeq = []
        for i in range(MOTOR_PERIOD):
            pha = i * 2 * np.pi / MOTOR_PERIOD
            res = 0
            for n, (mag, phase) in enumerate(self.spectrum):
                res += mag * np.sin(n * pha + phase)
            phaseSeq.append(res)
        return phaseSeq

    def currents(self) -> List[Tuple(int, int)]:
        currents = []
        for i, phasehift in enumerate(self.phaseShift()):
            pha = i * 2 * np.pi / 1024 + phasehift
            a = np.round(248 * np.sin(pha))
            b = np.round(248 * np.cos(pha))
            currents.append((a, b))
        return currents


@dataclass
class SweepMeasurement:
    samples: List[float]
    sampling_freq: float
    movement_ok: bool
    accel_error: int

    start_marker: float
    end_marker: float
    signal_start: float
    signal_end: float

    @staticmethod
    def from_raw_command(response: List[str]):
        samples = []
        sampling_freq = 0.0
        movement_ok = False
        accel_error = 0
        start_marker = 0.0
        end_marker = 0.0
        signal_start = 0.0
        signal_end = 0.0

        for line in response:
            if line.startswith("sampling_freq:"):
                sampling_freq = float(line.split(":")[1])
            elif line.startswith("movement_ok:"):
                movement_ok = line.split(":")[1].strip().lower() == "true"
            elif line.startswith("accel_error:"):
                accel_error = int(line.split(":")[1])
            elif line.startswith("start_marker:"):
                start_marker = float(line.split(":")[1])
            elif line.startswith("end_marker:"):
                end_marker = float(line.split(":")[1])
            elif line.startswith("signal_start:"):
                signal_start = float(line.split(":")[1])
            elif line.startswith("signal_end:"):
                signal_end = float(line.split(":")[1])
            elif line[0].isdigit():
                samples.append(float(line.split(",")[1]))

        return SweepMeasurement(
            samples=samples,
            sampling_freq=sampling_freq,
            movement_ok=movement_ok,
            accel_error=accel_error,
            start_marker=start_marker,
            end_marker=end_marker,
            signal_start=signal_start,
            signal_end=signal_end,
        )

    def is_ok(self):
        return self.movement_ok and self.accel_error == 0 and self.sampling_freq > 0

    def get_signal(self):
        start_marker_idx, end_marker_idx = locate_markers(self)
        start_marker_time = start_marker_idx / self.sampling_freq
        end_marker_time = end_marker_idx / self.sampling_freq

        signal_start_idx = int(
            (self.signal_start - self.start_marker) * self.sampling_freq)
        signal_end_idx = int(
            (self.signal_end - self.start_marker) * self.sampling_freq)

        return self.samples[start_marker_idx +
                            signal_start_idx:start_marker_idx + signal_end_idx]


def compute_energy(samples: List[float], start_idx: int, end_idx: int,
                   win: int) -> list[float]:
    # This isn't pythonic, but it mimics the firmware implementation
    energy = [sum(x * x for x in samples[start_idx:start_idx + win])]
    for i in range(start_idx + 1, end_idx):
        energy.append(energy[-1] + samples[i] * samples[i] -
                      samples[i - win] * samples[i - win])
    return energy


def locate_markers(measurement: SweepMeasurement,
                   search_win=0.1) -> Tuple[int, int]:
    ENERGY_WIN = 0.005  # s
    energy_win = int(ENERGY_WIN * measurement.sampling_freq)

    markers_offset = int((measurement.end_marker - measurement.start_marker) *
                         measurement.sampling_freq)
    start1_idx = int((measurement.start_marker - search_win / 2) *
                     measurement.sampling_freq)
    end1_idx = int((measurement.start_marker + search_win / 2) *
                   measurement.sampling_freq)

    energy1 = compute_energy(measurement.samples, start1_idx, end1_idx,
                             energy_win)
    energy2 = compute_energy(measurement.samples, start1_idx + markers_offset,
                             end1_idx + markers_offset, energy_win)
    combined_energy = [e1 + e2 for e1, e2 in zip(energy1, energy2)]

    mean = np.mean(combined_energy)
    first_peak = np.argmax(combined_energy > mean)

    return start1_idx + first_peak, start1_idx + first_peak + markers_offset


def locate_signal(measurement: SweepMeasurement,
                  search_win=0.1) -> Tuple[int, int]:
    start_marker_idx, end_marker_idx = locate_markers(measurement)
    signal_start = int((measurement.signal_start - measurement.start_marker) *
                       measurement.sampling_freq)
    signal_end = int((measurement.signal_end - measurement.start_marker) *
                     measurement.sampling_freq)
    return start_marker_idx + signal_start, start_marker_idx + signal_end


def compute_spectrogram(samples,
                        start_idx,
                        end_idx,
                        sampling_freq,
                        window_size_s,
                        step_size=1):
    """
    Compute a spectrogram of the signal. Returns time_bins, freq_bins,
    spectrogram.
    """
    win_size = int(window_size_s * sampling_freq)
    spectrogram = []
    for i in range(start_idx, end_idx, step_size):
        windowed_signal = samples[i - win_size // 2:i + win_size // 2]
        windowed_signal *= np.hanning(len(windowed_signal))
        fft = rfft(windowed_signal)
        spectrogram.append(np.abs(fft))
    spectrogram.pop()

    time_bins = [
        i / sampling_freq for i in range(start_idx, end_idx, step_size)
    ]
    freq_bins = rfftfreq(win_size, 1 / sampling_freq)
    return time_bins, freq_bins, np.array(spectrogram)


def dft_sweep_motor_harmonic(samples: np.ndarray, sampling_freq: float,
                             idx_start: int, idx_end: int, speed: float,
                             motor_steps: int, harmonic: int, window_size: int,
                             step_size: int):
    """
    Compute a single bin DFT sweep at an integral multiple of motor frequency.
    The window size and step size are given in motor periods.np.round(
    """
    motor_period_duration = 1 / (speed * motor_steps / 4)
    analysis_freq = speed * motor_steps / 4 * harmonic

    signal_duration = (idx_end - idx_start) / sampling_freq
    window_duration = window_size * motor_period_duration
    half_window_idx = int(window_duration * sampling_freq / 2)

    total_steps = int(signal_duration / motor_period_duration / step_size)

    sin_corr = []
    cos_corr = []
    for i, s in enumerate(samples):
        t = i / sampling_freq
        sin_corr.append(np.sin(2 * np.pi * analysis_freq * t) * s)
        cos_corr.append(np.cos(2 * np.pi * analysis_freq * t) * s)

    bins = []
    res = []
    for i in range(0, total_steps):
        center_time = i * motor_period_duration * step_size
        center_idx = idx_start + int(center_time * sampling_freq)

        sin_win = sin_corr[center_idx - half_window_idx:center_idx +
                           half_window_idx]
        cos_win = cos_corr[center_idx - half_window_idx:center_idx +
                           half_window_idx]

        sin_corr_sum = np.sum(sin_win)
        cos_corr_sum = np.sum(cos_win)
        bins.append(center_time)
        res.append(
            np.sqrt(sin_corr_sum * sin_corr_sum + cos_corr_sum * cos_corr_sum)
            / len(sin_win))

    return bins, np.asarray(res)


def find_n_valleys(y, n, hysteresis=0.1, max_iter=10, stepdown=0.9):
    """
    Identifies the n most prominent valleys by iteratively adjusting threshold
    until n valleys are found.
    """

    y = np.asarray(y)
    min_y, max_y = np.min(y), np.max(y)
    best_threshold = np.mean(y)
    regions = []

    for i in range(max_iter):
        lower_threshold = best_threshold
        upper_threshold = best_threshold + hysteresis * (max_y - min_y)

        num_regions = 0
        in_region = False
        regions = []
        start = None

        for i in range(len(y)):
            if y[i] <= lower_threshold and not in_region:
                num_regions += 1
                in_region = True
                start = i
            elif y[i] > upper_threshold and in_region:
                in_region = False
                regions.append((start, i))
        if num_regions == n:
            break

        best_threshold = min_y + (best_threshold - min_y) * stepdown

    valleys = []
    for start, end in regions:
        assert start < end
        valleys.append(start + np.argmin(y[start:end]))

    return valleys


def find_peaks(signal: Iterable[float],
               min_prominence: float = 0.2) -> List[Tuple[int, float, float]]:
    """
    Find all peaks in a signal. Signal is a 1D iterable containing the signal.

    Returns:
        List of tuples (peak_index, peak_value, prominence), sorted by
        prominence.
    """
    signal = np.asarray(signal)
    assert len(signal) > 0, "Signal must not be empty."

    n = len(signal)
    peaks = []

    peak_indices = [
        i for i in range(1, n - 1)
        if signal[i] > signal[i - 1] and signal[i] > signal[i + 1]
    ]

    # If no local maxima found, return global max
    if not peak_indices:
        max_idx = np.argmax(signal)
        return [(max_idx, signal[max_idx], 1)]

    # Compute left and right minimums
    left_min = np.zeros(n)
    right_min = np.zeros(n)

    left_min[0] = signal[0]
    for i in range(1, n):
        left_min[i] = min(left_min[i - 1], signal[i])

    right_min[-1] = signal[-1]
    for i in range(n - 2, -1, -1):
        right_min[i] = min(right_min[i + 1], signal[i])

    # Step 3: Compute prominence for each peak
    signal_max = max(signal)
    for i in peak_indices:
        surrounding_min = min(left_min[i - 1], right_min[i + 1])
        prominence = (signal[i] - surrounding_min) / signal_max
        if prominence >= min_prominence:
            peaks.append((i, signal[i], prominence))

    return sorted(peaks, key=lambda x: -x[2])


def harmonic_peaks_fit(harmonic_positions):
    """
    Computes a mean fit for hamonic positions. The positions are given as tuples
    (harmonic, position).

    Return a tuple (estimated_positions, sum_squared_error)
    """
    C_values = [h * p for h, p in harmonic_positions]
    C_est = np.mean(C_values)
    estimated_positions = [(h, C_est / h) for h, _ in harmonic_positions]
    sum_squared_error = sum(
        (p - p_est)**2
        for (_, p), (_, p_est) in zip(harmonic_positions, estimated_positions))

    return estimated_positions, sum_squared_error


def detect_harmonic_peaks(signals: List[Tuple[int, Iterable[float]]],
                          pos_function: Callable[[int], float],
                          min_prominence: float = 0.2):
    """
    Detect peaks in multiple signals that follow harmonic relationships. The
    signals are specified as a list of tuples (harmonic, signal). The position
    function is used to convert indices to positions. Return the best detected
    peaks and the best estimated positions.
    """

    peaks = [(h, [(pos_function(i), s, p)
                  for i, s, p in find_peaks(signal, min_prominence)])
             for h, signal in signals]

    # Try all peaks as anchors for harmonic detection
    best_badness = np.inf
    best_positions = None
    best_estimation = None
    for h_anchor, h_peaks in peaks:
        for anchor_pos, _, _ in h_peaks:
            nominal_pos = anchor_pos * h_anchor

            # Selected the closes peak for each harmonic
            selected_peaks = {}
            for h, h_peaks in peaks:
                best_dist = np.inf
                best_peak = None
                for pos, _, _ in h_peaks:
                    dist = abs(pos * h - nominal_pos)
                    if dist < best_dist:
                        best_dist = dist
                        best_peak = pos
                selected_peaks[h] = best_peak

            # Compute badness
            estimated_pos, badness = harmonic_peaks_fit(
                list(selected_peaks.items()))
            if badness < best_badness:
                best_badness = badness
                best_positions = selected_peaks
                best_estimation = estimated_pos

    best_positions = [(h, p) for h, p in best_positions.items()]
    return best_positions, best_estimation


def moving_average(signal, window_size):
    """
    Compute a moving average with boundary correction.
    """
    n = len(signal)
    smoothed = np.zeros(n)

    for i in range(n):
        left = max(0, i - window_size // 2)
        right = min(n, i + window_size // 2 + 1)
        smoothed[i] = np.mean(signal[left:right])

    return smoothed


def analyze_speed_sweep(samples, sampling_freq, start_idx, end_idx,
                        start_speed, top_speed, motor_steps, harmonic,
                        window_size):
    """
    Analyze a speed sweep measurement that goes from start_speed to top_speed
    and then back again to start_speed. The window_size is given in seconds
    """
    sweep_duration = (end_idx - start_idx) / sampling_freq
    ramp_duration = sweep_duration / 2
    one_period_revs = 1 / (motor_steps / 4)

    start_freq = harmonic * start_speed / one_period_revs
    top_freq = harmonic * top_speed / one_period_revs
    speed_accel = (top_speed - start_speed) / ramp_duration
    freq_accel = (top_freq - start_freq) / ramp_duration
    freq_accel_start_t = start_idx / sampling_freq
    freq_accel_top_t = (end_idx + start_idx) / 2 / sampling_freq

    sin_cor = []
    cos_cor = []
    for i, s in enumerate(samples):
        # The argument of sin and cos is in radians and consists of three parts:
        # - the constant velocity part
        # - the acceleration part
        # - the deceleration part
        t = i / sampling_freq
        if t < freq_accel_start_t:
            freq = start_freq
            arg = 2 * np.pi * start_freq * t
        elif t < freq_accel_top_t:
            freq = start_freq + freq_accel * (t - freq_accel_start_t)
            arg = 2 * np.pi * start_freq * t + np.pi * freq_accel * (
                t - freq_accel_start_t)**2
        else:
            freq = top_freq - freq_accel * (t - freq_accel_top_t)
            t_rel = t - freq_accel_top_t
            arg = 2 * np.pi * top_freq * t_rel - np.pi * freq_accel * t_rel**2
        if freq < sampling_freq / 2:
            sin_cor.append(np.sin(arg) * s)
            cos_cor.append(np.cos(arg) * s)
        else:
            sin_cor.append(0)
            cos_cor.append(0)

    retval = []
    for r in [(start_idx, (start_idx + end_idx) // 2),
              ((start_idx + end_idx) // 2, end_idx)]:
        res = []
        speed_bins = []
        for i in range(*r):
            win_half = int(window_size * sampling_freq / 2)
            sin_w = np.sum(sin_cor[i - win_half:i +
                                   win_half])  # * np.hanning(win_half * 2))
            cos_w = np.sum(cos_cor[i - win_half:i +
                                   win_half])  # * np.hanning(win_half * 2))

            t = i / sampling_freq
            if t < freq_accel_start_t:
                speed = start_speed
            elif t < freq_accel_top_t:
                speed = start_speed + speed_accel * (t - freq_accel_start_t)
            else:
                speed = top_speed - speed_accel * (t - freq_accel_top_t)

            res.append((sin_w * sin_w + cos_w * cos_w) / speed)
            speed_bins.append(speed)

        if r[1] == end_idx:
            speed_bins = speed_bins[::-1]
            res = res[::-1]
        retval.append((np.asarray(speed_bins), res))

    return tuple(retval)
