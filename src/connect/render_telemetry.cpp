#include "render.hpp"
#include "printer_type.hpp"

#include <client_response.hpp>
#include <segmented_json_macros.h>
#include <lfn.h>
#include <filename_type.hpp>
#include <filepath_operation.h>
#include <timing.h>
#include <state/printer_state.hpp>
#include <transfers/transfer.hpp>
#include <filament.hpp>
#include <filament_list.hpp>
#include <filament_sensor_states.hpp>

#include <option/has_cancel_object.h>
#if HAS_CANCEL_OBJECT()
    #include <feature/cancel_object/cancel_object.hpp>
#endif

#include <option/has_chamber_filtration_api.h>
#if HAS_CHAMBER_FILTRATION_API()
    #include <feature/chamber_filtration/chamber_filtration.hpp>
#endif

#include <cassert>
#include <cstring>
#include <cinttypes>

#include <marlin_server_shared.h>
#include <mbedtls/base64.h>

#include <option/has_mmu2.h>
#include <option/has_toolchanger.h>

using json::JsonOutput;
using json::JsonResult;
using printer_state::DeviceState;
using std::get_if;
using std::make_tuple;
using std::min;
using std::move;
using std::nullopt;
using std::optional;
using std::tuple;
using std::visit;
using transfers::Monitor;

#define JSON_MAC(NAME, VAL) JSON_FIELD_STR_FORMAT(NAME, "%02hhX:%02hhX:%02hhX:%02hhX:%02hhX:%02hhX", VAL[0], VAL[1], VAL[2], VAL[3], VAL[4], VAL[5])
#define JSON_IP(NAME, VAL)  JSON_FIELD_STR_FORMAT(NAME, "%hhu.%hhu.%hhu.%hhu", VAL[0], VAL[1], VAL[2], VAL[3])

