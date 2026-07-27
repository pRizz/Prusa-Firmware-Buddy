"""Plotly adapter and calibration-output rendering."""

import json
from pathlib import Path

import click
import numpy as np
import plotly.colors
import plotly.graph_objects as go

try:
    from .serial_machine import enabledMachineConnection, getPrusaPort
    from .signal_analysis import (
        SweepMeasurement,
        detect_harmonic_peaks,
        find_n_valleys,
        locate_markers,
        moving_average,
    )
except ImportError:
    from serial_machine import enabledMachineConnection, getPrusaPort
    from signal_analysis import (
        SweepMeasurement,
        detect_harmonic_peaks,
        find_n_valleys,
        locate_markers,
        moving_average,
    )


def store_or_show_plot(show, output, name, plot):
    if output is not None:
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
        plot.write_html(output / f"{name}.html")
    if show:
        plot.show()


def plot_raw_measurement(measurement: SweepMeasurement, name=None):
    fig = go.Figure()

    if name is not None:
        fig.update_layout(title=name)

    times = [
        i / measurement.sampling_freq for i in range(len(measurement.samples))
    ]
    fig.add_trace(go.Scatter(x=times, y=measurement.samples))

    start_maker_idx, end_marker_idx = locate_markers(measurement)
    start_marker_time = start_maker_idx / measurement.sampling_freq
    end_marker_time = end_marker_idx / measurement.sampling_freq

    signal_start_time = start_marker_time + measurement.signal_start - measurement.start_marker
    signal_end_time = start_marker_time + measurement.signal_end - measurement.start_marker

    fig.add_vline(x=start_marker_time,
                  line_dash="dash",
                  line_color="red",
                  annotation_text="Start marker")
    fig.add_vline(x=end_marker_time,
                  line_dash="dash",
                  line_color="red",
                  annotation_text="End marker")
    fig.add_vline(x=signal_start_time,
                  line_dash="dash",
                  line_color="green",
                  annotation_text="Signal start")
    fig.add_vline(x=signal_end_time,
                  line_dash="dash",
                  line_color="green",
                  annotation_text="Signal end")

    return fig


def plot_spectrogram(spectrogram, time_bins, freq_bins, name=None):
    fig = go.Figure(data=go.Heatmap(
        z=spectrogram.T, x=time_bins, y=freq_bins, colorscale='Jet'))
    fig.update_layout(title=name)
    return fig


