import unittest

import numpy as np
from click.testing import CliRunner

from .phase_stepping import PhaseCorrection, cli
from .signal_analysis import (
    PhaseCorrection as AnalysisPhaseCorrection,
    SweepMeasurement,
    compute_energy,
)


class PhaseSteppingTest(unittest.TestCase):

    def test_phase_correction_wraps_full_rotation(self):
        # Arrange
        base_correction = PhaseCorrection()
        base_correction.spectrum[2] = (1, 0)
        wrapped_correction = PhaseCorrection()
        wrapped_correction.spectrum[2] = (1, 2 * np.pi)
        opposite_correction = PhaseCorrection()
        opposite_correction.spectrum[2] = (1, np.pi)

        # Act
        base_currents = base_correction.currents()
        wrapped_currents = wrapped_correction.currents()
        opposite_currents = opposite_correction.currents()

        # Assert
        self.assertEqual(base_currents, wrapped_currents)
        self.assertNotEqual(base_currents, opposite_currents)

    def test_facade_preserves_phase_correction_import(self):
        # Arrange / Act / Assert
        self.assertIs(PhaseCorrection, AnalysisPhaseCorrection)

    def test_sweep_measurement_parses_command_response(self):
        # Arrange
        response = [
            "sampling_freq: 1300",
            "movement_ok: true",
            "accel_error: 0",
            "start_marker: 0.25",
            "end_marker: 0.75",
            "signal_start: 0.30",
            "signal_end: 0.70",
            "0,1.5",
            "1,-2.25",
        ]

        # Act
        measurement = SweepMeasurement.from_raw_command(response)

        # Assert
        self.assertEqual(measurement.samples, [1.5, -2.25])
        self.assertEqual(measurement.sampling_freq, 1300)
        self.assertTrue(measurement.is_ok())
        self.assertEqual((measurement.start_marker, measurement.end_marker),
                         (0.25, 0.75))
        self.assertEqual((measurement.signal_start, measurement.signal_end),
                         (0.30, 0.70))

    def test_compute_energy_matches_rolling_firmware_algorithm(self):
        # Arrange
        samples = [1, 2, 3, 4, 5]

        # Act
        energy = compute_energy(samples, start_idx=2, end_idx=5, win=2)

        # Assert
        self.assertEqual(energy, [25, 37, 53])

    def test_cli_lists_existing_commands(self):
        # Arrange
        runner = CliRunner()

        # Act
        result = runner.invoke(cli, ["--help"])

        # Assert
        self.assertEqual(result.exit_code, 0)
        for command in (
                "analyzeParamSweep",
                "analyzeSpeedSweep",
                "debugCalibration",
                "findOptimalMagnitude",
                "readLut",
                "writeLut",
        ):
            self.assertIn(command, result.output)


if __name__ == "__main__":
    unittest.main()
