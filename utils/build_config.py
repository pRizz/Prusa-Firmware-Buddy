"""Build configuration types and CMake execution for ``utils/build.py``."""

import subprocess
from abc import ABC, abstractmethod
from collections import namedtuple
from enum import Enum, auto
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple

import bootstrap

project_root = Path(__file__).resolve().parent.parent

Preset = namedtuple('Preset', ['name', 'description', 'cache_variables'])


@lru_cache()
def get_dependency(name):
    """Return an installation path of a dependency."""
    install_dir = bootstrap.get_dependency_directory(name)
    if name == 'ninja':
        return install_dir / 'ninja'
    if name == 'cmake':
        return install_dir / 'bin' / 'cmake'
    return install_dir


class CaseInsensitiveEnum(Enum):

    @classmethod
    def _missing_(cls, name):
        for member in cls:
            if member.name.lower() == name.lower():
                return member


class Bootloader(CaseInsensitiveEnum):
    """Represents the -DBOOTLOADER CMake option."""

    NO = 'no'
    EMPTY = 'empty'
    YES = 'yes'

    @property
    def file_component(self):
        if self == Bootloader.NO:
            return 'noboot'
        if self == Bootloader.EMPTY:
            return 'emptyboot'
        if self == Bootloader.YES:
            return 'boot'
        raise NotImplementedError


class BuildType(CaseInsensitiveEnum):
    """Represents the -DCONFIG CMake option."""

    DEBUG = 'debug'
    RELEASE = 'release'


class HostTool(CaseInsensitiveEnum):
    """Known host tools."""

    png2font = 'png2font'
    unittests = 'unittests'


class BuildConfiguration(ABC):

    @abstractmethod
    def get_cmake_cache_entries(self) -> List[Tuple[str, str, str]]:
        """Convert the build configuration to CMake cache entries."""

    @abstractmethod
    def get_cmake_flags(self, build_dir: Path) -> List[str]:
        """Return all CMake command-line flags required for this configuration."""

    name: str
    build_type: BuildType
    generator: str

    def __hash__(self):
        return hash(self.name)


class BuildLayout(Enum):
    DEVELOPMENT = auto()
    """
    Used when configuring future build (cproject, etc).
    Build dirs are placed under build-vscode-(buddy,dwarf,modularbed,xbuddy-extension).
    """

    COMMON_BUILD_DIR = auto()
    """
    Used when building multiple configurations.
    Build dirs are placed under build/<printer>_(release/debug)_(no,)boot>.
    """


class FirmwareBuildConfiguration(BuildConfiguration):

    def __init__(self,
                 *,
                 preset: Preset,
                 bootloader: Bootloader,
                 build_type: BuildType,
                 build_layout: BuildLayout,
                 toolchain: Optional[Path] = None,
                 generator: str = 'Ninja',
                 generate_dfu: bool = False,
                 signing_key: Optional[Path] = None,
                 version_suffix: Optional[str] = None,
                 version_suffix_short: Optional[str] = None,
                 custom_entries: Optional[List[str]] = None):
        self.preset = preset
        self.build_type = build_type
        self.bootloader = bootloader
        self.build_layout = build_layout
        self.toolchain = toolchain or FirmwareBuildConfiguration.default_toolchain(
        )
        self.generator = generator
        self.generate_dfu = generate_dfu
        self.signing_key = signing_key
        self.version_suffix = version_suffix
        self.version_suffix_short = version_suffix_short
        self.custom_entries = custom_entries or []

    @staticmethod
    def default_toolchain() -> Path:
        return project_root / 'cmake/GccArmNoneEabi.cmake'

    def get_cmake_cache_entries(self):
        signing_key_flag = self.signing_key.resolve(
        ) if self.signing_key else ''
        entries = []

        if self.generator.lower() == 'ninja':
            entries.append(('CMAKE_MAKE_PROGRAM', 'FILEPATH',
                            str(get_dependency('ninja'))))

        for name, value in self.preset.cache_variables.items():
            ignored_in_common_layout = [
                'MODULARBED_BINARY_DIR', 'DWARF_BINARY_DIR',
                'XBUDDY_EXTENSION_BINARY_DIR'
            ]
            if self.build_layout == BuildLayout.COMMON_BUILD_DIR and name in ignored_in_common_layout:
                continue
            if isinstance(value, bool):
                entries.append((name, 'BOOL', 'YES' if value else 'NO'))
            elif isinstance(value, str):
                entries.append((name, 'STRING', value))
            elif isinstance(value, dict):
                entries.append((name, value['type'], value['value']))
            else:
                raise AssertionError("unexpected preset's value type")

        entries.extend([
            ('BOOTLOADER', 'STRING', self.bootloader.value.upper()),
            ('GENERATE_DFU', 'BOOL', 'ON' if self.generate_dfu else 'OFF'),
            ('SIGNING_KEY', 'FILEPATH', str(signing_key_flag)),
            ('CMAKE_TOOLCHAIN_FILE', 'FILEPATH', str(self.toolchain)),
            ('CMAKE_BUILD_TYPE', 'STRING', self.build_type.value.title()),
            ('PROJECT_VERSION_SUFFIX', 'STRING', self.version_suffix or ''),
            ('PROJECT_VERSION_SUFFIX_SHORT', 'STRING',
             self.version_suffix_short or ''),
        ])
        entries.extend(self.custom_entries)
        return entries

    def get_cmake_flags(self, build_dir: Path) -> List[str]:
        flags = [
            '-D{}:{}={}'.format(*entry)
            for entry in self.get_cmake_cache_entries()
        ]
        flags += [
            '-U{}'.format(name)
            for name, value in self.preset.cache_variables.items()
            if value is None
        ]
        flags += ['-G', self.generator]
        flags += ['-S', str(project_root)]
        flags += ['-B', str(build_dir)]
        return flags

    @property
    def name(self):
        return '_'.join([
            self.preset.name,
            self.build_type.value,
            self.bootloader.file_component,
        ])


