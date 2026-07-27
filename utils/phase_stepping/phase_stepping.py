"""Click and import facade for phase-stepping calibration tools."""

import json
import sys
import time

import click
import numpy as np

try:
    from .plotting import (
        debugCalibration,
        plot_accelerated_spectrogram,
        plot_optimal_magnitude_sweep,
        plot_parameter_sweep_analysis,
        plot_raw_measurement,
        plot_speed_sweep_analysis,
        plot_spectrogram,
        store_or_show_plot,
    )
    from .serial_machine import (
        Machine,
        enabledMachineConnection,
        getPrusaPort,
        machineConnection,
        readLut,
        writeLut,
    )
    from .signal_analysis import (
        MOTOR_PERIOD,
        PhaseCorrection,
        SweepMeasurement,
        analyze_speed_sweep,
        compute_energy,
        compute_spectrogram,
        detect_harmonic_peaks,
        dft_sweep_motor_harmonic,
        find_n_valleys,
        find_peaks,
        harmonic_peaks_fit,
        locate_markers,
        locate_signal,
        moving_average,
    )
except ImportError:
    from plotting import (
        debugCalibration,
        plot_accelerated_spectrogram,
        plot_optimal_magnitude_sweep,
        plot_parameter_sweep_analysis,
        plot_raw_measurement,
        plot_speed_sweep_analysis,
        plot_spectrogram,
        store_or_show_plot,
    )
    from serial_machine import (
        Machine,
        enabledMachineConnection,
        getPrusaPort,
        machineConnection,
        readLut,
        writeLut,
    )
    from signal_analysis import (
        MOTOR_PERIOD,
        PhaseCorrection,
        SweepMeasurement,
        analyze_speed_sweep,
        compute_energy,
        compute_spectrogram,
        detect_harmonic_peaks,
        dft_sweep_motor_harmonic,
        find_n_valleys,
        find_peaks,
        harmonic_peaks_fit,
        locate_markers,
        locate_signal,
        moving_average,
    )


@click.command("readLut")
@click.option("--axis",
              required=True,
              type=click.Choice(["X", "Y"]),
              help="Axis for reading LUT")
@click.option("--dir",
              required=True,
              type=click.Choice(["F", "B"]),
              help="Table for which direction")
@click.option("--port", type=str, default=getPrusaPort(), help="Machine port")
def readLutCmd(axis: str, dir: str, port: str) -> None:
    with machineConnection(port) as machine:
        machine.waitForBoot()
        currents = readLut(machine, axis, dir)
        json.dump(currents.spectrum, sys.stdout, indent=4)


@click.command("writeLut")
@click.argument("filepath",
                required=True,
                type=click.Path(file_okay=True, exists=True, dir_okay=False))
@click.option("--axis",
              required=True,
              type=click.Choice(["X", "Y"]),
              help="Axis for reading LUT")
@click.option("--dir",
              required=True,
              type=click.Choice(["F", "B"]),
              help="Table for which direction")
@click.option("--port", type=str, default=getPrusaPort(), help="Machine port")
def writeLutCmd(axis: str, dir: str, port: str, filepath: str) -> None:
    with open(filepath) as f:
        correction = json.load(f)
    with machineConnection(port) as machine:
        machine.waitForBoot()
        writeLut(machine, axis, dir, PhaseCorrection(correction))


@click.command("analyzeParamSweep")
@click.option("--port", type=str, default=getPrusaPort(), help="Machine port")
@click.option("--motor-steps", type=int, default=200)
@click.option("--axis", type=click.Choice(["X", "Y"]))
@click.option("--speed", type=float, default=1)
@click.option("--revs", type=float, default=2)
@click.option("--n", type=int, default=2)
@click.option("--mag-start", type=float, default=0)
@click.option("--mag-end", type=float, default=0.0)
@click.option("--pha-start", type=float, default=0)
@click.option("--pha-end", type=float, default=0)
@click.option("--output",
              type=click.Path(dir_okay=True, file_okay=False),
              default=None,
              help="Output directory for data")
