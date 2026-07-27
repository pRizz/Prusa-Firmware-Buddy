#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import posixpath
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath

ROOT = Path(
    os.environ.get(
        "BUILD_WORKSPACE_DIRECTORY",
        Path(__file__).resolve().parents[2],
    ))
DEFAULT_LEDGER_PATH = ROOT / ".bright-builds-rules-checks.tsv"
CHECK_ID = "file-lengths"
TEMPORARY_REASON_PATTERN = re.compile(
    r"temporary: campaign=[a-z0-9][a-z0-9-]*; "
    r"remove when file is below 629 lines and campaign gates pass")
PERMANENT_REASON_PREFIXES = {
    "permanent: imported/upstream; provenance=": "imported",
    "permanent: generated; source=": "generated",
    "permanent: declarative registry; deletion-test=": "declarative",
}
OWNED_REASON_PREFIX = "permanent: owned deep module; deletion-test="


class PolicyError(ValueError):
    """Raised when the active file-length ledger violates Phase 40 policy."""


class ReasonKind(Enum):
    IMPORTED = "imported"
    GENERATED = "generated"
    DECLARATIVE = "declarative"
    TEMPORARY = "temporary"
    OWNED = "owned"


@dataclass(frozen=True)
class LedgerEntry:
    check_id: str
    path: str
    reason: str


@dataclass(frozen=True)
class PolicySummary:
    permanent_count: int
    temporary_count: int
    owned_permanent_count: int
    total_count: int


def _path_set(contents: str) -> frozenset[str]:
    return frozenset(contents.splitlines())


