#!/usr/bin/env python3
"""Developer and CI build command façade."""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict

project_root = Path(__file__).resolve().parent.parent
dependencies_dir = project_root / '.dependencies'
utils_dir = project_root / 'utils'
presets_dir = utils_dir / 'presets'

# Add utils to the import path so this script also works as a direct entrypoint.
sys.path.insert(0, str(utils_dir))

import bootstrap
from build_config import (Bootloader, BuildConfiguration, BuildLayout,
                          BuildResult, BuildType, CaseInsensitiveEnum,
                          FirmwareBuildConfiguration, HostTool,
                          HostToolBuildConfiguration, Preset, build,
                          get_dependency)
from build_presets import (CMakePresetsGenerator, CProjectGenerator,
                           load_presets)
from build_products import project_version, store_products


def bootstrap_(*args, interactive=False):
    """Run the bootstrap script."""
    bootstrap_py = utils_dir / 'bootstrap.py'
    return subprocess.run([sys.executable, str(bootstrap_py)] + list(args),
                          check=False,
                          encoding='utf-8',
                          stdout=None if interactive else subprocess.PIPE,
                          stderr=None if interactive else subprocess.PIPE)


def list_of(value_type, *, all_values, name):
    """Create an argument-parser for comma-separated list of values."""

    def convert(val):
        if val == '':
            return []
        values = [part.lower() for part in val.split(',')]
        if 'all' in values:
            return all_values
        return [value_type(value) for value in values]

    convert.__name__ = name
    return convert


def cmake_cache_entry(arg):
    match = re.fullmatch(r'(.*):(.*)=(.*)', arg)
    if not match:
        raise ValueError('invalid cmake entry; must be <NAME>:<TYPE>=<VALUE>')
    return (match.group(1), match.group(2), match.group(3))


def create_argument_parser(all_presets):
    """Create the stable command-line interface for the build entrypoint."""
    parser = argparse.ArgumentParser()
    # yapf: disable
    parser.add_argument(
        '--preset',
        type=list_of(str, all_values=[preset.name for preset in all_presets], name='Variant'),
        default='all',
        help='Presets of the firmware to build (default: {default})'.format(
            default=','.join(preset.name for preset in all_presets)))
    parser.add_argument(
        '--build-type',
        type=list_of(BuildType, all_values=list(BuildType), name='BuildType'),
        default='release',
        help=('Build type (debug or release; default: release; '
              'default for --generate-cproject: debug,release).'))
    parser.add_argument(
        '--bootloader',
        type=list_of(Bootloader, all_values=list(Bootloader), name='Bootloader'),
        default='yes,no',
        help='What bootloader mode to use ("yes", "no" or "empty"; default: "empty").')
    parser.add_argument(
        '--signing-key',
        type=Path,
        help='A PEM private key to be used to generate .bbf version.')
    parser.add_argument(
        '--version-suffix',
        type=str,
        default='<auto>',
        help='Version suffix (e.g. -BETA+1035.PR111.B4)')
    parser.add_argument(
        '--version-suffix-short',
        type=str,
        default='<auto>',
        help='Version suffix (e.g. +1035)')
    parser.add_argument(
        '--final',
        action='store_true',
        help='Set\'s --version-suffix and --version-suffix-short to empty string.')
    parser.add_argument(
        '--build-dir',
        type=Path,
        help='Specify a custom build directory to be used.')
    parser.add_argument(
        '--products-dir',
        type=Path,
        help='Directory to store built firmware (default: <build-dir>/products).')
    parser.add_argument(
        '-G', '--generator',
        type=str,
        default='Ninja',
        help='Generator to be used by CMake (default=Ninja).')
    parser.add_argument(
        '--toolchain',
        type=Path,
        help='Path to a CMake toolchain file to be used.')
    parser.add_argument(
        '--generate-dfu',
        action='store_true',
        help='Generate .dfu versions of the firmware.'
    )
    parser.add_argument(
        '--generate-cproject',
        action='store_true',
        help='Generate .cproject and .project files and exit without building.',
    )
    parser.add_argument(
        '--generate-cmake-presets',
        action='store_true',
        help='Generate CMakePresets.json and exit without building.',
    )
    parser.add_argument(
        '--host-tools',
        action='store_true',
        help=('Build host tools (png2font and others). '
              'Turned on by default with --generate-cproject only.')
    )
    parser.add_argument(
        '--no-build',
        action='store_true',
        help='Do not build, configure the build only.'
    )
    parser.add_argument(
        '--skip-bootstrap',
        action='store_true',
        help='Skip bootstrap, useful if dependencies are already installed.'
    )
    parser.add_argument(
        '--no-store-output',
        dest='store_output',
        action='store_const',
        const=False,
        help='Do not write build output to files - print it to console instead.'
    )
    parser.add_argument(
        '--store-output',
        dest='store_output',
        action='store_const',
        const=True,
        help='Write build output to files - print it to console instead.'
    )
    parser.add_argument(
        '-D', '--cmake-def',
        action='append', type=cmake_cache_entry,
        help='Custom CMake cache entries (e.g. -DCUSTOM_COMPILE_OPTIONS:STRING=-Werror)'
    )
    # yapf: enable
    return parser