@click.option("--show", is_flag=True)
@click.option("--as-numpy/--as-machine",
              default=False,
              help="Use numpy or the direct machine implementation?")
def analyzeParamSweep(port, motor_steps, axis, speed, revs, n, mag_start,
                      mag_end, pha_start, pha_end, output, show, as_numpy):
    """
    Analyze parameter sweep
    """

    if output is None and not show:
        print("No output specified, nothing to do. Specify --output or --show")
        return

    present_plot = lambda name, plot: store_or_show_plot(
        show, output, name, plot)

    with enabledMachineConnection(port=port) as machine:
        time.sleep(0.2)
        machine.command("G92 X0 Y0")
        while True:
            raw_output = machine.command(
                f"M973 {axis} R{revs:.10f} F{speed:.10f} H{n} A{pha_start:.10f} B{pha_end:.10f} C{mag_start:.10f} D{mag_end:.10f}"
            )
            sweep_measurement_f = SweepMeasurement.from_raw_command(raw_output)
            machine.command("G0 F10000 X0 Y0")
            if sweep_measurement_f.is_ok():
                break
            print("Retrying")

        pha_start_b, pha_end_b = pha_end, pha_start
        mag_start_b, mag_end_b = mag_end, mag_start

        while True:
            raw_output = machine.command(
                f"M973 {axis} R{revs:.10f} F{speed:.10f} H{n} A{pha_start_b:.10f} B{pha_end_b:.10f} C{mag_start_b:.10f} D{mag_end_b:.10f}"
            )
            sweep_measurement_b = SweepMeasurement.from_raw_command(raw_output)
            machine.command("G0 F10000 X0 Y0")
            if sweep_measurement_b.is_ok():
                break
            print("Retrying")

    present_plot(
        "raw_f",
        plot_raw_measurement(sweep_measurement_f,
                             name="Forward sweep raw data"))
    present_plot(
        "raw_b",
        plot_raw_measurement(sweep_measurement_b,
                             name="Backward sweep raw data"))

    signal_start_f, signal_end_f = locate_signal(sweep_measurement_f)
    signal_start_b, signal_end_b = locate_signal(sweep_measurement_b)

    # Spectrogram
    time_bins_f, freq_bins_f, spectrogram_f = compute_spectrogram(
        sweep_measurement_f.samples, signal_start_f, signal_end_f,
        sweep_measurement_f.sampling_freq, 0.2)
    time_bins_b, freq_bins_b, spectrogram_b = compute_spectrogram(
        sweep_measurement_b.samples, signal_start_b, signal_end_b,
        sweep_measurement_b.sampling_freq, 0.2)

    present_plot(
        "spectrogram_f",
        plot_spectrogram(spectrogram_f,
                         time_bins_f,
                         freq_bins_f,
                         name="Forward sweep spectrogram"))
    present_plot(
        "spectrogram_b",
        plot_spectrogram(spectrogram_b,
                         time_bins_b,
                         freq_bins_b,
                         name="Backward sweep spectrogram"))

    # Analysis
    if as_numpy:
        analysis_freq = motor_steps / 4 * n
        analysis_f_freq_idx = np.argmin(np.abs(freq_bins_f - analysis_freq))
        analysis_b_freq_idx = np.argmin(np.abs(freq_bins_b - analysis_freq))

        f_response = [
            spectrum[analysis_f_freq_idx] for spectrum in spectrogram_f
        ]
        b_response = [
            spectrum[analysis_b_freq_idx] for spectrum in spectrogram_b
        ]
        b_response.reverse(
        )  # The sweep runs from end to start, but we want to compare it to the forward sweep
    else:
        time_bins_f, f_response = dft_sweep_motor_harmonic(
            sweep_measurement_f.samples, sweep_measurement_f.sampling_freq,
            signal_start_f, signal_end_f, speed, motor_steps, n, 10, 1)
        time_bins_b, b_response = dft_sweep_motor_harmonic(
            sweep_measurement_b.samples, sweep_measurement_b.sampling_freq,
            signal_start_b, signal_end_b, speed, motor_steps, n, 10, 1)
        b_response = b_response[::-1]

    mag_bins = np.linspace(mag_start, mag_end, len(time_bins_f))
    pha_bins = np.linspace(pha_start, pha_end, len(time_bins_b))

    trim_len = min(len(f_response), len(b_response))
    f_response = f_response[:trim_len]
    b_response = b_response[:trim_len]
    time_bins_f = time_bins_f[:trim_len]
    mag_bins = mag_bins[:trim_len]
    pha_bins = pha_bins[:trim_len]

    f_response, b_response = f_response + b_response, f_response + b_response

    present_plot(
        "analysis",
        plot_parameter_sweep_analysis(time_bins_f, mag_bins, pha_bins,
                                      f_response, b_response, pha_start,
                                      pha_end))