FROZEN_PERMANENT_PATHS = _path_set(
    "include/common/visit_all_struct_fields.hpp\ninclude/marlin/Configuration_COREONE.h\ninclude/marlin/Configuration_COREONE_adv.h\ninclude/marlin/Configuration_MINI.h\n"
    "include/marlin/Configuration_MINI_adv.h\ninclude/marlin/Configuration_MK3.5.h\ninclude/marlin/Configuration_MK3.5_adv.h\ninclude/marlin/Configuration_MK4.h\n"
    "include/marlin/Configuration_MK4_adv.h\ninclude/marlin/Configuration_XL.h\ninclude/marlin/Configuration_XL_DEV_KIT.h\ninclude/marlin/Configuration_XL_DEV_KIT_adv.h\n"
    "include/marlin/Configuration_XL_Dwarf.h\ninclude/marlin/Configuration_XL_Dwarf_adv.h\ninclude/marlin/Configuration_XL_adv.h\ninclude/marlin/Configuration_iX.h\n"
    "include/marlin/Configuration_iX_adv.h\nlib/Catch2/include/external/clara.hpp\nlib/Catch2/include/internal/catch_tostring.h\nlib/Catch2/include/reporters/catch_reporter_console.cpp\n"
    "lib/Catch2/projects/SelfTest/UsageTests/Matchers.tests.cpp\nlib/Catch2/single_include/catch2/catch.hpp\nlib/Drivers/CMSIS/Device/ST/STM32F4xx/Include/stm32f407xx.h\nlib/Drivers/CMSIS/Device/ST/STM32F4xx/Include/stm32f427xx.h\n"
    "lib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/_htmresc/mini-st.css\nlib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/_htmresc/mini-st_2020.css\nlib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/stm32g030xx.h\nlib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/stm32g031xx.h\n"
    "lib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/stm32g041xx.h\nlib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/stm32g050xx.h\nlib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/stm32g051xx.h\nlib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/stm32g061xx.h\n"
    "lib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/stm32g070xx.h\nlib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/stm32g071xx.h\nlib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/stm32g081xx.h\nlib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/stm32g0b0xx.h\n"
    "lib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/stm32g0b1xx.h\nlib/Drivers/CMSIS/Device/ST/STM32G0xx/Include/stm32g0c1xx.h\nlib/Drivers/CMSIS/Device/ST/STM32H5xx/Include/Templates/partition_stm32h523xx.h\nlib/Drivers/CMSIS/Device/ST/STM32H5xx/Include/Templates/partition_stm32h533xx.h\n"
    "lib/Drivers/CMSIS/Device/ST/STM32H5xx/Include/Templates/partition_stm32h562xx.h\nlib/Drivers/CMSIS/Device/ST/STM32H5xx/Include/Templates/partition_stm32h563xx.h\nlib/Drivers/CMSIS/Device/ST/STM32H5xx/Include/Templates/partition_stm32h573xx.h\nlib/Drivers/CMSIS/Device/ST/STM32H5xx/Include/stm32h503xx.h\n"
    "lib/Drivers/CMSIS/Device/ST/STM32H5xx/Include/stm32h523xx.h\nlib/Drivers/CMSIS/Device/ST/STM32H5xx/Include/stm32h533xx.h\nlib/Drivers/CMSIS/Device/ST/STM32H5xx/Include/stm32h562xx.h\nlib/Drivers/CMSIS/Device/ST/STM32H5xx/Include/stm32h563xx.h\n"
    "lib/Drivers/CMSIS/Device/ST/STM32H5xx/Include/stm32h573xx.h\nlib/Drivers/CMSIS/Device/ST/STM32H5xx/_htmresc/mini-st_2020.css\nlib/Drivers/CMSIS/Include/cmsis_armcc.h\nlib/Drivers/CMSIS/Include/cmsis_armclang.h\n"
    "lib/Drivers/CMSIS/Include/cmsis_gcc.h\nlib/Drivers/CMSIS/Include/cmsis_iccarm.h\nlib/Drivers/CMSIS/Include/core_armv8mbl.h\nlib/Drivers/CMSIS/Include/core_armv8mml.h\n"
    "lib/Drivers/CMSIS/Include/core_cm0.h\nlib/Drivers/CMSIS/Include/core_cm0plus.h\nlib/Drivers/CMSIS/Include/core_cm1.h\nlib/Drivers/CMSIS/Include/core_cm23.h\n"
    "lib/Drivers/CMSIS/Include/core_cm3.h\nlib/Drivers/CMSIS/Include/core_cm33.h\nlib/Drivers/CMSIS/Include/core_cm4.h\nlib/Drivers/CMSIS/Include/core_cm7.h\n"
    "lib/Drivers/CMSIS/Include/core_sc000.h\nlib/Drivers/CMSIS/Include/core_sc300.h\nlib/Drivers/lis2dh12-pid/_htmresc/mini-st_2020.css\nlib/Drivers/lis2dh12-pid/lis2dh12_reg.c\n"
    "lib/Drivers/lis2dh12-pid/lis2dh12_reg.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/Legacy/stm32_hal_legacy.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/Legacy/stm32f4xx_hal_can_legacy.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/Legacy/stm32f4xx_hal_eth_legacy.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_adc.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_can.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_cec.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_cryp.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_dfsdm.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_dma.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_dma2d.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_dsi.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_eth.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_flash_ex.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_fmpi2c.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_fmpsmbus.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_gpio_ex.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_hash.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_i2c.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_irda.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_lptim.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_ltdc.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_mmc.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_qspi.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_rcc.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_rcc_ex.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_rtc.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_rtc_ex.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_sai.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_sd.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_smartcard.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_smbus.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_spi.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_tim.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_uart.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_hal_usart.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_adc.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_bus.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_cortex.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_dac.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_dma.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_dma2d.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_exti.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_fmc.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_fmpi2c.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_fsmc.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_gpio.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_i2c.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_lptim.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_pwr.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_rcc.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_rtc.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_sdmmc.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_spi.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_system.h\nlib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_tim.h\n"
    "lib/Drivers/stm32f4xx_hal_driver/Inc/stm32f4xx_ll_usart.h\nlib/Drivers/stm32f4xx_hal_driver/Src/Legacy/stm32f4xx_hal_can.c\nlib/Drivers/stm32f4xx_hal_driver/Src/Legacy/stm32f4xx_hal_eth.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_adc.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_adc_ex.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_can.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_cec.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_cryp.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_cryp_ex.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_dac.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_dcmi.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_dfsdm.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_dma.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_dma2d.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_dsi.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_eth.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_flash.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_flash_ex.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_fmpi2c.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_fmpsmbus.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_hash.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_hash_ex.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_hcd.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_i2c.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_i2s.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_i2s_ex.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_irda.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_lptim.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_ltdc.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_mmc.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_nand.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_nor.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_pccard.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_pcd.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_qspi.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_rcc.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_rcc_ex.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_rng.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_rtc.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_rtc_ex.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_sai.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_sd.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_sdram.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_smartcard.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_smbus.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_spdifrx.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_spi.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_sram.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_tim.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_tim_ex.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_uart.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_hal_usart.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_ll_adc.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_ll_fmc.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_ll_fsmc.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_ll_rcc.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_ll_rtc.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_ll_sdmmc.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_ll_tim.c\nlib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_ll_usb.c\n"
    "lib/Drivers/stm32f4xx_hal_driver/Src/stm32f4xx_ll_utils.c\nlib/Drivers/stm32g0xx_hal_driver/Inc/Legacy/stm32_hal_legacy.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_adc.h\n"
    "lib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_cec.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_comp.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_cryp.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_dma.h\n"
    "lib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_fdcan.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_flash.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_gpio_ex.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_i2c.h\n"
    "lib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_irda.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_lptim.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_pcd.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_pwr_ex.h\n"
    "lib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_rcc.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_rcc_ex.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_rtc.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_rtc_ex.h\n"
    "lib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_smartcard.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_smbus.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_spi.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_tim.h\n"
    "lib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_uart.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_uart_ex.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_hal_usart.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_adc.h\n"
    "lib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_bus.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_comp.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_crs.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_dac.h\n"
    "lib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_dma.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_dmamux.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_exti.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_gpio.h\n"
    "lib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_i2c.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_lptim.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_lpuart.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_pwr.h\n"
    "lib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_rcc.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_rtc.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_spi.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_system.h\n"
    "lib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_tim.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_ucpd.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_usart.h\nlib/Drivers/stm32g0xx_hal_driver/Inc/stm32g0xx_ll_usb.h\n"
    "lib/Drivers/stm32g0xx_hal_driver/Release_Notes.html\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_adc.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_cec.c\n"
    "lib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_comp.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_cryp.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_dac.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_dma.c\n"
    "lib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_exti.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_fdcan.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_flash.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_flash_ex.c\n"
    "lib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_hcd.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_i2c.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_i2s.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_irda.c\n"
    "lib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_lptim.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_pcd.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_pwr_ex.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_rcc.c\n"
    "lib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_rcc_ex.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_rng.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_rtc.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_rtc_ex.c\n"
    "lib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_smartcard.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_smbus.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_spi.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_tim.c\n"
    "lib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_tim_ex.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_uart.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_uart_ex.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_hal_usart.c\n"
    "lib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_ll_adc.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_ll_rcc.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_ll_rtc.c\nlib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_ll_tim.c\n"
    "lib/Drivers/stm32g0xx_hal_driver/Src/stm32g0xx_ll_usb.c\nlib/Drivers/stm32g0xx_hal_driver/_htmresc/mini-st.css\nlib/Drivers/stm32g0xx_hal_driver/_htmresc/mini-st_2020.css\nlib/Drivers/stm32h5xx_hal_driver/Inc/Legacy/stm32_hal_legacy.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_adc.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_adc_ex.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_cec.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_cryp.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_dcmi.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_dma.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_dma_ex.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_eth.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_fdcan.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_flash.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_flash_ex.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_fmac.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_gtzc.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_i2c.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_i2s.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_i3c.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_irda.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_irda_ex.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_lptim.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_mmc.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_pcd.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_pka.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_pwr.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_rcc.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_rcc_ex.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_rtc.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_rtc_ex.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_sai.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_sd.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_smartcard.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_smbus.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_spi.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_tim.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_tim_ex.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_uart.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_usart.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_hal_xspi.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_adc.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_bus.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_comp.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_cordic.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_cortex.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_crs.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_dac.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_dcache.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_dma.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_exti.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_fmac.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_fmc.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_gpio.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_i2c.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_i3c.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_icache.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_lptim.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_lpuart.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_opamp.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_pwr.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_rcc.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_rng.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_rtc.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_sdmmc.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_spi.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_system.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_tim.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_ucpd.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_usart.h\nlib/Drivers/stm32h5xx_hal_driver/Inc/stm32h5xx_ll_usb.h\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_adc.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_adc_ex.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_cec.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_comp.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_cordic.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_cortex.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_cryp.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_cryp_ex.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_dac.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_dac_ex.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_dcache.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_dcmi.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_dma.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_dma_ex.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_dts.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_eth.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_eth_ex.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_exti.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_fdcan.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_flash.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_flash_ex.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_fmac.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_gpio.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_gtzc.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_hash.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_hcd.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_i2c.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_i2s.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_i3c.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_icache.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_irda.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_lptim.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_mmc.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_nand.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_nor.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_opamp.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_otfdec.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_pcd.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_pka.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_pssi.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_pwr.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_pwr_ex.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_ramcfg.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_rcc.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_rcc_ex.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_rng.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_rtc.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_rtc_ex.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_sai.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_sd.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_sdram.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_smartcard.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_smbus.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_spi.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_sram.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_tim.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_tim_ex.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_uart.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_uart_ex.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_usart.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_hal_xspi.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_ll_adc.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_ll_dma.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_ll_fmc.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_ll_rcc.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_ll_rtc.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_ll_sdmmc.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_ll_spi.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_ll_tim.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_ll_usb.c\nlib/Drivers/stm32h5xx_hal_driver/Src/stm32h5xx_ll_utils.c\n"
    "lib/Drivers/stm32h5xx_hal_driver/_htmresc/mini-st_2020.css\nlib/Marlin/Marlin/src/HAL/HAL_STM32_F4_F7/STM32F7/TMC2660.cpp\nlib/Marlin/Marlin/src/Marlin.cpp\nlib/Marlin/Marlin/src/core/macros.h\n"
    "lib/Marlin/Marlin/src/core/types.h\nlib/Marlin/Marlin/src/feature/I2CPositionEncoder.cpp\nlib/Marlin/Marlin/src/feature/bedlevel/ubl/ubl_G29.cpp\nlib/Marlin/Marlin/src/feature/phase_stepping/calibration.cpp\n"
    "lib/Marlin/Marlin/src/feature/phase_stepping/phase_stepping.cpp\nlib/Marlin/Marlin/src/feature/precise_stepping/precise_stepping.cpp\nlib/Marlin/Marlin/src/feature/prusa/MMU2/mmu2_mk4.cpp\nlib/Marlin/Marlin/src/feature/prusa/MMU2/protocol_logic.cpp\n"
    "lib/Marlin/Marlin/src/feature/tmc_util.cpp\nlib/Marlin/Marlin/src/gcode/calibrate/G28.cpp\nlib/Marlin/Marlin/src/gcode/calibrate/G33.cpp\nlib/Marlin/Marlin/src/gcode/calibrate/G65.cpp\n"
    "lib/Marlin/Marlin/src/gcode/calibrate/M958.cpp\nlib/Marlin/Marlin/src/gcode/gcode.cpp\nlib/Marlin/Marlin/src/gcode/gcode.h\nlib/Marlin/Marlin/src/inc/Conditionals_LCD.h\n"
    "lib/Marlin/Marlin/src/inc/Conditionals_post.h\nlib/Marlin/Marlin/src/inc/SanityCheck.h\nlib/Marlin/Marlin/src/lcd/language/language_en.h\nlib/Marlin/Marlin/src/libs/softspi.h\n"
    "lib/Marlin/Marlin/src/module/configuration_store.cpp\nlib/Marlin/Marlin/src/module/endstops.cpp\nlib/Marlin/Marlin/src/module/motion.cpp\nlib/Marlin/Marlin/src/module/planner.cpp\n"
    "lib/Marlin/Marlin/src/module/planner.h\nlib/Marlin/Marlin/src/module/probe.cpp\nlib/Marlin/Marlin/src/module/prusa/homing_corexy.cpp\nlib/Marlin/Marlin/src/module/prusa/toolchanger.cpp\n"
    "lib/Marlin/Marlin/src/module/stepper.cpp\nlib/Marlin/Marlin/src/module/stepper/trinamic.cpp\nlib/Marlin/Marlin/src/module/temperature.cpp\nlib/Marlin/Marlin/src/module/temperature.h\n"
    "lib/Marlin/Marlin/src/module/tool_change.cpp\nlib/Marlin/Marlin/src/pins/pinsDebug_list.h\nlib/Middlewares/ST/STM32_USB_Host_Library/Class/MSC/Src/usbh_msc.c\nlib/Middlewares/ST/STM32_USB_Host_Library/Class/MSC/Src/usbh_msc_bot.c\n"
    "lib/Middlewares/ST/STM32_USB_Host_Library/Core/Src/usbh_core.c\nlib/Middlewares/ST/STM32_USB_Host_Library/Core/Src/usbh_ctlreq.c\nlib/Middlewares/Third_Party/FatFs/src/ff.c\nlib/Middlewares/Third_Party/FatFs/src/ffunicode.c\n"
    "lib/Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS/cmsis_os.c\nlib/Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS/cmsis_os.h\nlib/Middlewares/Third_Party/FreeRTOS/Source/event_groups.c\nlib/Middlewares/Third_Party/FreeRTOS/Source/include/FreeRTOS.h\n"
    "lib/Middlewares/Third_Party/FreeRTOS/Source/include/croutine.h\nlib/Middlewares/Third_Party/FreeRTOS/Source/include/event_groups.h\nlib/Middlewares/Third_Party/FreeRTOS/Source/include/queue.h\nlib/Middlewares/Third_Party/FreeRTOS/Source/include/semphr.h\n"
    "lib/Middlewares/Third_Party/FreeRTOS/Source/include/stream_buffer.h\nlib/Middlewares/Third_Party/FreeRTOS/Source/include/task.h\nlib/Middlewares/Third_Party/FreeRTOS/Source/include/timers.h\nlib/Middlewares/Third_Party/FreeRTOS/Source/portable/Common/mpu_wrappers_v2.c\n"
    "lib/Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM0/port.c\nlib/Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM33_NTZ/non_secure/mpu_wrappers_v2_asm.c\nlib/Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM33_NTZ/non_secure/port.c\nlib/Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F/port.c\n"
    "lib/Middlewares/Third_Party/FreeRTOS/Source/queue.c\nlib/Middlewares/Third_Party/FreeRTOS/Source/stream_buffer.c\nlib/Middlewares/Third_Party/FreeRTOS/Source/tasks.c\nlib/Middlewares/Third_Party/FreeRTOS/Source/timers.c\n"
    "lib/Middlewares/Third_Party/LwIP/src/api/api_lib.c\nlib/Middlewares/Third_Party/LwIP/src/api/api_msg.c\nlib/Middlewares/Third_Party/LwIP/src/api/sockets.c\nlib/Middlewares/Third_Party/LwIP/src/api/tcpip.c\n"
    "lib/Middlewares/Third_Party/LwIP/src/core/altcp.c\nlib/Middlewares/Third_Party/LwIP/src/core/dns.c\nlib/Middlewares/Third_Party/LwIP/src/core/ipv4/dhcp.c\nlib/Middlewares/Third_Party/LwIP/src/core/ipv4/etharp.c\n"
    "lib/Middlewares/Third_Party/LwIP/src/core/ipv4/igmp.c\nlib/Middlewares/Third_Party/LwIP/src/core/ipv4/ip4.c\nlib/Middlewares/Third_Party/LwIP/src/core/ipv4/ip4_frag.c\nlib/Middlewares/Third_Party/LwIP/src/core/ipv6/dhcp6.c\n"
    "lib/Middlewares/Third_Party/LwIP/src/core/ipv6/ip6.c\nlib/Middlewares/Third_Party/LwIP/src/core/ipv6/ip6_frag.c\nlib/Middlewares/Third_Party/LwIP/src/core/ipv6/nd6.c\nlib/Middlewares/Third_Party/LwIP/src/core/mem.c\n"
    "lib/Middlewares/Third_Party/LwIP/src/core/netif.c\nlib/Middlewares/Third_Party/LwIP/src/core/pbuf.c\nlib/Middlewares/Third_Party/LwIP/src/core/raw.c\nlib/Middlewares/Third_Party/LwIP/src/core/tcp.c\n"
    "lib/Middlewares/Third_Party/LwIP/src/core/tcp_in.c\nlib/Middlewares/Third_Party/LwIP/src/core/tcp_out.c\nlib/Middlewares/Third_Party/LwIP/src/core/udp.c\nlib/Middlewares/Third_Party/LwIP/src/include/lwip/netif.h\n"
    "lib/Middlewares/Third_Party/LwIP/src/include/lwip/opt.h\nlib/Middlewares/Third_Party/LwIP/src/include/lwip/sockets.h\nlib/Middlewares/Third_Party/LwIP/src/include/netif/ppp/ppp.h\nlib/Middlewares/Third_Party/LwIP/src/include/netif/ppp/ppp_impl.h\n"
    "lib/Middlewares/Third_Party/LwIP/src/netif/lowpan6.c\nlib/Middlewares/Third_Party/LwIP/src/netif/lowpan6_common.c\nlib/Middlewares/Third_Party/LwIP/src/netif/ppp/auth.c\nlib/Middlewares/Third_Party/LwIP/src/netif/ppp/ccp.c\n"
    "lib/Middlewares/Third_Party/LwIP/src/netif/ppp/chap-new.c\nlib/Middlewares/Third_Party/LwIP/src/netif/ppp/chap_ms.c\nlib/Middlewares/Third_Party/LwIP/src/netif/ppp/eap.c\nlib/Middlewares/Third_Party/LwIP/src/netif/ppp/fsm.c\n"
    "lib/Middlewares/Third_Party/LwIP/src/netif/ppp/ipcp.c\nlib/Middlewares/Third_Party/LwIP/src/netif/ppp/ipv6cp.c\nlib/Middlewares/Third_Party/LwIP/src/netif/ppp/lcp.c\nlib/Middlewares/Third_Party/LwIP/src/netif/ppp/ppp.c\n"
    "lib/Middlewares/Third_Party/LwIP/src/netif/ppp/pppoe.c\nlib/Middlewares/Third_Party/LwIP/src/netif/ppp/pppol2tp.c\nlib/Middlewares/Third_Party/LwIP/src/netif/ppp/pppos.c\nlib/Middlewares/Third_Party/LwIP/src/netif/ppp/upap.c\n"
    "lib/Middlewares/Third_Party/LwIP/src/netif/ppp/utils.c\nlib/Middlewares/Third_Party/LwIP/src/netif/ppp/vj.c\nlib/Middlewares/Third_Party/littlefs/bd/lfs_emubd.c\nlib/Middlewares/Third_Party/littlefs/lfs.c\n"
    "lib/Middlewares/Third_Party/littlefs/lfs.h\nlib/Middlewares/Third_Party/littlefs/runners/bench_runner.c\nlib/Middlewares/Third_Party/littlefs/runners/test_runner.c\nlib/Middlewares/Third_Party/littlefs/scripts/bench.py\n"
    "lib/Middlewares/Third_Party/littlefs/scripts/code.py\nlib/Middlewares/Third_Party/littlefs/scripts/cov.py\nlib/Middlewares/Third_Party/littlefs/scripts/data.py\nlib/Middlewares/Third_Party/littlefs/scripts/perf.py\n"
    "lib/Middlewares/Third_Party/littlefs/scripts/perfbd.py\nlib/Middlewares/Third_Party/littlefs/scripts/plot.py\nlib/Middlewares/Third_Party/littlefs/scripts/plotmpl.py\nlib/Middlewares/Third_Party/littlefs/scripts/stack.py\n"
    "lib/Middlewares/Third_Party/littlefs/scripts/structs.py\nlib/Middlewares/Third_Party/littlefs/scripts/summary.py\nlib/Middlewares/Third_Party/littlefs/scripts/test.py\nlib/Middlewares/Third_Party/littlefs/scripts/tracebd.py\n"
    "lib/Middlewares/Third_Party/mbedtls/3rdparty/everest/library/Hacl_Curve25519.c\nlib/Middlewares/Third_Party/mbedtls/3rdparty/everest/library/legacy/Hacl_Curve25519.c\nlib/Middlewares/Third_Party/mbedtls/include/mbedtls/aes.h\nlib/Middlewares/Third_Party/mbedtls/include/mbedtls/bignum.h\n"
    "lib/Middlewares/Third_Party/mbedtls/include/mbedtls/bn_mul.h\nlib/Middlewares/Third_Party/mbedtls/include/mbedtls/check_config.h\nlib/Middlewares/Third_Party/mbedtls/include/mbedtls/cipher.h\nlib/Middlewares/Third_Party/mbedtls/include/mbedtls/compat-1.3.h\n"
    "lib/Middlewares/Third_Party/mbedtls/include/mbedtls/config.h\nlib/Middlewares/Third_Party/mbedtls/include/mbedtls/config_psa.h\nlib/Middlewares/Third_Party/mbedtls/include/mbedtls/dhm.h\nlib/Middlewares/Third_Party/mbedtls/include/mbedtls/ecp.h\n"
    "lib/Middlewares/Third_Party/mbedtls/include/mbedtls/oid.h\nlib/Middlewares/Third_Party/mbedtls/include/mbedtls/pk.h\nlib/Middlewares/Third_Party/mbedtls/include/mbedtls/rsa.h\nlib/Middlewares/Third_Party/mbedtls/include/mbedtls/ssl.h\n"
    "lib/Middlewares/Third_Party/mbedtls/include/mbedtls/ssl_internal.h\nlib/Middlewares/Third_Party/mbedtls/include/mbedtls/x509_crt.h\nlib/Middlewares/Third_Party/mbedtls/include/psa/crypto.h\nlib/Middlewares/Third_Party/mbedtls/include/psa/crypto_extra.h\n"
    "lib/Middlewares/Third_Party/mbedtls/include/psa/crypto_se_driver.h\nlib/Middlewares/Third_Party/mbedtls/include/psa/crypto_sizes.h\nlib/Middlewares/Third_Party/mbedtls/include/psa/crypto_values.h\nlib/Middlewares/Third_Party/mbedtls/library/aes.c\n"
    "lib/Middlewares/Third_Party/mbedtls/library/aria.c\nlib/Middlewares/Third_Party/mbedtls/library/bignum.c\nlib/Middlewares/Third_Party/mbedtls/library/blowfish.c\nlib/Middlewares/Third_Party/mbedtls/library/camellia.c\n"
    "lib/Middlewares/Third_Party/mbedtls/library/certs.c\nlib/Middlewares/Third_Party/mbedtls/library/cipher.c\nlib/Middlewares/Third_Party/mbedtls/library/cipher_wrap.c\nlib/Middlewares/Third_Party/mbedtls/library/cmac.c\n"
    "lib/Middlewares/Third_Party/mbedtls/library/constant_time.c\nlib/Middlewares/Third_Party/mbedtls/library/ctr_drbg.c\nlib/Middlewares/Third_Party/mbedtls/library/des.c\nlib/Middlewares/Third_Party/mbedtls/library/dhm.c\n"
    "lib/Middlewares/Third_Party/mbedtls/library/ecdh.c\nlib/Middlewares/Third_Party/mbedtls/library/ecdsa.c\nlib/Middlewares/Third_Party/mbedtls/library/ecjpake.c\nlib/Middlewares/Third_Party/mbedtls/library/ecp.c\n"
    "lib/Middlewares/Third_Party/mbedtls/library/ecp_curves.c\nlib/Middlewares/Third_Party/mbedtls/library/entropy.c\nlib/Middlewares/Third_Party/mbedtls/library/error.c\nlib/Middlewares/Third_Party/mbedtls/library/gcm.c\n"
    "lib/Middlewares/Third_Party/mbedtls/library/hmac_drbg.c\nlib/Middlewares/Third_Party/mbedtls/library/md.c\nlib/Middlewares/Third_Party/mbedtls/library/memory_buffer_alloc.c\nlib/Middlewares/Third_Party/mbedtls/library/net_sockets.c\n"
    "lib/Middlewares/Third_Party/mbedtls/library/nist_kw.c\nlib/Middlewares/Third_Party/mbedtls/library/oid.c\nlib/Middlewares/Third_Party/mbedtls/library/pk.c\nlib/Middlewares/Third_Party/mbedtls/library/pk_wrap.c\n"
    "lib/Middlewares/Third_Party/mbedtls/library/pkparse.c\nlib/Middlewares/Third_Party/mbedtls/library/psa_crypto.c\nlib/Middlewares/Third_Party/mbedtls/library/psa_crypto_driver_wrappers.c\nlib/Middlewares/Third_Party/mbedtls/library/rsa.c\n"
    "lib/Middlewares/Third_Party/mbedtls/library/sha512.c\nlib/Middlewares/Third_Party/mbedtls/library/ssl_ciphersuites.c\nlib/Middlewares/Third_Party/mbedtls/library/ssl_cli.c\nlib/Middlewares/Third_Party/mbedtls/library/ssl_msg.c\n"
    "lib/Middlewares/Third_Party/mbedtls/library/ssl_srv.c\nlib/Middlewares/Third_Party/mbedtls/library/ssl_tls.c\nlib/Middlewares/Third_Party/mbedtls/library/version_features.c\nlib/Middlewares/Third_Party/mbedtls/library/x509.c\n"
    "lib/Middlewares/Third_Party/mbedtls/library/x509_crl.c\nlib/Middlewares/Third_Party/mbedtls/library/x509_crt.c\nlib/Middlewares/Third_Party/mbedtls/programs/aes/crypt_and_hash.c\nlib/Middlewares/Third_Party/mbedtls/programs/psa/key_ladder_demo.c\n"
    "lib/Middlewares/Third_Party/mbedtls/programs/ssl/ssl_client2.c\nlib/Middlewares/Third_Party/mbedtls/programs/ssl/ssl_context_info.c\nlib/Middlewares/Third_Party/mbedtls/programs/ssl/ssl_mail_client.c\nlib/Middlewares/Third_Party/mbedtls/programs/ssl/ssl_server2.c\n"
    "lib/Middlewares/Third_Party/mbedtls/programs/test/benchmark.c\nlib/Middlewares/Third_Party/mbedtls/programs/test/query_config.c\nlib/Middlewares/Third_Party/mbedtls/programs/test/udp_proxy.c\nlib/Middlewares/Third_Party/mbedtls/programs/x509/cert_write.c\n"
    "lib/Middlewares/Third_Party/mbedtls/tests/compat.sh\nlib/Middlewares/Third_Party/mbedtls/tests/scripts/all.sh\nlib/Middlewares/Third_Party/mbedtls/tests/scripts/check_names.py\nlib/Middlewares/Third_Party/mbedtls/tests/scripts/generate_psa_tests.py\n"
    "lib/Middlewares/Third_Party/mbedtls/tests/scripts/generate_test_code.py\nlib/Middlewares/Third_Party/mbedtls/tests/scripts/test_generate_test_code.py\nlib/Middlewares/Third_Party/mbedtls/tests/src/psa_exercise_key.c\nlib/Middlewares/Third_Party/mbedtls/tests/ssl-opt.sh\n"
    "lib/Prusa-Firmware-MMU/lib/Catch2/extras/catch_amalgamated.cpp\nlib/Prusa-Firmware-MMU/lib/Catch2/extras/catch_amalgamated.hpp\nlib/Prusa-Firmware-MMU/lib/Catch2/src/catch2/catch_tostring.hpp\nlib/Prusa-Firmware-MMU/lib/Catch2/src/catch2/internal/catch_clara.hpp\n"
    "lib/Prusa-Firmware-MMU/lib/Catch2/src/catch2/internal/catch_run_context.cpp\nlib/Prusa-Firmware-MMU/lib/Catch2/src/catch2/reporters/catch_reporter_console.cpp\nlib/Prusa-Firmware-MMU/lib/Catch2/tests/SelfTest/IntrospectiveTests/CmdLine.tests.cpp\nlib/Prusa-Firmware-MMU/lib/Catch2/tests/SelfTest/UsageTests/Matchers.tests.cpp\n"
    "lib/Prusa-Firmware-MMU/lib/Catch2/tests/SelfTest/UsageTests/MatchersRanges.tests.cpp\nlib/Prusa-Firmware-MMU/lib/lufa/Bootloaders/CDC/BootloaderCDC.c\nlib/Prusa-Firmware-MMU/lib/lufa/Bootloaders/DFU/BootloaderDFU.c\nlib/Prusa-Firmware-MMU/lib/lufa/Bootloaders/HID/HostLoaderApp/hid_bootloader_cli.c\n"
    "lib/Prusa-Firmware-MMU/lib/lufa/Demos/Device/ClassDriver/RNDISEthernet/Lib/TCP.c\nlib/Prusa-Firmware-MMU/lib/lufa/Demos/Device/LowLevel/CCID/CCID.c\nlib/Prusa-Firmware-MMU/lib/lufa/Demos/Device/LowLevel/RNDISEthernet/Lib/TCP.c\nlib/Prusa-Firmware-MMU/lib/lufa/Demos/Host/LowLevel/MassStorageHost/Lib/MassStoreCommands.c\n"
    "lib/Prusa-Firmware-MMU/lib/lufa/LUFA/Drivers/USB/Class/Common/AudioClassCommon.h\nlib/Prusa-Firmware-MMU/lib/lufa/LUFA/Drivers/USB/Class/Common/HIDClassCommon.h\nlib/Prusa-Firmware-MMU/lib/lufa/LUFA/Drivers/USB/Core/AVR8/EndpointStream_AVR8.h\nlib/Prusa-Firmware-MMU/lib/lufa/LUFA/Drivers/USB/Core/AVR8/Endpoint_AVR8.h\n"
    "lib/Prusa-Firmware-MMU/lib/lufa/LUFA/Drivers/USB/Core/AVR8/Pipe_AVR8.h\nlib/Prusa-Firmware-MMU/lib/lufa/LUFA/Drivers/USB/Core/StdDescriptors.h\nlib/Prusa-Firmware-MMU/lib/lufa/LUFA/Drivers/USB/Core/UC3/Endpoint_UC3.h\nlib/Prusa-Firmware-MMU/lib/lufa/LUFA/Drivers/USB/Core/UC3/Pipe_UC3.h\n"
    "lib/Prusa-Firmware-MMU/lib/lufa/LUFA/Drivers/USB/Core/XMEGA/EndpointStream_XMEGA.h\nlib/Prusa-Firmware-MMU/lib/lufa/LUFA/Drivers/USB/Core/XMEGA/Endpoint_XMEGA.h\nlib/Prusa-Firmware-MMU/lib/lufa/Projects/TempDataLogger/Lib/FATFs/ff.c\nlib/Prusa-Firmware-MMU/lib/lufa/Projects/Webserver/Lib/FATFs/ff.c\n"
    "lib/Prusa-Firmware-MMU/lib/lufa/Projects/Webserver/Lib/uip/uip.c\nlib/Prusa-Firmware-MMU/lib/lufa/Projects/Webserver/Lib/uip/uip.h\nlib/Prusa-Firmware-MMU/lib/lufa/Projects/Webserver/Lib/uip/uipopt.h\nlib/Prusa-Firmware-MMU/tests/unit/modules/protocol/test_protocol.cpp\n"
    "lib/Prusa-Firmware-MMU/utils/gcovr.py\nlib/QR/qrcodegen.c\nlib/SG14/inplace_vector.hpp\nlib/Segger/SEGGER_RTT.c\n"
    "lib/Segger/SEGGER_SYSVIEW.c\nlib/TMCStepper/src/TMCStepper.h\nlib/WUI/mdns/mdns.c\nlib/WUI/mdns/mdns_out.c\n"
    "lib/WUI/sntp/sntp.c\nlib/esp32-nic/main/uart_nic.c\nlib/esp8266-nic/main/uart_nic.c\nlib/heatshrink/greatest.h\n"
    "lib/heatshrink/test_heatshrink_dynamic.c\nlib/heatshrink/test_heatshrink_dynamic_theft.c\nlib/libbgcode/src/LibBGCode/binarize/binarize.cpp\nlib/libbgcode/src/LibBGCode/convert/convert.cpp\n"
    "lib/liblightmodbus/test/test_main.cpp\nlib/liblightmodbus/test/tester.cpp\nlib/magic_enum/include/magic_enum/magic_enum.hpp\nlib/magic_enum/include/magic_enum/magic_enum_containers.hpp\n"
    "lib/magic_enum/test/3rdparty/Catch2/include/catch2/catch.hpp\nlib/magic_enum/test/test.cpp\nlib/magic_enum/test/test_flags.cpp\nlib/printf/printf.c\n"
    "lib/printf/test/catch.hpp\nlib/printf/test/test_suite.cpp\nlib/sfl-library/benchmark/nanobench.h\nlib/sfl-library/include/sfl/compact_vector.hpp\n"
    "lib/sfl-library/include/sfl/detail/rb_tree.hpp\nlib/sfl-library/include/sfl/detail/uninitialized_memory_algorithms.hpp\nlib/sfl-library/include/sfl/devector.hpp\nlib/sfl-library/include/sfl/map.hpp\n"
    "lib/sfl-library/include/sfl/multimap.hpp\nlib/sfl-library/include/sfl/multiset.hpp\nlib/sfl-library/include/sfl/segmented_devector.hpp\nlib/sfl-library/include/sfl/segmented_vector.hpp\n"
    "lib/sfl-library/include/sfl/set.hpp\nlib/sfl-library/include/sfl/small_flat_map.hpp\nlib/sfl-library/include/sfl/small_flat_multimap.hpp\nlib/sfl-library/include/sfl/small_flat_multiset.hpp\n"
    "lib/sfl-library/include/sfl/small_flat_set.hpp\nlib/sfl-library/include/sfl/small_map.hpp\nlib/sfl-library/include/sfl/small_multimap.hpp\nlib/sfl-library/include/sfl/small_multiset.hpp\n"
    "lib/sfl-library/include/sfl/small_set.hpp\nlib/sfl-library/include/sfl/small_unordered_flat_map.hpp\nlib/sfl-library/include/sfl/small_unordered_flat_multimap.hpp\nlib/sfl-library/include/sfl/small_unordered_flat_multiset.hpp\n"
    "lib/sfl-library/include/sfl/small_unordered_flat_set.hpp\nlib/sfl-library/include/sfl/small_vector.hpp\nlib/sfl-library/include/sfl/static_flat_map.hpp\nlib/sfl-library/include/sfl/static_flat_multimap.hpp\n"
    "lib/sfl-library/include/sfl/static_flat_multiset.hpp\nlib/sfl-library/include/sfl/static_flat_set.hpp\nlib/sfl-library/include/sfl/static_map.hpp\nlib/sfl-library/include/sfl/static_multimap.hpp\n"
    "lib/sfl-library/include/sfl/static_multiset.hpp\nlib/sfl-library/include/sfl/static_set.hpp\nlib/sfl-library/include/sfl/static_unordered_flat_map.hpp\nlib/sfl-library/include/sfl/static_unordered_flat_multimap.hpp\n"
    "lib/sfl-library/include/sfl/static_unordered_flat_multiset.hpp\nlib/sfl-library/include/sfl/static_unordered_flat_set.hpp\nlib/sfl-library/include/sfl/static_vector.hpp\nlib/sfl-library/include/sfl/vector.hpp\n"
    "lib/sfl-library/test/static_flat_map.cpp\nlib/sfl-library/test/static_flat_multimap.cpp\nlib/sfl-library/test/static_flat_multiset.cpp\nlib/sfl-library/test/static_flat_set.cpp\n"
    "lib/sfl-library/test/static_map.cpp\nlib/sfl-library/test/static_multimap.cpp\nlib/sfl-library/test/static_multiset.cpp\nlib/sfl-library/test/static_set.cpp\n"
    "lib/sfl-library/test/static_unordered_flat_map.cpp\nlib/sfl-library/test/static_unordered_flat_multimap.cpp\nlib/sfl-library/test/static_unordered_flat_multiset.cpp\nlib/sfl-library/test/static_unordered_flat_set.cpp\n"
    "lib/sfl-library/test/static_vector.cpp\nlib/tinyusb/examples/device/video_capture/src/images.h\nlib/tinyusb/examples/host/msc_file_explorer/src/msc_app.c\nlib/tinyusb/hw/bsp/ch32v307/system_ch32v30x.c\n"
    "lib/tinyusb/hw/bsp/fomu/include/csr.h\nlib/tinyusb/hw/bsp/gd32vf103/system_gd32vf103.c\nlib/tinyusb/hw/bsp/same70_qmtech/hpl_pmc_config.h\nlib/tinyusb/hw/bsp/same70_qmtech/hpl_xdmac_config.h\n"
    "lib/tinyusb/hw/bsp/same70_xplained/hpl_pmc_config.h\nlib/tinyusb/hw/bsp/same70_xplained/hpl_xdmac_config.h\nlib/tinyusb/hw/bsp/sltb009a/sltb009a.c\nlib/tinyusb/hw/mcu/dialog/da1469x/SDK_10.0.8.105/sdk/bsp/include/DA1469xAB.h\n"
    "lib/tinyusb/hw/mcu/dialog/da1469x/SDK_10.0.8.105/sdk/bsp/include/cmsis_gcc.h\nlib/tinyusb/hw/mcu/dialog/da1469x/SDK_10.0.8.105/sdk/bsp/include/core_cm0.h\nlib/tinyusb/hw/mcu/dialog/da1469x/SDK_10.0.8.105/sdk/bsp/include/core_cm33.h\nlib/tinyusb/hw/mcu/nordic/nrf5x/s140_nrf52_6.1.1_API/include/ble.h\n"
    "lib/tinyusb/hw/mcu/nordic/nrf5x/s140_nrf52_6.1.1_API/include/ble_gap.h\nlib/tinyusb/hw/mcu/nordic/nrf5x/s140_nrf52_6.1.1_API/include/ble_gattc.h\nlib/tinyusb/hw/mcu/nordic/nrf5x/s140_nrf52_6.1.1_API/include/ble_gatts.h\nlib/tinyusb/hw/mcu/nordic/nrf5x/s140_nrf52_6.1.1_API/include/nrf_soc.h\n"
    "lib/tinyusb/lib/SEGGER_RTT/RTT/SEGGER_RTT.c\nlib/tinyusb/lib/embedded-cli/embedded_cli.h\nlib/tinyusb/lib/fatfs/source/ff.c\nlib/tinyusb/lib/fatfs/source/ffunicode.c\n"
    "lib/tinyusb/src/class/audio/audio.h\nlib/tinyusb/src/class/audio/audio_device.c\nlib/tinyusb/src/class/audio/audio_device.h\nlib/tinyusb/src/class/cdc/cdc_host.c\n"
    "lib/tinyusb/src/class/hid/hid.h\nlib/tinyusb/src/class/hid/hid_host.c\nlib/tinyusb/src/class/msc/msc_device.c\nlib/tinyusb/src/class/usbtmc/usbtmc_device.c\n"
    "lib/tinyusb/src/class/video/video_device.c\nlib/tinyusb/src/common/tusb_fifo.c\nlib/tinyusb/src/device/usbd.c\nlib/tinyusb/src/device/usbd.h\n"
    "lib/tinyusb/src/host/usbh.c\nlib/tinyusb/src/portable/analog/max3421/hcd_max3421.c\nlib/tinyusb/src/portable/bridgetek/ft9xx/dcd_ft9xx.c\nlib/tinyusb/src/portable/chipidea/ci_hs/dcd_ci_hs.c\n"
    "lib/tinyusb/src/portable/dialog/da146xx/dcd_da146xx.c\nlib/tinyusb/src/portable/ehci/ehci.c\nlib/tinyusb/src/portable/espressif/esp32sx/dcd_esp32sx.c\nlib/tinyusb/src/portable/mentor/musb/dcd_musb.c\n"
    "lib/tinyusb/src/portable/mentor/musb/hcd_musb.c\nlib/tinyusb/src/portable/mentor/musb/musb_type.h\nlib/tinyusb/src/portable/microchip/pic/dcd_pic.c\nlib/tinyusb/src/portable/microchip/pic32mz/dcd_pic32mz.c\n"
    "lib/tinyusb/src/portable/microchip/pic32mz/usbhs_registers.h\nlib/tinyusb/src/portable/microchip/samx7x/common_usb_regs.h\nlib/tinyusb/src/portable/microchip/samx7x/dcd_samx7x.c\nlib/tinyusb/src/portable/nordic/nrf5x/dcd_nrf5x.c\n"
    "lib/tinyusb/src/portable/nuvoton/nuc505/dcd_nuc505.c\nlib/tinyusb/src/portable/nxp/khci/hcd_khci.c\nlib/tinyusb/src/portable/ohci/ohci.c\nlib/tinyusb/src/portable/raspberrypi/rp2040/hcd_rp2040.c\n"
    "lib/tinyusb/src/portable/renesas/rusb2/dcd_rusb2.c\nlib/tinyusb/src/portable/renesas/rusb2/hcd_rusb2.c\nlib/tinyusb/src/portable/renesas/rusb2/rusb2_type.h\nlib/tinyusb/src/portable/st/stm32_fsdev/dcd_stm32_fsdev.c\n"
    "lib/tinyusb/src/portable/st/synopsys/dcd_synopsys.c\nlib/tinyusb/src/portable/st/synopsys/synopsys_common.h\nlib/tinyusb/src/portable/sunxi/dcd_sunxi_musb.c\nlib/tinyusb/src/portable/sunxi/musb_def.h\n"
    "lib/tinyusb/src/portable/synopsys/dwc2/dcd_dwc2.c\nlib/tinyusb/src/portable/synopsys/dwc2/dwc2_type.h\nlib/tinyusb/src/portable/ti/msp430x5xx/dcd_msp430x5xx.c\nlib/tinyusb/src/portable/valentyusb/eptri/dcd_eptri.c\n"
    "src/common/hwio_pindef.h\nsrc/common/marlin_server_types/client_response.hpp\nsrc/device/stm32f4/cmsis.cpp\nsrc/device/stm32f4/cmsis_boot.cpp\n"
    "src/gui/res/cc/font_bold_11x19_full.hpp\nsrc/gui/res/cc/font_bold_13x22_full.hpp\nsrc/gui/res/cc/font_bold_30x53_digits.hpp\nsrc/gui/res/cc/font_regular_11x18_full.hpp\n"
    "src/gui/res/cc/font_regular_11x18_latin.hpp\nsrc/gui/res/cc/font_regular_11x18_latin_and_cyrillic.hpp\nsrc/gui/res/cc/font_regular_11x18_latin_and_katakana.hpp\nsrc/gui/res/cc/font_regular_11x18_standard.hpp\n"
    "src/gui/res/cc/font_regular_7x13_full.hpp\nsrc/gui/res/cc/font_regular_7x13_latin.hpp\nsrc/gui/res/cc/font_regular_7x13_latin_and_cyrillic.hpp\nsrc/gui/res/cc/font_regular_7x13_latin_and_katakana.hpp\n"
    "src/gui/res/cc/font_regular_7x13_standard.hpp\nsrc/gui/res/cc/font_regular_9x16_full.hpp\nsrc/gui/res/cc/font_regular_9x16_latin.hpp\nsrc/gui/res/cc/font_regular_9x16_latin_and_cyrillic.hpp\n"
    "src/gui/res/cc/font_regular_9x16_latin_and_katakana.hpp\nsrc/gui/res/cc/font_regular_9x16_standard.hpp\nsrc/persistent_stores/store_instances/config_store/store_definition.hpp\ntests/stubs/FreeRTOS/Source/event_groups.c\n"
    "tests/stubs/FreeRTOS/Source/include/FreeRTOS.h\ntests/stubs/FreeRTOS/Source/include/croutine.h\ntests/stubs/FreeRTOS/Source/include/event_groups.h\ntests/stubs/FreeRTOS/Source/include/message_buffer.h\n"
    "tests/stubs/FreeRTOS/Source/include/queue.h\ntests/stubs/FreeRTOS/Source/include/semphr.h\ntests/stubs/FreeRTOS/Source/include/stream_buffer.h\ntests/stubs/FreeRTOS/Source/include/task.h\n"
    "tests/stubs/FreeRTOS/Source/include/timers.h\ntests/stubs/FreeRTOS/Source/queue.c\ntests/stubs/FreeRTOS/Source/stream_buffer.c\ntests/stubs/FreeRTOS/Source/tasks.c\n"
    "tests/stubs/FreeRTOS/Source/timers.c\ntests/stubs/inc/macros.h\n")

