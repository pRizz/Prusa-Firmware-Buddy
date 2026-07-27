"""Serial-machine adapter for phase-stepping calibration."""

from contextlib import contextmanager
from typing import Generator, List, Optional

import serial.tools.list_ports
from serial import Serial  # type: ignore

try:
    from .signal_analysis import PhaseCorrection
except ImportError:
    from signal_analysis import PhaseCorrection

PRUSA_VID = 0x2c99


class Machine:

    def __init__(self, port: Serial) -> None:
        self._port = port
        self.accFreq = None

    @contextmanager
    def _preserveTimeout(self) -> Generator[None, None, None]:
        originalTimeout = self._port.timeout
        try:
            yield
        finally:
            self._port.timeout = originalTimeout

    def waitForBoot(self) -> None:
        """
        Wait for the board to boot up - that is no new info is echoed
        """
        self.command("G")

    def command(self, command: str, timeout: float = 10) -> List[str]:
        """
        Issue G-code command, waits for completion and returns a list of
        returned values (lines of response)
        """
        if not command.endswith("\n"):
            command += "\n"
        with self._preserveTimeout():
            # Clear pending data
            self._port.timeout = None
            self._port.read_all()
            # Send command
            self._port.write(command.encode("utf-8"))
            # Wait for response
            response = []
            if timeout != 0:
                self._port.timeout = timeout
            else:
                self._port.timeout = 3
            while True:
                line = self._port.readline().decode("utf-8").strip()
                if line == "":
                    if timeout != 0:
                        raise TimeoutError(
                            f"No response on command {command.strip()}")
                    else:
                        return response
                line = line.strip()
                if line.endswith("ok"):
                    if line[:-2] != "":
                        response.append(line[:-2])
                    return response
                response.append(line)

    def multiCommand(self,
                     commands: List[str],
                     timeout: float = 10) -> List[str]:
        """
        Issue multiple G-code commands at once, return line summary.
        """
        command = "\n".join(commands) + "\n"
        okCount = 0
        with self._preserveTimeout():
            # Clear pending data
            self._port.timeout = None
            self._port.read_all()
            # Send command
            self._port.write(command.encode("utf-8"))
            # Wait for response
            response = []
            if timeout != 0:
                self._port.timeout = timeout
            else:
                self._port.timeout = 3
            while True:
                line = self._port.readline().decode("utf-8").strip()
                if line == "":
                    if timeout != 0:
                        raise TimeoutError(
                            f"No response on command {command.strip()}")
                    else:
                        return response
                line = line.strip()
                if line.endswith("ok"):
                    if line[:-2] != "":
                        response.append(line[:-2])
                    okCount += 1
                    if okCount == len(commands):
                        return response
                response.append(line)


def getPrusaPort() -> Optional[str]:
    """
    Return first port that belongs to a Prusa machine
    """
    for port in serial.tools.list_ports.comports():
        if port.vid == PRUSA_VID:
            return port.device
    return None


@contextmanager
def machineConnection(port: str = getPrusaPort()) -> Generator[Machine, None,
                                                               None]:
    with Serial(port) as s:
        yield Machine(s)


@contextmanager
def enabledMachineConnection(port: str = getPrusaPort()) -> Generator[
        Machine, None, None]:
    with Serial(port) as s:
        m = Machine(s)
        m.waitForBoot()
        m.command("M17")
        m.command("M970 X1 Y1")
        yield m
        m.command("M18")


def readLut(machine: Machine, axis: str, direction: str) -> PhaseCorrection:
    prefix = f"M971 {axis} {direction}"
    rawResponse = machine.command(prefix)

    correction = PhaseCorrection()
    for line in rawResponse:
        if not line.startswith(prefix):
            continue
        line = line.removeprefix(prefix).strip()
        idx, mag, pha = line.split(" ")
        idx = int(idx.removeprefix('I'))
        mag = float(mag.removeprefix('M'))
        pha = float(pha.removeprefix('P'))

        correction.spectrum[idx] = (mag, pha)
    return correction


def writeLut(machine: Machine, axis: str, direction: str,
             correction: PhaseCorrection) -> None:
    machine.command(f"M970 {axis}0")
    idx = 0
    for mag, pha in correction.spectrum[:17]:
        machine.command(f"M971 {axis}{direction} I{idx} M{mag:.7g} P{pha:.7g}")
        idx += 1
    machine.command(f"M970 {axis}1")