@click.command("findOptimalMagnitude")
@click.option("--port", type=str, default=getPrusaPort(), help="Machine port")
@click.option("--motor-steps", type=int, default=200)
@click.option("--axis", type=click.Choice(["X", "Y"]))
@click.option("--speed", type=float, default=1)
@click.option("--revs", type=float, default=1)
@click.option("--n", type=int, default=2)
@click.option("--mag-start", type=float, default=0.001)
@click.option("--mag-step", type=float, default=2)
@click.option("--pha-start", type=float, default=-2)
@click.option("--pha-end", type=float, default=14)
@click.option("--output",
              type=click.Path(dir_okay=True, file_okay=False),
              default=None,
              help="Output directory for data")
@click.option("--show", is_flag=True)
def findOptimalMagnitude(port, motor_steps, axis, speed, revs, n, mag_start,
                         mag_step, pha_start, pha_end, output, show):
    """
    Perform several parameter sweeps to locate optimal magnitude
    """
    if output is None and not show:
        print("No output specified, nothing to do. Specify --output or --show")
        return

    present_plot = lambda name, plot: store_or_show_plot(
        show, output, name, plot)

    last_minimum = np.inf
    mag = mag_start
    gone_worse_count = 0
    traces = []
    with enabledMachineConnection(port=port) as machine:
        time.sleep(0.2)
        machine.command("G92 X0 Y0")

        for _ in range(20):
            print(f"Testing magnitude {mag:.5f}: ", end="")
            raw_output = machine.command(
                f"M973 {axis} R{revs:.10f} F{speed:.10f} H{n} A{pha_start:.10f} B{pha_end:.10f} C{mag:.10f} D{mag:.10f}"
            )
            sweep_measurement = SweepMeasurement.from_raw_command(raw_output)
            machine.command("G0 F10000 X0 Y0")

            if not sweep_measurement.is_ok():
                print("Movement error")
                continue

            signal_start_f, signal_end_f = locate_signal(sweep_measurement)
            time_bins_f, f_response = dft_sweep_motor_harmonic(
                sweep_measurement.samples, sweep_measurement.sampling_freq,
                signal_start_f, signal_end_f, speed, motor_steps, n, 10, 1)

            f_response = moving_average(f_response, len(f_response) // 20)

            traces.append((mag, np.linspace(pha_start, pha_end,
                                            len(f_response)), f_response))

            minimum = np.min(f_response)
            print(minimum)
            if minimum < last_minimum:
                gone_worse_count = 0
                last_minimum = minimum
            else:
                gone_worse_count += 1
                if gone_worse_count >= 2:
                    break

            mag *= mag_step

    present_plot("optimal_mag", plot_optimal_magnitude_sweep(traces))


@click.command("analyzeSpeedSweep")
@click.option("--port", type=str, default=getPrusaPort(), help="Machine port")
@click.option("--motor-steps", type=int, default=200)
@click.option("--axis", type=click.Choice(["X", "Y"]))
@click.option("--revs", type=float, default=5)
@click.option("--speed-start", type=float, default=0.5)
@click.option("--speed-end", type=float, default=3)
@click.option("--output",
              type=click.Path(dir_okay=True, file_okay=False),
              default=None,
              help="Output directory for data")
@click.option("--show", is_flag=True)
def analyzeSpeedSweep(port, motor_steps, axis, revs, speed_start, speed_end,
                      output, show):
    """
    Analyze speed sweep
    """

    if output is None and not show:
        print("No output specified, nothing to do. Specify --output or --show")
        return

    present_plot = lambda name, plot: store_or_show_plot(
        show, output, name, plot)

    with enabledMachineConnection(port=port) as machine:
        machine.command("M17")
        time.sleep(0.2)
        machine.command("G92 X0 Y0")
        raw_output = machine.command(
            f"M974 {axis} R{revs:.10f} A{speed_start:.10f} B{speed_end:.10f}")
        sweep_measurement_f = SweepMeasurement.from_raw_command(raw_output)

        raw_output = machine.command(
            f"M974 {axis} R{-revs:.10f} A{speed_start:.10f} B{speed_end:.10f}")
        machine.command("G0 F10000 X0 Y0")
        sweep_measurement_b = SweepMeasurement.from_raw_command(raw_output)

    present_plot(
        "raw_f",
        plot_raw_measurement(sweep_measurement_f,
                             name="Forward sweep raw data"))
    present_plot(
        "raw_b",
        plot_raw_measurement(sweep_measurement_b,
                             name="Backward sweep raw data"))

    for dir, meas in {
            "f": sweep_measurement_f,
            "b": sweep_measurement_b
    }.items():
        signal_start, signal_end = locate_signal(meas)
        time_bins, freq_bins, spectrogram = compute_spectrogram(
            meas.samples, signal_start, signal_end, meas.sampling_freq, 0.2)
        present_plot(
            f"spectrogram_{dir}",
            plot_accelerated_spectrogram(spectrogram,
                                         time_bins,
                                         freq_bins,
                                         speed_start,
                                         speed_end,
                                         name=f"{dir} sweep spectrogram"))

    harmonic_analysis = {}
    for h in [1, 2, 3, 4]:
        signal_start, signal_end = locate_signal(sweep_measurement_f)
        (speeds_f_up,
         profile_f_up), (speeds_f_down, profile_f_down) = analyze_speed_sweep(
             sweep_measurement_f.samples, sweep_measurement_f.sampling_freq,
             signal_start, signal_end, speed_start, speed_end, motor_steps, h,
             0.05)

        signal_start, signal_end = locate_signal(sweep_measurement_b)
        (speeds_b_up,
         profile_b_up), (speeds_b_down, profile_b_down) = analyze_speed_sweep(
             sweep_measurement_b.samples, sweep_measurement_b.sampling_freq,
             signal_start, signal_end, speed_start, speed_end, motor_steps, h,
             0.05)

        trim_len = min(len(speeds_f_up), len(speeds_b_up), len(speeds_f_down),
                       len(speeds_b_down))
        speeds_f_up = speeds_f_up[:trim_len]
        speeds_b_up = speeds_b_up[:trim_len]
        speeds_f_down = speeds_f_down[:trim_len]
        speeds_b_down = speeds_b_down[:trim_len]

        profile_f_up = profile_f_up[:trim_len]
        profile_b_up = profile_b_up[:trim_len]
        profile_f_down = profile_f_down[:trim_len]
        profile_b_down = profile_b_down[:trim_len]

        harmonic_analysis[h] = {
            "f_up": (speeds_f_up, profile_f_up),
            "f_down": (speeds_f_down, profile_f_down),
            "b_up": (speeds_b_up, profile_b_up),
            "b_down": (speeds_b_down, profile_b_down),
        }

    present_plot("speed_sweep_analysis",
                 plot_speed_sweep_analysis(harmonic_analysis))


@click.group()
def cli():
    """
    Test & calibration scripts
    """


cli.add_command(readLutCmd)
cli.add_command(writeLutCmd)
cli.add_command(analyzeParamSweep)
cli.add_command(findOptimalMagnitude)
cli.add_command(analyzeSpeedSweep)
cli.add_command(debugCalibration)

if __name__ == "__main__":
    cli()
