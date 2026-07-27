"""Preset loading and IDE/CMake generation for ``utils/build.py``."""

import json
import os
import shutil
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path
from typing import List
from uuid import uuid4

from build_config import (BuildConfiguration, FirmwareBuildConfiguration,
                          Preset, get_dependency, project_root)

presets_dir = project_root / 'utils' / 'presets'


class CProjectGenerator:

    @staticmethod
    def create_cmake_def(name, value_type, value) -> ET.Element:
        definition = ET.Element('def')
        definition.attrib['name'] = name
        definition.attrib['type'] = value_type
        definition.attrib['val'] = value
        return definition

    @staticmethod
    def generate_language_settings(cconfigurations):
        """Generate .settings/language.settings.xml file."""
        settings = ET.parse(project_root / 'utils' / 'cproject' /
                            'template_language_settings.xml')
        project = settings.getroot()
        template = project.find('./configuration')
        assert template is not None, 'invalid template'

        for cconfiguration in cconfigurations:
            new_config = deepcopy(template)
            managedbuilder_config = cconfiguration.find(
                './storageModule[@buildSystemId="org.eclipse.cdt'
                '.managedbuilder.core.configurationDataProvider"]')
            new_config.attrib['id'] = managedbuilder_config.attrib['id']
            new_config.attrib['name'] = managedbuilder_config.attrib['name']
            project.append(new_config)

        output_path = project_root / '.settings' / 'language.settings.xml'
        os.makedirs(output_path.parent, exist_ok=True)
        with open(output_path, 'wb') as output_file:
            output_file.write(
                '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'.
                encode())
            settings.write(output_file)
        print('generated: .settings/language.settings.xml')

    @staticmethod
    def generate_core_settings():
        """Generate .settings/org.eclipse.cdt.core.prefs file."""
        shutil.copy(
            project_root / 'utils' / 'cproject' /
            'template_org_eclipse_cdt_core.prefs',
            project_root / '.settings' / 'org.eclipse.cdt.core.prefs')
        print('generated: .settings/org.eclipse.cdt.core.prefs')

    @staticmethod
    def generate_project():
        shutil.copy(
            project_root / 'utils' / 'cproject' / 'template_project.xml',
            project_root / '.project')
        print('generated: .project')

    @staticmethod
    def get_element(source: ET.Element, element_path: str) -> ET.Element:
        result = source.find(element_path)
        assert result is not None
        return result

    @staticmethod
    def generate_cconfiguration(
            template: ET.Element,
            configuration: BuildConfiguration) -> ET.Element:
        get_element = CProjectGenerator.get_element
        cconfiguration = deepcopy(template)
        cmake_defines = [
            CProjectGenerator.create_cmake_def(*entry)
            for entry in configuration.get_cmake_cache_entries()
        ]
        name = configuration.name.upper()
        build_subdir = 'cproject-fw' if isinstance(
            configuration, FirmwareBuildConfiguration) else 'cproject-host'

        identifier = 'com.st.stm32cube.ide.mcu.gnu.managedbuild.config.exe.debug.'
        identifier += str(uuid4()).replace('-', '')
        cconfiguration.attrib['id'] = identifier

        managedbuilder_config = get_element(
            cconfiguration, './storageModule[@buildSystemId="org.eclipse.cdt'
            '.managedbuilder.core.configurationDataProvider"]')
        managedbuilder_config.attrib['id'] = identifier
        managedbuilder_config.attrib['name'] = name

        cdt_build_system = get_element(
            cconfiguration, './storageModule[@moduleId="cdtBuildSystem"]')
        build_config = get_element(cdt_build_system, 'configuration')
        build_config.attrib['name'] = name
        build_config.attrib['id'] = identifier
        folder_info = get_element(build_config, 'folderInfo')
        folder_info.attrib['id'] = identifier + '.'
        builder = get_element(get_element(folder_info, 'toolChain'), 'builder')
        builder.attrib['buildPath'] = '/build/' + build_subdir

        cmake_config = get_element(
            cconfiguration,
            './storageModule[@moduleId="de.marw.cdt.cmake.core.settings"]')
        cmake_config.attrib['buildDir'] = 'build/' + build_subdir
        get_element(cmake_config, 'defs').extend(cmake_defines)
        cmake_path = str(get_dependency('cmake'))
        for platform_name in ('linux', 'win32'):
            get_element(cmake_config,
                        platform_name).attrib['command'] = cmake_path
        return cconfiguration

    @staticmethod
    def generate(configurations: List[BuildConfiguration]):
        """Generate a .cproject and .project with given configurations."""
        get_element = CProjectGenerator.get_element
        template = ET.parse(project_root / 'utils' / 'cproject' /
                            'template_cproject.xml')
        cproject = template.getroot()
        core_settings = get_element(
            cproject,
            './storageModule[@moduleId="org.eclipse.cdt.core.settings"]')
        all_configurations = core_settings.findall('cconfiguration')
        assert len(all_configurations) == 1
        configuration_template = all_configurations[0]
        core_settings.remove(configuration_template)
        for configuration in configurations:
            generated = CProjectGenerator.generate_cconfiguration(
                template=configuration_template, configuration=configuration)
            core_settings.append(generated)
        with open(project_root / '.cproject', 'wb') as output_file:
            output_file.write(
                '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'.
                encode())
            output_file.write('<?fileVersion 4.0.0?>\n'.encode())
            template.write(output_file)
        print('generated: .cproject')
        CProjectGenerator.generate_project()
        CProjectGenerator.generate_language_settings(core_settings)
        CProjectGenerator.generate_language_settings(core_settings)
        CProjectGenerator.generate_core_settings()