def plot_accelerated_spectrogram(spectrogram,
                                 time_bins,
                                 freq_bins,
                                 fundamental_start,
                                 fundamental_end,
                                 name=None):
    spectrogram = np.asarray(spectrogram)
    fig = go.Figure(data=go.Heatmap(
        z=spectrogram.T, x=time_bins, y=freq_bins, colorscale='Jet'))
    fig.update_layout(title=name)

    # The speed is linearly increasing, so the fundamental frequency is also
    # linearly increasing. Draw the fundamental line + harmonics
    for i in range(1, 9):
        max_y = freq_bins[-1]

        origin_y = fundamental_start * i
        origin_x = time_bins[0]

        end_y = fundamental_end * i
        end_x = time_bins[len(time_bins) // 2]
        if end_y > max_y:
            end_y = max_y
            end_x = end_x - (fundamental_end - max_y / i) / (
                fundamental_end - fundamental_start) * (end_x - time_bins[0])

        fig.add_trace(
            go.Scatter(x=[origin_x, end_x],
                       y=[origin_y, end_y],
                       mode="lines",
                       line_shape="linear",
                       line=dict(color="black", width=1)))
    return fig


def plot_parameter_sweep_analysis(time_bins, mag_bins, pha_bins, f_response,
                                  b_response, pha_start, pha_end):
    fig = go.Figure()
    fig.update_layout(
        title="Resonance analysis based on parameter sweep",
        yaxis_title="Magnitude",
        yaxis=dict(
            domain=[0.1, 1
                    ]  # Shrinks the plot area upwards to create space below
        ),
        xaxis=dict(
            title="Time (s)",
            domain=[0, 1],
            showgrid=True,  # Show grid only for main x-axis
            zeroline=True,
        ),
        xaxis2=dict(title="Mag",
                    overlaying="x",
                    side="bottom",
                    anchor="free",
                    position=0.05,
                    tickformat=".4f",
                    showgrid=False,
                    nticks=20),
        xaxis3=dict(title="Pha",
                    overlaying="x",
                    side="bottom",
                    anchor="free",
                    position=0.00,
                    tickformat=".2f",
                    showgrid=False,
                    nticks=20),
    )

    for name, response in [("Forward", f_response), ("Backward", b_response)]:
        fig.add_trace(
            go.Scatter(x=time_bins,
                       y=response,
                       name=name + " response to time"))
        fig.add_trace(
            go.Scatter(x=mag_bins,
                       y=response,
                       name=name + " response to mag",
                       xaxis="x2"))
        fig.add_trace(
            go.Scatter(x=pha_bins,
                       y=response,
                       name=name + " response to pha",
                       xaxis="x3"))

    if pha_start == pha_end:
        return fig

    num_valleys = (pha_end - pha_start) // (2 * np.pi)
    to_pha_space = lambda x: (x / len(time_bins) *
                              (pha_end - pha_start) + pha_start)

    f_valleys_idx = find_n_valleys(f_response, num_valleys)
    b_valleys_idx = find_n_valleys(b_response, num_valleys)

    for v_idx in f_valleys_idx:
        fig.add_trace(
            go.Scatter(x=[to_pha_space(v_idx)],
                       y=[f_response[v_idx]],
                       mode="markers",
                       marker=dict(color="blue"),
                       xaxis="x3",
                       showlegend=False))
    for v_idx in b_valleys_idx:
        fig.add_trace(
            go.Scatter(x=[to_pha_space(v_idx)],
                       y=[b_response[v_idx]],
                       mode="markers",
                       marker=dict(color="red"),
                       xaxis="x3",
                       showlegend=False))

    for v in [(a + b) // 2 for a, b in zip(f_valleys_idx, b_valleys_idx)]:
        fig.add_vline(x=time_bins[v],
                      line_dash="dash",
                      line_color="green",
                      annotation_text="Identified pha")

    for v in [(to_pha_space(a) + to_pha_space(b)) / 2
              for a, b in zip(f_valleys_idx, b_valleys_idx)]:
        print(f"Candidate pha: {v % (2 * np.pi)}")

    return fig


def plot_optimal_magnitude_sweep(traces):
    fig = go.Figure()
    fig.update_layout(title="Optimal magnitude sweep",
                      yaxis_title="Magnitude",
                      xaxis_title="Phase")
    for mag, phases, response in traces:
        fig.add_trace(go.Scatter(x=phases, y=response, name=f"Mag {mag:.5f}"))
    return fig


def plot_speed_sweep_analysis(harmonic_analysis):
    fig = go.Figure()
    fig.update_layout(title="Speed sweep analysis",
                      yaxis_title="Magnitude",
                      xaxis_title="Speed (mm/s)")
    colors = plotly.colors.DEFAULT_PLOTLY_COLORS
    for i, (harmonic, data) in enumerate(harmonic_analysis.items()):
        color = colors[i]
        for name, (speeds, profile) in data.items():
            fig.add_trace(
                go.Scatter(x=speeds,
                           y=profile,
                           name=f"H{harmonic} {name}",
                           mode="lines",
                           line=dict(color=color, width=1),
                           visible="legendonly"))

        combination = np.add(data["f_up"][1], data["f_down"][1])
        combination = np.add(combination, data["b_up"][1])
        combination = np.add(combination, data["b_down"][1])
        fig.add_trace(
            go.Scatter(x=data["f_up"][0],
                       y=combination,
                       name=f"H{harmonic}",
                       mode="lines",
                       line=dict(color=color, width=2)))

    signals = []
    for harmonic, data in harmonic_analysis.items():
        signal = np.add(data["f_up"][1], data["f_down"][1])
        signal = np.add(signal, data["b_up"][1])
        signal = np.add(signal, data["b_down"][1])
        # Combining before smoothing is cheaper than four Hanning windows.
        signal = moving_average(signal, len(signal) // 50)
        signals.append((harmonic, signal))

    speeds = harmonic_analysis[1]["f_up"][0]
    best_found, best_estimate = detect_harmonic_peaks(signals,
                                                      lambda idx: speeds[idx])

    print("Best found", best_found)
    print("Best estimate", best_estimate)

    for harmonic, pos in best_found:
        fig.add_vline(x=pos,
                      line_dash="dash",
                      line_color=colors[harmonic - 1],
                      annotation_text=f"Best found H{harmonic}")
    for harmonic, pos in best_estimate:
        fig.add_vline(x=pos,
                      line_dash="solid",
                      line_color=colors[harmonic - 1],
                      annotation_text=f"Best estimate H{harmonic}")

    return fig


@click.command("debugCalibration")
@click.option("--port", type=str, default=getPrusaPort(), help="Machine port")
@click.option("--axis", type=click.Choice(["X", "Y"]))
@click.option("--show", is_flag=True)
@click.option("--output",
              type=click.Path(dir_okay=True, file_okay=False),
              default=None,
              help="Output directory for data")
def debugCalibration(port, axis, show, output):
    """
    Debug calibration
    """

    if output is None and not show:
        print("No output specified, nothing to do. Specify --output or --show")
        return

    present_plot = lambda name, plot: store_or_show_plot(
        show, output, name, plot)

    def handle_raw_singal(obj):
        fig = go.Figure()
        tims = [
            i / obj["annotation"]["sampling_freq"]
            for i in range(len(obj["signal"]))
        ]
        fig.add_trace(go.Scatter(x=tims, y=obj["signal"]))

        start_marker, end_marker = obj["signal_bounds"]
        start_marker /= obj["annotation"]["sampling_freq"]
        end_marker /= obj["annotation"]["sampling_freq"]

        fig.add_vline(x=start_marker,
                      line_dash="dash",
                      line_color="red",
                      annotation_text="Signal start")
        fig.add_vline(x=end_marker,
                      line_dash="dash",
                      line_color="red",
                      annotation_text="Signal end")

        present_plot(obj["name"], fig)

    harmonic_data = {}

    def handle_dft_speed_sweep_result(obj):
        nonlocal harmonic_data
        harmonic = obj["harmonic"]
        name = obj["name"]

        if harmonic not in harmonic_data:
            harmonic_data[harmonic] = {}
        harmonic_data[harmonic][name] = obj

    detected_peaks = None

    def handle_detected_peaks(obj):
        nonlocal detected_peaks
        detected_peaks = obj

    mag_search_traces = {}

    def handle_mag_search(obj):
        harmonic = obj["harmonic"]
        if harmonic not in mag_search_traces:
            mag_search_traces[harmonic] = []
        mag_search_traces[harmonic].append(obj)

    param_search_traces = {}

    def handle_param_search(obj):
        harmonic = obj["harmonic"]
        if harmonic not in param_search_traces:
            param_search_traces[harmonic] = []
        param_search_traces[harmonic].append(obj)

    with enabledMachineConnection(port=port) as machine:
        raw_output = machine.command(f"M972 {axis}", timeout=60)

    for line in raw_output:
        if line.startswith("# raw_signal"):
            handle_raw_singal(json.loads(line.split(" ", maxsplit=2)[2]))
        if line.startswith("# dft_speed_sweep_result"):
            handle_dft_speed_sweep_result(
                json.loads(line.split(" ", maxsplit=2)[2]))
        if line.startswith("# harmonic_peaks"):
            handle_detected_peaks(json.loads(line.split(" ", maxsplit=2)[2]))
        if line.startswith("# magnitude_search"):
            handle_mag_search(json.loads(line.split(" ", maxsplit=2)[2]))
        if line.startswith("# param_search"):
            handle_param_search(json.loads(line.split(" ", maxsplit=2)[2]))

    # Plot all harmonic data
    fig = go.Figure()
    fig.update_layout(title="Speed sweep analysis",
                      yaxis_title="Magnitude",
                      xaxis_title="Speed (rev/s)")
    colors = plotly.colors.DEFAULT_PLOTLY_COLORS
    for h, data in harmonic_data.items():
        color = colors[h - 1]
        combination = None
        for name, obj in data.items():
            speeds = np.linspace(obj["start_x"], obj["end_x"],
                                 len(obj["signal"]))
            signal = np.asarray(obj["signal"])
            if combination is None:
                combination = signal
            else:
                combination = np.add(combination, signal)
            fig.add_trace(
                go.Scatter(x=speeds,
                           y=signal,
                           name=f"H{h} {name}",
                           mode="lines",
                           line=dict(color=color, width=1),
                           visible="legendonly"))

        fig.add_trace(
            go.Scatter(x=speeds,
                       y=combination,
                       name=f"H{h}",
                       mode="lines",
                       line=dict(color=color, width=2)))

    for peak in detected_peaks["peaks"]:
        harmonic = peak["harmonic"]
        meas_pos = peak["measured_position"]
        est_pos = peak["estimated_position"]
        fig.add_vline(x=meas_pos,
                      line_dash="dash",
                      line_color=colors[harmonic - 1],
                      annotation_text=f"Measured H{harmonic}")
        fig.add_vline(x=est_pos,
                      line_dash="solid",
                      line_color=colors[harmonic - 1],
                      annotation_text=f"Estimated H{harmonic}")

    present_plot("speed_sweep_analysis", fig)

    # Plot each magnitude search
    for h, traces in mag_search_traces.items():
        fig = go.Figure()
        fig.update_layout(title=f"Magnitude search H{h}",
                          yaxis_title="Magnitude",
                          xaxis_title="Magnitude")
        for trace in traces:
            fig.add_trace(
                go.Scatter(y=trace["response"],
                           name=f"Mag {trace['magnitude']}",
                           mode="lines"))
        present_plot(f"mag_search_H{h}", fig)

    # Plot each phase search
    for h, traces in param_search_traces.items():
        for dir in [1, -1]:
            dirname = "forward" if dir == 1 else "backward"
            fig = go.Figure()
            fig.update_layout(title=f"Phase search H{h} - {dirname}",
                              yaxis_title="Magnitude",
                              xaxis_title="Phase")
            for trace in [
                    x for x in traces
                    if x["move_dir"] == dir and x["mag_start"] == x["mag_end"]
            ]:
                x = np.linspace(trace["pha_start"], trace["pha_end"],
                                len(trace["response"]))
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=trace["response"],
                        name=f"Pha {trace['pha_start']} → {trace['pha_end']}",
                        mode="lines"))
            present_plot(f"pha_search_H{h}_{dirname}", fig)

    # Plot each mag search
    for h, traces in param_search_traces.items():
        for dir in [1, -1]:
            dirname = "forward" if dir == 1 else "backward"
            fig = go.Figure()
            fig.update_layout(title=f"Magnitude search H{h} - {dirname}",
                              yaxis_title="Response",
                              xaxis_title="Magnitude")
            for trace in [
                    x for x in traces
                    if x["move_dir"] == dir and x["pha_start"] == x["pha_end"]
            ]:
                x = np.linspace(trace["mag_start"], trace["mag_end"],
                                len(trace["response"]))
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=trace["response"],
                        name=f"Mag {trace['mag_start']} → {trace['mag_end']}",
                        mode="lines"))
            present_plot(f"mag_search_H{h}_{dirname}", fig)