def create_configurations(args, all_presets):
    """Translate parsed command-line options into build configurations."""
    selected_preset_names = [
        preset_name.lower() for preset_name in args.preset
    ]
    selected_presets = [
        preset for preset in all_presets
        if preset.name.lower() in selected_preset_names
    ]
    generate_project_files = args.generate_cproject or args.generate_cmake_presets
    build_layout = BuildLayout.DEVELOPMENT if generate_project_files else BuildLayout.COMMON_BUILD_DIR
    configurations = [
        FirmwareBuildConfiguration(
            preset=preset,
            bootloader=bootloader,
            build_type=build_type,
            build_layout=build_layout,
            generate_dfu=args.generate_dfu,
            signing_key=args.signing_key,
            version_suffix=args.version_suffix,
            version_suffix_short=args.version_suffix_short,
            generator=args.generator,
            toolchain=args.toolchain,
            custom_entries=args.cmake_def) for preset in selected_presets
        for build_type in args.build_type for bootloader in args.bootloader
    ]
    if args.host_tools:
        configurations.extend([
            HostToolBuildConfiguration(tool=tool,
                                       build_type=build_type,
                                       generator=args.generator)
            for tool in HostTool for build_type in args.build_type
        ])
    return configurations


def report_results(results):
    """Print the stable build summary and return whether any build failed."""
    print()
    print('Building finished: {} success, {} failure(s).'.format(
        sum(1 for result in results.values() if not result.is_failure),
        sum(1 for result in results.values() if result.is_failure)))
    failure = False
    max_configuration_name_length = max(
        len(configuration.name) for configuration in results)
    for configuration, result in results.items():
        if result.configuration_failed:
            status = 'project configuration FAILED'
            failure = True
        elif result.build_failed:
            status = 'build FAILED'
            failure = True
        else:
            status = 'SUCCESS'
        print(' {} {}'.format(
            configuration.name.lower().ljust(max_configuration_name_length,
                                             ' '), status))
    return failure


def main():
    all_presets = load_presets()
    args = create_argument_parser(all_presets).parse_args(sys.argv[1:])
    bootstrap.switch_to_venv_if_nedded()

    build_dir_root = args.build_dir or project_root / 'build'
    products_dir_root = args.products_dir or (build_dir_root / 'products')

    if args.final:
        args.version_suffix = ''
        args.version_suffix_short = ''

    if args.generate_cproject or args.generate_cmake_presets:
        args.build_type = list(BuildType)
        args.host_tools = True
        args.no_build = True

    configurations = create_configurations(args, all_presets)
    if args.generate_cproject:
        CProjectGenerator.generate(configurations)
        return
    if args.generate_cmake_presets:
        CMakePresetsGenerator.generate(configurations)
        return

    if not args.skip_bootstrap:
        bootstrap.bootstrap()

    results: Dict[BuildConfiguration, BuildResult] = {}
    for configuration in configurations:
        build_dir = build_dir_root / configuration.name.lower()
        print('Building ' + configuration.name.lower())
        result = build(configuration,
                       build_dir=build_dir,
                       configure_only=args.no_build,
                       output_to_file=args.store_output
                       if args.store_output is not None else False)
        store_products(result.products, configuration, products_dir_root)
        results[configuration] = result

    if report_results(results):
        sys.exit(1)


if __name__ == '__main__':
    main()