ORIGINAL_TEMPORARY_PATHS = _path_set(
    "lib/WUI/espif.cpp\nlib/WUI/nhttp/server.cpp\nlib/WUI/wui.cpp\nrust/crates/domain/src/auxiliary.rs\n"
    "rust/crates/domain/src/feature.rs\nrust/crates/domain/src/gui.rs\nrust/crates/domain/src/network.rs\nsrc/buddy/filesystem_fatfs.cpp\n"
    "src/buddy/main.cpp\nsrc/common/gcode/gcode_info.cpp\nsrc/common/gcode/gcode_reader_binary.cpp\nsrc/common/marlin_print_preview.cpp\n"
    "src/common/marlin_server.cpp\nsrc/common/media_prefetch/media_prefetch.cpp\nsrc/common/power_panic.cpp\nsrc/common/probe_analysis.cpp\n"
    "src/connect/connect.cpp\nsrc/connect/marlin_printer.cpp\nsrc/connect/planner.cpp\nsrc/connect/render.cpp\n"
    "src/device/stm32f4/hal_msp.cpp\nsrc/device/stm32f4/peripherals.cpp\nsrc/gui/MItem_tools.cpp\nsrc/gui/MItem_tools.hpp\n"
    "src/gui/screen_printing.cpp\nsrc/gui/screen_tools_mapping.cpp\nsrc/guiapi/include/Rect16.h\nsrc/guiapi/src/ili9488.cpp\n"
    "src/guiapi/src/st7789v.cpp\nsrc/marlin_stubs/G425.cpp\nsrc/marlin_stubs/pause/pause.cpp\nsrc/persistent_stores/journal/backend.cpp\n"
    "src/persistent_stores/store_instances/config_store/store_definition.cpp\nsrc/puppies/Dwarf.cpp\nsrc/puppy/shared/modbus/ModbusProtocol.cpp\nsrc/puppy/xbuddy_extension/hal.cpp\n"
    "src/state/printer_state.cpp\nsrc/transfers/transfer.cpp\ntests/unit/common/gcode/reader/gcode_reader.cpp\ntests/unit/gui/rectangle_tests.cpp\n"
    "tests/unit/gui/window/tests_layout.cpp\ntests/unit/lib/Marlin/MMU2/mmu2_protocol_logic_test.cpp\ntests/unit/lib/WUI/nhttp/server_tests.cpp\ntests/unit/media_prefetch/media_prefetch_tests.cpp\n"
    "tests/unit/persistent_stores/EEPROM_journal_test.cpp\ntools/bazel/phase10_verify.py\ntools/bazel/phase10_verify_test.py\ntools/bazel/phase11_verify.py\n"
    "tools/bazel/phase11_verify_test.py\ntools/bazel/phase13_ci_evidence.py\ntools/bazel/phase14_simulator_evidence.py\ntools/bazel/phase15_hardware_evidence.py\n"
    "tools/bazel/phase15_hardware_evidence_test.py\ntools/bazel/phase16_live_network_evidence.py\ntools/bazel/phase16_live_network_evidence_test.py\ntools/bazel/phase17_release_candidate_evidence.py\n"
    "tools/bazel/phase17_release_candidate_evidence_test.py\ntools/bazel/phase18_cutover_review.py\ntools/bazel/phase18_cutover_review_test.py\ntools/bazel/phase19_aggregate_ci_evidence.py\n"
    "tools/bazel/phase20_release_candidate_artifacts.py\ntools/bazel/phase20_release_candidate_artifacts_test.py\ntools/bazel/phase22_metadata_reconciliation.py\ntools/bazel/phase23_simulator_evidence_execution.py\n"
    "tools/bazel/phase24_hardware_media_safety_evidence_execution.py\ntools/bazel/phase24_hardware_media_safety_evidence_execution_test.py\ntools/bazel/phase25_live_service_evidence_execution.py\ntools/bazel/phase26_release_signing_upstream_evidence.py\n"
    "tools/bazel/phase26_release_signing_upstream_evidence_test.py\ntools/bazel/phase27_retained_code_acceptance_decisions.py\ntools/bazel/phase27_retained_code_acceptance_decisions_test.py\ntools/bazel/phase28_final_readiness_packet.py\n"
    "tools/bazel/phase28_final_readiness_packet_test.py\ntools/bazel/phase31_final_evidence_intake.py\ntools/bazel/phase31_final_evidence_intake_test.py\ntools/bazel/phase32_blocker_register_triage.py\n"
    "tools/bazel/phase32_blocker_register_triage_test.py\ntools/bazel/phase33_maintainer_decision_inputs.py\ntools/bazel/phase33_maintainer_decision_inputs_test.py\ntools/bazel/phase34_final_readiness_demotion_dry_run.py\n"
    "tools/bazel/phase34_final_readiness_demotion_dry_run_test.py\ntools/bazel/phase35_cutover_decision_artifact.py\ntools/bazel/phase35_cutover_decision_artifact_test.py\ntools/bazel/phase38_cutover_workflow.py\n"
    "tools/bazel/phase38_cutover_workflow_test.py\ntools/bazel/phase5_verify.py\ntools/bazel/phase6_verify.py\ntools/bazel/phase7_verify.py\n"
    "tools/bazel/phase7_verify_test.py\ntools/bazel/phase8_verify.py\ntools/bazel/phase8_verify_test.py\ntools/bazel/phase9_verify.py\n"
    "tools/bazel/phase9_verify_test.py\nutils/build.py\nutils/phase_stepping/phase_stepping.py\n"
)

