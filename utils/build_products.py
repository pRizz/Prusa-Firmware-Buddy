"""Artifact publication helpers for ``utils/build.py``."""

import shutil
from pathlib import Path
from typing import List

from build_config import BuildConfiguration, FirmwareBuildConfiguration

project_root = Path(__file__).resolve().parent.parent


def project_version():
    """Return current project version (e.g. ``4.0.3``)."""
    with open(project_root / 'version.txt', 'r') as version_file:
        return version_file.read().strip()


def store_products(products: List[Path], build_config: BuildConfiguration,
                   products_dir: Path):
    """Copy build products to a shared products directory."""
    products_dir.mkdir(parents=True, exist_ok=True)
    for product in products:
        base_name = build_config.name.lower()
        if isinstance(build_config, FirmwareBuildConfiguration
                      ) and build_config.version_suffix != '<auto>':
            version = project_version()
            name = base_name + '_' + version + (build_config.version_suffix
                                                or '')
        else:
            name = base_name
        destination = products_dir / (name + product.suffix)
        shutil.copy(product, destination)
