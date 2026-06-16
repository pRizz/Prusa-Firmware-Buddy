# Phase 1 Baseline Matrix

## Requirement Coverage

- **BASE-01:** Maintainer can inspect a complete supported printer, board, MCU, bootloader, feature, and artifact matrix derived from the existing firmware reference.

## Source Of Truth

The matrix below is derived from the current C/C++/CMake/Python reference, not from future Rust or Bazel assumptions.

| Source | Baseline Role |
|--------|---------------|
| `ProjectOptions.cmake` | Defines printer, board, MCU, bootloader, and feature option values. |
| `utils/presets/presets.json` | Source data for supported preset combinations. |
| `CMakePresets.json` | Generated maintainer-visible preset surface. |
| `CMakeLists.txt` | Firmware target graph, packaging outputs, generated headers, and board-specific source inclusion. |
| `utils/build.py` | High-level current build, preset generation, DFU generation, and product staging wrapper. |
| `cmake/Littlefs.cmake` | LittleFS/resource image generation behavior. |
| `utils/pack_fw.py` | Firmware packaging helper for release artifacts. |

## Supported Product Matrix

### Printers

| Printer | Status | Primary Evidence |
|---------|--------|------------------|
| `COREONE` | supported-reference | `ProjectOptions.cmake`, `utils/presets/presets.json` |
| `MINI` | supported-reference | `ProjectOptions.cmake`, `utils/presets/presets.json` |
| `MK4` | supported-reference | `ProjectOptions.cmake`, `utils/presets/presets.json` |
| `MK3.5` | supported-reference | `ProjectOptions.cmake`, `utils/presets/presets.json` |
| `XL` | supported-reference | `ProjectOptions.cmake`, `utils/presets/presets.json` |
| `iX` | supported-reference | `ProjectOptions.cmake`, `utils/presets/presets.json` |
| `XL_DEV_KIT` | supported-reference | `ProjectOptions.cmake`, `utils/presets/presets.json` |

### Boards

| Board | Status | Primary Evidence |
|-------|--------|------------------|
| `BUDDY` | supported-reference | `ProjectOptions.cmake` |
| `XBUDDY` | supported-reference | `ProjectOptions.cmake` |
| `XLBUDDY` | supported-reference | `ProjectOptions.cmake` |
| `DWARF` | supported-reference | `ProjectOptions.cmake` |
| `MODULARBED` | supported-reference | `ProjectOptions.cmake` |
| `XL_DEV_KIT_XLB` | supported-reference | `ProjectOptions.cmake` |
| `XBUDDY_EXTENSION` | supported-reference | `ProjectOptions.cmake` |

### MCU Families

| MCU | Status | Primary Evidence |
|-----|--------|------------------|
| `STM32F407VG` | supported-reference | `ProjectOptions.cmake`, `cmake/GccArmNoneEabi.cmake` |
| `STM32F429VI` | supported-reference | `ProjectOptions.cmake`, `cmake/GccArmNoneEabi.cmake` |
| `STM32F427ZI` | supported-reference | `ProjectOptions.cmake`, `cmake/GccArmNoneEabi.cmake` |
| `STM32G070RBT6` | supported-reference | `ProjectOptions.cmake`, `cmake/GccArmNoneEabi.cmake` |
| `STM32H503CBU7` | supported-reference | `ProjectOptions.cmake`, `cmake/GccArmNoneEabi.cmake` |

### Bootloader And Build Modes

| Surface | Reference Status | Source |
|---------|------------------|--------|
| Boot/noboot firmware variants | supported-reference | `ProjectOptions.cmake`, `utils/build.py`, `CMakeLists.txt` |
| DFU generation | supported-reference | `utils/build.py`, `utils/dfu.py`, `CMakeLists.txt` |
| Puppy/auxiliary firmware packages | supported-reference | `CMakeLists.txt`, `utils/gen_puppies_descriptor.py` |
| Signing key path (`SIGNING_KEY`) | external-input | `ProjectOptions.cmake`, `utils/build.py` |

## Feature And Artifact Surface

### Major Feature Flags

| Feature Flag | Reference Status | Source |
|--------------|------------------|--------|
| `WUI` | supported-reference | `ProjectOptions.cmake`, `lib/WUI/` |
| `CONNECT` | supported-reference | `ProjectOptions.cmake`, `src/connect/` |
| `RESOURCES` | supported-reference | `ProjectOptions.cmake`, `src/resources/`, `cmake/Littlefs.cmake` |
| `TRANSLATIONS_ENABLED` | supported-reference | `ProjectOptions.cmake`, `utils/translations_and_fonts/` |
| `TOUCH_ENABLED` | supported-reference | `ProjectOptions.cmake`, `src/gui/` |
| `HAS_MMU2` | supported-reference | `ProjectOptions.cmake`, `src/mmu2/`, `lib/AddMMU2.cmake` |
| `HAS_PUPPIES` | supported-reference | `ProjectOptions.cmake`, `src/puppies/` |
| `HAS_DWARF` | supported-reference | `ProjectOptions.cmake`, `src/puppy/dwarf/` |
| `HAS_PUPPY_MODULARBED` | supported-reference | `ProjectOptions.cmake`, `src/puppy/modularbed/` |
| `HAS_XBUDDY_EXTENSION` | supported-reference | `ProjectOptions.cmake`, `src/puppy/xbuddy_extension/` |
| `HAS_USB_DEVICE` | supported-reference | `ProjectOptions.cmake`, `src/buddy/usb_device.cpp` |
| `HAS_NFC` | supported-reference | `ProjectOptions.cmake` |

### Release Artifact Types

| Artifact | Reference Status | Source |
|----------|------------------|--------|
| `.bin` | supported-reference | `CMakeLists.txt`, `utils/build.py` |
| `.bbf` | supported-reference | `CMakeLists.txt`, `utils/pack_fw.py` |
| `.dfu` | supported-reference | `CMakeLists.txt`, `utils/build.py`, `utils/dfu.py` |
| `.map` | supported-reference | `CMakeLists.txt` |
| LittleFS/resource images | supported-reference | `cmake/Littlefs.cmake`, `utils/mklittlefs.py` |
| Translation/font generated headers | supported-reference | `utils/translations_and_fonts/`, `src/gui/res/cc/`, `src/guiapi/include/` |

## Refresh Rules

1. Refresh this matrix whenever `ProjectOptions.cmake`, `utils/presets/presets.json`, `CMakePresets.json`, `CMakeLists.txt`, or `utils/build.py` changes in a way that affects supported combinations.
2. Mark unknown or hardware-dependent values as `manual-evidence-needed`; do not guess.
3. Do not treat Bazel as authoritative for this matrix until Phase 2 and Phase 3 explicitly replace the source of truth.
4. Do not include private signing key material, network credentials, tokens, certificates, or crash dump contents in this artifact.