LOCKED_OWNED_PATHS = frozenset({
    "src/connect/planner.cpp",
    "src/gui/screen_tools_mapping.cpp",
    "src/guiapi/include/Rect16.h",
})


def _normalize_path(candidate_path: str, line_number: int) -> str:
    if (not candidate_path or "\\" in candidate_path
            or PurePosixPath(candidate_path).is_absolute()
            or candidate_path in {".", ".."}
            or candidate_path.startswith("../")
            or posixpath.normpath(candidate_path) != candidate_path):
        raise PolicyError(
            f"line {line_number}: path must be normalized and repo-relative: "
            f"{candidate_path or '<empty>'}")
    return candidate_path


def _reason_kind(reason: str, line_number: int) -> ReasonKind:
    if TEMPORARY_REASON_PATTERN.fullmatch(reason):
        return ReasonKind.TEMPORARY
    if reason.startswith(
            OWNED_REASON_PREFIX) and reason != OWNED_REASON_PREFIX:
        return ReasonKind.OWNED
    for prefix, kind in PERMANENT_REASON_PREFIXES.items():
        if reason.startswith(prefix) and reason != prefix:
            return ReasonKind(kind)
    raise PolicyError(f"line {line_number}: unapproved reason: {reason}")


def parse_ledger(
    contents: str,
    *,
    source: str = ".bright-builds-rules-checks.tsv",
) -> tuple[LedgerEntry, ...]:
    if not contents:
        raise PolicyError(f"{source}: ledger must not be empty")

    entries: list[LedgerEntry] = []
    seen_paths: set[str] = set()
    maybe_previous_path: str | None = None
    for line_number, line in enumerate(contents.splitlines(), start=1):
        fields = line.split("\t")
        if len(fields) != 3:
            raise PolicyError(
                f"{source}:{line_number}: row must contain exactly three tab-separated fields"
            )
        check_id, raw_path, reason = fields
        if check_id != CHECK_ID:
            raise PolicyError(
                f"{source}:{line_number}: unsupported check ID: {check_id or '<empty>'}"
            )
        relative_path = _normalize_path(raw_path, line_number)
        if reason != reason.strip() or not reason:
            raise PolicyError(
                f"{source}:{line_number}: reason must be non-empty and trimmed"
            )
        _reason_kind(reason, line_number)
        if relative_path in seen_paths:
            raise PolicyError(
                f"{source}:{line_number}: duplicate path: {relative_path}")
        if maybe_previous_path is not None and maybe_previous_path >= relative_path:
            raise PolicyError(
                f"{source}:{line_number}: paths must be unique and sorted")
        seen_paths.add(relative_path)
        maybe_previous_path = relative_path
        entries.append(LedgerEntry(check_id, relative_path, reason))

    return tuple(entries)