class HostToolBuildConfiguration(BuildConfiguration):

    def __init__(self,
                 build_type: BuildType,
                 tool: HostTool,
                 generator: str = 'Ninja'):
        self.build_type = build_type
        self.tool = tool
        self.generator = generator

    def get_cmake_cache_entries(self):
        entries = []
        if self.generator.lower() == 'ninja':
            entries.append(('CMAKE_MAKE_PROGRAM', 'FILEPATH',
                            str(get_dependency('ninja'))))
        entries.extend((tool.value.upper() + '_ENABLE', 'BOOL',
                        'YES' if tool == self.tool else 'NO')
                       for tool in HostTool)
        return entries

    def get_cmake_flags(self, build_dir: Path) -> List[str]:
        flags = [
            '-D{}:{}={}'.format(*entry)
            for entry in self.get_cmake_cache_entries()
        ]
        flags += ['-G', self.generator or 'Ninja']
        flags += ['-S', str(project_root)]
        flags += ['-B', str(build_dir)]
        return flags

    @property
    def name(self):
        return '_'.join([self.tool.value, self.build_type.value.lower()])


class BuildResult:
    """Represents a result of an attempt to build the project."""

    def __init__(self, config_returncode: int, build_returncode: Optional[int],
                 stdout: Optional[Path], stderr: Optional[Path],
                 products: List[Path]):
        self.config_returncode = config_returncode
        self.build_returncode = build_returncode
        self.stdout = stdout
        self.stderr = stderr
        self.products = products

    @property
    def configuration_failed(self):
        return self.config_returncode != 0

    @property
    def build_failed(self):
        return self.build_returncode != 0 and self.build_returncode is not None

    @property
    def is_failure(self):
        return self.configuration_failed or self.build_failed

    def __str__(self):
        return '<BuildResult config={self.config_returncode} build={self.build_returncode}>'.format(
            self=self)


def build(configuration: BuildConfiguration,
          build_dir: Path,
          configure_only=False,
          output_to_file=True) -> BuildResult:
    """Build a project with a single configuration."""
    flags = configuration.get_cmake_flags(build_dir=build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    products = []

    if output_to_file:
        stdout_path = build_dir / 'stdout.txt'
        stderr_path = build_dir / 'stderr.txt'
        stdout = open(stdout_path, 'w')
        stderr = open(stderr_path, 'w')
    else:
        stdout_path, stderr_path = None, None
        stdout, stderr = None, None

    config_process = subprocess.run([str(get_dependency('cmake'))] + flags,
                                    stdout=stdout,
                                    stderr=stderr,
                                    check=False)
    if not configure_only and config_process.returncode == 0:
        command = [
            str(get_dependency('cmake')), '--build',
            str(build_dir), '--config',
            configuration.build_type.value.lower()
        ]
        build_process = subprocess.run(command,
                                       stdout=stdout,
                                       stderr=stderr,
                                       check=False)
        build_returncode = build_process.returncode
        products.extend(build_dir / filename for filename in [
            'firmware', 'firmware.bin', 'firmware.bbf', 'firmware.dfu',
            'firmware.map'
        ] if (build_dir / filename).exists())
    else:
        build_returncode = None

    if stdout:
        stdout.close()
    if stderr:
        stderr.close()

    return BuildResult(config_returncode=config_process.returncode,
                       build_returncode=build_returncode,
                       stdout=stdout_path,
                       stderr=stderr_path,
                       products=products)