namespace connect_client::detail {

#if PRINTER_IS_PRUSA_iX()
const char *to_str(FilamentSensorState state) {
    switch (state) {
    case FilamentSensorState::NotInitialized:
        return "NOT_INITIALIZED";
    case FilamentSensorState::NotCalibrated:
        return "NOT_CALIBRATED";
    case FilamentSensorState::HasFilament:
        return "HAS_FILAMENT";
    case FilamentSensorState::NoFilament:
        return "NO_FILAMENT";
    case FilamentSensorState::NotConnected:
        return "NOT_CONNECTED";
    case FilamentSensorState::Disabled:
        return "DISABLED";
    }

    return "Unknown";
}
#endif

static std::optional<transfers::Monitor::Status> get_transfer_status(size_t resume_point, const RenderState &state) {
    if (state.transfer_id.has_value()) {
        // If we've seen a transfer info previously, allow using a stale one to continue there.
        auto transfer_status = Monitor::instance.status(resume_point != 0);
        if (transfer_status.has_value() && transfer_status->id != state.transfer_id) {
            // But if the ID changed mid-report, bail out.
            return nullopt;
        }
        return transfer_status;
    } else {
        return nullopt;
    }
}

JsonResult render_msg(size_t resume_point, JsonOutput &output, RenderState &, const transfers::Download::InlineRequest &request) {
    // Keep the indentation of the JSON in here!
    // clang-format off
        JSON_START;
        JSON_OBJ_START;
            JSON_FIELD_STR("transfer", "inline") JSON_COMMA;
            if (request.details.has_value()) {
                JSON_FIELD_STR("hash", request.details->hash) JSON_COMMA;
                JSON_FIELD_INT("team_id", request.details->team_id) JSON_COMMA;
                JSON_FIELD_INT("transfer_id", request.details->transfer_id.to_uint32_t()) JSON_COMMA;
            }
            // Relates both to size of the FS block.
            JSON_FIELD_INT("chunk", 4096) JSON_COMMA;
            JSON_FIELD_INT("file_id", request.file_id) JSON_COMMA;
            JSON_FIELD_INT("start", request.start) JSON_COMMA;
            JSON_FIELD_INT("end", request.end);
        JSON_OBJ_END;
        JSON_END;
    // clang-format on
}

JsonResult render_msg(size_t resume_point, JsonOutput &output, RenderState &state, const SendTelemetry &telemetry) {
    const auto params = state.printer.params();

    const optional<Monitor::Status> transfer_status = get_transfer_status(resume_point, state);
    const auto &preferred_head = params.slots[params.preferred_head()];

#if PRINTER_IS_PRUSA_iX()
    auto extruder_fs_state = preferred_head.extruder_fs_state;
    auto remote_fs_state = preferred_head.remote_fs_state;
#endif

    // Keep the indentation of the JSON in here!
    // clang-format off
        JSON_START;
        JSON_OBJ_START;
            if (transfer_status.has_value()) {
                // We use the guard-versions here, because we re-acquire
                // the status on each resume of this "coroutine". In the
                // very rare case the transfer ends and a new one starts in
                // between, it might go away and we need to abort this
                // attempt (we'll retry later on).
                //
                // To minimize the risk, we place these first.
                //
                // And yes, we need the guard on each one, because we can
                // resume at each and every of these fields.
                JSON_FIELD_INT_G(transfer_status.has_value(), "transfer_id", transfer_status->id.to_uint32_t()) JSON_COMMA;
                JSON_FIELD_INT_G(transfer_status.has_value(), "transfer_transferred", transfer_status->download_progress.get_valid_size()) JSON_COMMA;
                JSON_FIELD_INT_G(transfer_status.has_value(), "transfer_time_remaining", transfer_status->time_remaining_estimate()) JSON_COMMA;
                JSON_FIELD_FFIXED_G(transfer_status.has_value(), "transfer_progress", transfer_status->progress_estimate() * 100.0, 1) JSON_COMMA;
            }

            // These are not included in the fingerprint as they are changing a lot.
            if (params.has_job) {
                JSON_FIELD_INT("job_id", params.job_id) JSON_COMMA;
                JSON_FIELD_INT("time_printing", params.print_duration) JSON_COMMA;
                if (params.time_to_end != marlin_server::TIME_TO_END_INVALID) {
                    JSON_FIELD_INT("time_remaining", params.time_to_end) JSON_COMMA;
                }
                if (params.time_to_pause != marlin_server::TIME_TO_END_INVALID) {
                    // Connect calls it "filament change". Slicer "Time to
                    // color change". But in reality it is both pause and
                    // filament change (M600 / M601).
                    JSON_FIELD_INT("filament_change_in", params.time_to_pause) JSON_COMMA;
                }
                JSON_FIELD_INT("progress", params.progress_percent) JSON_COMMA;
            }

            // This info is duplicated in the slots structure if we have
            // MMU/toolchanger. Eventually, it would be gread to deduplicate in
            // some way (eg. send the slots structure only), but for that we
            // need to coordinate with Connect, as these are probably
            // "essential" fields right now.
            if (telemetry.mode == SendTelemetry::Mode::Full) {
                JSON_FIELD_FFIXED("temp_nozzle", preferred_head.temp_nozzle, 1) JSON_COMMA;
                JSON_FIELD_FFIXED("temp_bed", params.temp_bed, 1) JSON_COMMA;
#if PRINTER_IS_PRUSA_iX()
                JSON_FIELD_FFIXED("temp_heatbreak", preferred_head.temp_heatbreak, 1) JSON_COMMA;
                JSON_FIELD_FFIXED("temp_psu", params.temp_psu, 1) JSON_COMMA;
                JSON_FIELD_FFIXED("temp_ambient", params.temp_ambient, 1) JSON_COMMA;
                if (extruder_fs_state) {
                    JSON_FIELD_STR_G(extruder_fs_state, "extruder_fs_state", to_str(*extruder_fs_state)) JSON_COMMA;
                }
                if (remote_fs_state) {
                    JSON_FIELD_STR_G(extruder_fs_state, "remote_fs_state", to_str(*remote_fs_state)) JSON_COMMA;
                }
#endif
                JSON_FIELD_FFIXED("target_nozzle", params.target_nozzle, 1) JSON_COMMA;
                JSON_FIELD_FFIXED("target_bed", params.target_bed, 1) JSON_COMMA;
                JSON_FIELD_INT("speed", params.print_speed) JSON_COMMA;
                JSON_FIELD_INT("flow", params.flow_factor) JSON_COMMA;
                if (strlen(params.slots[params.preferred_slot()].material.data()) > 0) {
                    JSON_FIELD_STR("material", params.slots[params.preferred_slot()].material.data()) JSON_COMMA;
                }
#if XL_ENCLOSURE_SUPPORT()
                if (params.enclosure_info.present) {
                    JSON_FIELD_OBJ("enclosure");
                        JSON_FIELD_INT("temp", params.enclosure_info.temp) JSON_COMMA;
                        JSON_FIELD_INT("fan_rpm", params.enclosure_info.fan_rpm) JSON_COMMA;
                        JSON_FIELD_INT("time_in_use", params.enclosure_info.time_in_use);
                    JSON_OBJ_END JSON_COMMA;
                }
#endif
#if PRINTER_IS_PRUSA_COREONE()
                JSON_FIELD_OBJ("chamber");
                    JSON_FIELD_FFIXED("temp", params.chamber_info.current_temp, 1) JSON_COMMA;
                    JSON_FIELD_INT("target_temp", params.chamber_info.target_temp) JSON_COMMA;
                    JSON_FIELD_INT("fan_1_rpm", params.chamber_info.fan_1_rpm) JSON_COMMA;
                    JSON_FIELD_INT("fan_2_rpm", params.chamber_info.fan_2_rpm) JSON_COMMA;
                    JSON_FIELD_INT("fan_pwm_target", params.chamber_info.fan_pwm_target) JSON_COMMA;
                    JSON_FIELD_INT("led_intensity", params.chamber_info.led_intensity);
                JSON_OBJ_END JSON_COMMA;
#endif
                if (!params.has_job) {
                    // To avoid spamming the DB, connect doesn't want positions during printing
                    JSON_FIELD_FFIXED("axis_x", params.pos[Printer::X_AXIS_POS], 2) JSON_COMMA;
                    JSON_FIELD_FFIXED("axis_y", params.pos[Printer::Y_AXIS_POS], 2) JSON_COMMA;
                }
                JSON_FIELD_FFIXED("axis_z", params.pos[Printer::Z_AXIS_POS], 2) JSON_COMMA;
                if (params.has_job) {
                    JSON_FIELD_INT("fan_extruder", preferred_head.heatbreak_fan_rpm) JSON_COMMA;
                    JSON_FIELD_INT("fan_print", preferred_head.print_fan_rpm) JSON_COMMA;
                    JSON_FIELD_FFIXED("filament", params.filament_used, 1) JSON_COMMA;
                }

#if HAS_MMU2() || HAS_TOOLCHANGER()
                // Skip if we have single-tool XL or mk4 without MMU/with MMU disabled.
                if (params.enabled_tool_cnt() > 1) {
                    JSON_FIELD_OBJ("slot");
                        state.iter = 0;
                        while (state.iter < params.slots.size()) {
                            // Note: XL can have multiple slots, but not consequitive, therefore the trick with a mask.
                            if (params.slot_mask & (1 << state.iter)) {
                                JSON_CUSTOM("\"%zu\":{", state.iter + 1);
                                    JSON_FIELD_STR("material", params.slots[state.iter].material.data()) JSON_COMMA;
                                    JSON_FIELD_FFIXED("temp", params.slots[state.iter].temp_nozzle, 1) JSON_COMMA;
                                    JSON_FIELD_FFIXED("fan_hotend", params.slots[state.iter].heatbreak_fan_rpm, 1) JSON_COMMA;
                                    JSON_FIELD_FFIXED("fan_print", params.slots[state.iter].print_fan_rpm, 1);
                                JSON_OBJ_END JSON_COMMA;
                            }
                            state.iter++;
                        }
#if HAS_MMU2()
                        // If we are in here (enabled_tool_cnt() > 0), it can
                        // be either because we have MMU _enabled_ - therefore,
                        // we send the info, or because we have a toolchanger
                        // (in which case it's not MMU and we don't send it).
                        JSON_FIELD_INT("state", params.progress_code) JSON_COMMA;
                        JSON_FIELD_STR_FORMAT("command", "%c", params.command_code) JSON_COMMA;
#endif
                        JSON_FIELD_INT("active", params.active_slot);
                    JSON_OBJ_END JSON_COMMA;
                }
#endif
            }
            if (state.background_command_id.has_value()) {
                JSON_FIELD_INT("command_id", *state.background_command_id) JSON_COMMA;
            }

            if (params.state.dialog.has_value()) {
                JSON_FIELD_INT_G(params.state.dialog.has_value(), "dialog_id", params.state.dialog->dialog_id.to_uint32_t()) JSON_COMMA;
            }
            // State is sent always, first because it seems important, but
            // also, we want something that doesn't have the final comma on
            // it.
            JSON_FIELD_STR("state", to_str(params.state.device_state));
        JSON_OBJ_END;
        JSON_END;
    // clang-format on
}

} // namespace connect_client::detail
