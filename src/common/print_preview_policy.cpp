#include "marlin_print_preview.hpp"

#include "filament.hpp"
#include "filament_sensors_handler.hpp"
#include "mmu2_toolchanger_common.hpp"
#include "selftest_result_evaluation.hpp"
#include "timing.h"
#include "tools_mapping.hpp"

#include <common/gcode/gcode_info_scan.hpp>
#include <config_store/store_instance.hpp>
#include <module/prusa/spool_join.hpp>
#include <module/prusa/tool_mapper.hpp>
#include <option/has_mmu2.h>
#include <option/has_toolchanger.h>

std::optional<PhasesPrintPreview> IPrintPreview::getCorrespondingPhase(IPrintPreview::State state) {
    switch (state) {
    case State::inactive:
        return std::nullopt;
    case State::init:
    case State::loading:
        return PhasesPrintPreview::loading;
    case State::download_wait:
        return PhasesPrintPreview::download_wait;
    case State::preview_wait_user:
        return PhasesPrintPreview::main_dialog;
    case State::unfinished_selftest_wait_user:
        return PhasesPrintPreview::unfinished_selftest;
    case State::new_firmware_available_wait_user:
        return PhasesPrintPreview::new_firmware_available;
#if HAS_TOOLCHANGER() || HAS_MMU2()
    case State::tools_mapping_wait_user:
        return PhasesPrintPreview::tools_mapping;
#endif
    case State::wrong_printer_wait_user:
        return PhasesPrintPreview::wrong_printer;
    case State::wrong_printer_wait_user_abort:
        return PhasesPrintPreview::wrong_printer_abort;
    case State::filament_not_inserted_wait_user:
    case State::filament_not_inserted_load:
        return PhasesPrintPreview::filament_not_inserted;
#if HAS_MMU2()
    case State::mmu_filament_inserted_wait_user:
    case State::mmu_filament_inserted_unload:
        return PhasesPrintPreview::mmu_filament_inserted;
#endif
    case State::wrong_filament_wait_user:
    case State::wrong_filament_change:
        return PhasesPrintPreview::wrong_filament;
    case State::file_error_wait_user:
        return PhasesPrintPreview::file_error;
    case State::checks_done:
    case State::done:
        return std::nullopt;
    }
    return std::nullopt;
}

#if ENABLED(PRUSA_SPOOL_JOIN) && ENABLED(PRUSA_TOOL_MAPPING)

bool PrintPreview::ToolsMappingValidty::all_ok() const {
    return unassigned_gcodes.count() == 0
#if not HAS_MMU2()
        && mismatched_filaments.count() == 0
#endif
        && mismatched_nozzles.count() == 0 && unloaded_tools.count() == 0;
}

auto PrintPreview::check_tools_mapping_validity(const ToolMapper &mapper, const SpoolJoin &joiner, const GCodeInfo &gcode) -> ToolsMappingValidty {
    ToolsMappingValidty result;

    for (int gcode_tool = 0; gcode_tool < gcode.GivenExtrudersCount(); ++gcode_tool) {
        if (!gcode.get_extruder_info(gcode_tool).used()) {
            continue;
        }
        if (mapper.to_physical(gcode_tool) == ToolMapper::NO_TOOL_MAPPED) {
            result.unassigned_gcodes.set(gcode_tool);
        }
    }

    auto get_nozzle_diameter = [&]([[maybe_unused]] size_t idx) {
#if HAS_TOOLCHANGER()
        return config_store().get_nozzle_diameter(idx);
#elif HAS_MMU2()
        return config_store().get_nozzle_diameter(0);
#endif
    };

    auto nozzles_match = [&](uint8_t physical_extruder) {
        const auto gcode_tool = tools_mapping::to_gcode_tool_custom(mapper, joiner, physical_extruder);
        if (gcode_tool == tools_mapping::no_tool
            || !gcode.get_extruder_info(gcode_tool).used()
            || !gcode.get_extruder_info(gcode_tool).nozzle_diameter.has_value()) {
            return true;
        }

        const float distance = std::abs(
            static_cast<float>(gcode.get_extruder_info(gcode_tool).nozzle_diameter.value())
            - static_cast<float>(get_nozzle_diameter(physical_extruder)));
        return distance <= 0.001f;
    };

    auto tool_needs_to_be_loaded = [&]([[maybe_unused]] uint8_t physical_extruder) {
#if HAS_TOOLCHANGER()
        if (!config_store().fsensor_enabled.get()) {
            return false;
        }
        return check_extruder_need_filament_load(physical_extruder, ToolMapper::NO_TOOL_MAPPED, [&](uint8_t physical) {
            return tools_mapping::to_gcode_tool_custom(mapper, joiner, physical);
        });
#elif HAS_MMU2()
        return false;
#endif
    };

    auto tool_has_correct_filament_type = [&](uint8_t physical_extruder) {
        return check_correct_filament_type(physical_extruder, ToolMapper::NO_TOOL_MAPPED, [&](uint8_t physical) {
            return tools_mapping::to_gcode_tool_custom(mapper, joiner, physical);
        });
    };

    for (size_t physical = 0; physical < EXTRUDERS; ++physical) {
        if (!is_tool_enabled(physical)) {
            continue;
        }
        if (tool_needs_to_be_loaded(physical)) {
            result.unloaded_tools.set(physical);
        }
        if (!nozzles_match(physical)) {
            result.mismatched_nozzles.set(physical);
        }
        if (!tool_has_correct_filament_type(physical)) {
            result.mismatched_filaments.set(physical);
        }
    }

    return result;
}