def _paths_for_kind(
    entries: tuple[LedgerEntry, ...],
    *kinds: ReasonKind,
) -> frozenset[str]:
    accepted = set(kinds)
    return frozenset(entry.path
                     for line_number, entry in enumerate(entries, start=1)
                     if _reason_kind(entry.reason, line_number) in accepted)


def _set_delta(expected: frozenset[str], actual: frozenset[str]) -> str:
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    details = []
    if missing:
        details.append(f"missing={missing[:3]}")
    if unexpected:
        details.append(f"unexpected={unexpected[:3]}")
    return "; ".join(details) or "sets differ"


def validate_policy(
    entries: tuple[LedgerEntry, ...],
    *,
    terminal: bool = False,
) -> PolicySummary:
    entry_by_path = {entry.path: entry for entry in entries}
    active_paths = frozenset(entry_by_path)
    provenance_paths = _paths_for_kind(
        entries,
        ReasonKind.IMPORTED,
        ReasonKind.GENERATED,
        ReasonKind.DECLARATIVE,
    )
    temporary_paths = _paths_for_kind(entries, ReasonKind.TEMPORARY)
    owned_paths = _paths_for_kind(entries, ReasonKind.OWNED)

    reclassified_frozen = frozenset(relative_path
                                    for relative_path in FROZEN_PERMANENT_PATHS
                                    & active_paths
                                    if relative_path not in provenance_paths)
    if reclassified_frozen:
        raise PolicyError("frozen permanent paths were reclassified: "
                          f"{sorted(reclassified_frozen)[:3]}")
    if provenance_paths != FROZEN_PERMANENT_PATHS:
        raise PolicyError(
            "frozen permanent set changed: "
            f"{_set_delta(FROZEN_PERMANENT_PATHS, provenance_paths)}")

    unexpected_temporary = temporary_paths - ORIGINAL_TEMPORARY_PATHS
    if unexpected_temporary:
        raise PolicyError(f"temporary set grew outside the original 95 paths: "
                          f"{sorted(unexpected_temporary)[:3]}")
    unexpected_owned = owned_paths - LOCKED_OWNED_PATHS
    if unexpected_owned:
        raise PolicyError(
            f"unauthorized owned permanence: {sorted(unexpected_owned)[:3]}")

    allowed_paths = FROZEN_PERMANENT_PATHS | temporary_paths | owned_paths
    unexpected_active = active_paths - allowed_paths
    if unexpected_active:
        raise PolicyError(
            f"unauthorized active paths: {sorted(unexpected_active)[:3]}")

    if terminal:
        expected_terminal = FROZEN_PERMANENT_PATHS | LOCKED_OWNED_PATHS
        if temporary_paths:
            raise PolicyError(
                f"terminal mode requires zero temporary paths; found {len(temporary_paths)}"
            )
        if owned_paths != LOCKED_OWNED_PATHS or active_paths != expected_terminal:
            raise PolicyError("terminal exact set mismatch: "
                              f"{_set_delta(expected_terminal, active_paths)}")

    permanent_count = len(provenance_paths | owned_paths)
    return PolicySummary(
        permanent_count=permanent_count,
        temporary_count=len(temporary_paths),
        owned_permanent_count=len(owned_paths),
        total_count=len(entries),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=
        "Validate the shrink-only Phase 40 file-length exception policy.")
    parser.add_argument(
        "--ledger",
        type=Path,
        default=DEFAULT_LEDGER_PATH,
        help="active exception ledger (default: repository ledger)",
    )
    parser.add_argument(
        "--terminal",
        action="store_true",
        help="require the exact 841-path terminal permanent set",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        contents = args.ledger.read_text(encoding="utf-8")
        entries = parse_ledger(contents, source=args.ledger.as_posix())
        summary = validate_policy(entries, terminal=args.terminal)
    except (OSError, PolicyError) as error:
        print(f"FAIL phase40 file-length policy: {error}", file=sys.stderr)
        return 1

    mode = "terminal" if args.terminal else "shrink-only"
    print("PASS phase40 file-length policy "
          f"mode={mode} permanent={summary.permanent_count} "
          f"temporary={summary.temporary_count} "
          f"owned_permanent={summary.owned_permanent_count} "
          f"total={summary.total_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