class CMakePresetsGenerator:

    @staticmethod
    def normalize_cache_value(value, value_type):
        if value_type.lower() != 'filepath' or not value:
            return value
        return '${sourceDir}/' + str(
            Path(os.path.abspath(value)).relative_to(project_root).as_posix())

    @staticmethod
    def build_dir_for_configuration(configuration: BuildConfiguration) -> str:
        if not isinstance(configuration, FirmwareBuildConfiguration):
            return 'build-vscode-host'
        if 'dwarf' in configuration.preset.name:
            return 'build-vscode-dwarf'
        if 'modularbed' in configuration.preset.name:
            return 'build-vscode-modularbed'
        if 'xbuddy-extension' in configuration.preset.name:
            return 'build-vscode-xbuddy-extension'
        return 'build-vscode-buddy'

    @staticmethod
    def generate_cmake_preset(configuration: BuildConfiguration):
        build_dir = CMakePresetsGenerator.build_dir_for_configuration(
            configuration)
        return {
            'name': configuration.name,
            'generator': configuration.generator,
            'binaryDir': build_dir,
            'cacheVariables': {
                key: {
                    'type':
                    value_type,
                    'value':
                    CMakePresetsGenerator.normalize_cache_value(
                        value, value_type)
                }
                for key, value_type, value in
                configuration.get_cmake_cache_entries()
            }
        }

    @staticmethod
    def generate(configurations: List[BuildConfiguration]):
        """Generate CMakePresets.json file."""
        cmake_presets = {
            'version':
            3,
            'cmakeMinimumRequired': {
                'major': 3,
                'minor': 21,
                'patch': 0,
            },
            'configurePresets': [
                CMakePresetsGenerator.generate_cmake_preset(configuration)
                for configuration in configurations
            ]
        }
        with open(project_root / 'CMakePresets.json', 'w') as output_file:
            json.dump(cmake_presets, output_file, indent=4)
            output_file.write('\n')


def load_presets() -> List[Preset]:
    presets_file_path = presets_dir / 'presets.json'
    with open(presets_file_path, 'r') as presets_file:
        data = json.load(presets_file)
    return [
        Preset(name=preset_data['name'],
               description=preset_data['description'],
               cache_variables=preset_data['cacheVariables'])
        for preset_data in data['presets']
    ]