#endif

bool PrintPreview::check_extruder_need_filament_load(
    uint8_t physical_extruder,
    uint8_t no_gcode_value,
    stdext::inplace_function<uint8_t(uint8_t)> gcode_extruder_getter) {
    const auto gcode_extruder = gcode_extruder_getter(physical_extruder);
    if (gcode_extruder == no_gcode_value) {
        return false;
    }
    if (!GCodeInfo::getInstance().get_extruder_info(gcode_extruder).used()) {
        return false;
    }
    return !FSensors_instance().ToolHasFilament(physical_extruder);
}

bool PrintPreview::check_correct_filament_type(
    uint8_t physical_extruder,
    uint8_t no_gcode_value,
    stdext::inplace_function<uint8_t(uint8_t)> gcode_extruder_getter) {
    const auto gcode_extruder = gcode_extruder_getter(physical_extruder);
    if (gcode_extruder == no_gcode_value) {
        return true;
    }

    const auto &extruder_info = GCodeInfo::getInstance().get_extruder_info(gcode_extruder);
    if (!extruder_info.used() || !extruder_info.filament_name.has_value()) {
        return true;
    }

    const auto loaded_filament_params = config_store().get_filament_type(physical_extruder).parameters();
    return strcmp(extruder_info.filament_name->data(), "---") == 0
        || strcmp(extruder_info.filament_name->data(), loaded_filament_params.name.data()) == 0;
}

PrintPreview::Result PrintPreview::stateToResult() const {
    switch (GetState()) {
    case State::init:
    case State::download_wait:
    case State::loading:
        return Result::Wait;
    case State::preview_wait_user:
        return Result::Image;
    case State::unfinished_selftest_wait_user:
    case State::new_firmware_available_wait_user:
    case State::wrong_printer_wait_user:
    case State::wrong_printer_wait_user_abort:
    case State::wrong_filament_change:
    case State::wrong_filament_wait_user:
    case State::filament_not_inserted_load:
    case State::filament_not_inserted_wait_user:
#if HAS_MMU2()
    case State::mmu_filament_inserted_unload:
    case State::mmu_filament_inserted_wait_user:
#endif
    case State::checks_done:
    case State::file_error_wait_user:
        return Result::Questions;
    case State::inactive:
    case State::done:
        return Result::Inactive;
#if HAS_MMU2() || HAS_TOOLCHANGER()
    case State::tools_mapping_wait_user:
        return Result::ToolsMapping;
#endif
    }
    return Result::Inactive;
}

void PrintPreview::Init() {
    ChangeState(State::init);
}

IPrintPreview::State PrintPreview::stateFromSelftestCheck() {
#if HAS_SELFTEST()
    if (!is_selftest_successfully_completed()) {
        return State::unfinished_selftest_wait_user;
    }
#endif
    return stateFromUpdateCheck();
}

IPrintPreview::State PrintPreview::stateFromUpdateCheck() {
    if (GCodeInfo::getInstance().get_valid_printer_settings().outdated_firmware.is_valid()) {
        return stateFromPrinterCheck();
    }
    new_firmware_open_ms = ticks_ms();
    return State::new_firmware_available_wait_user;
}

IPrintPreview::State PrintPreview::stateFromPrinterCheck() {
    GCodeInfo::getInstance().EvaluateToolsValid();
    if (GCodeInfo::getInstance().get_valid_printer_settings().is_valid(tools_mapping::is_tool_mapping_possible())) {
        return stateFromFilamentPresence();
    }
    return GCodeInfo::getInstance().get_valid_printer_settings().is_fatal(tools_mapping::is_tool_mapping_possible())
        ? State::wrong_printer_wait_user_abort
        : State::wrong_printer_wait_user;
}
