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

const char *to_str(Printer::FinishedJobResult result) {
    switch (result) {
    case Printer::FinishedJobResult::FIN_OK:
        return "FIN_OK";
    case Printer::FinishedJobResult::FIN_STOPPED:
        return "FIN_STOPPED";
    }
    return nullptr;
}

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

JsonResult render_msg(size_t resume_point, JsonOutput &output, RenderState &state, const Event &event) {
    const auto params = state.printer.params();
    const auto &info = state.printer.printer_info();
    const bool has_extra = (event.type != EventType::Accepted) && (event.type != EventType::Rejected);
    std::optional<Printer::FinishedJobResult> job_state;

    const char *reject_with = nullptr;
    Printer::NetCreds creds = {};
    if (event.type == EventType::Info) {
        // Technically, it would be better to store this as part of
        // the render state. But that would be a bit wasteful, so
        // we do it here in a "late" fasion. At worst, we would get
        // the api key and ssid from two different times, but they
        // are not directly related to each other anyway.
        //
        // Prepare the creds here, before the magical switch hidden in
        // JSON_START... Otherwise it could be skipped on further
        // runs/resumes.
        creds = state.printer.net_creds();
    }

    if (event.type == EventType::JobInfo && (!params.has_job || event.job_id.value_or(params.job_id) != params.job_id)) {
        // We have a job history (with just the state) of two last jobs, if this is one of them, send it,
        // otherwise reject.
        if (event.job_id.has_value()) {
            job_state = state.printer.get_prior_job_result(event.job_id.value());
        }
        if (job_state == nullopt) {
            reject_with = params.has_job ? "Job ID doesn't match" : "No job in progress";
        }
    }

    if (event.type == EventType::FileInfo && !state.has_stat && !state.file_extra.renderer.holds_alternative<DirRenderer>()) {
        // The file probably doesn't exist or something
        // Exception for /usb, as that one doesn't have stat even though it exists.
        reject_with = "File not found";
    }

    const optional<Monitor::Status> transfer_status = event.type == EventType::TransferInfo ? get_transfer_status(resume_point, state) : nullopt;

    if (reject_with != nullptr) {
        // The fact we can render in multiple steps doesn't matter, we would
        // descend into here every time and resume the Rejected event.
        Event rejected(event);
        rejected.type = EventType::Rejected;
        rejected.reason = reject_with;
        return render_msg(resume_point, output, state, rejected);
    }

    // Keep the indentation of the JSON in here!
    // clang-format off
        JSON_START;
        JSON_OBJ_START;
            if (has_extra && params.has_job) {
                JSON_FIELD_INT("job_id", params.job_id) JSON_COMMA;
            }

            if (event.reason != nullptr) {
                JSON_FIELD_STR("reason", event.reason) JSON_COMMA;
            }

            if (event.machine_reason != MachineReason::None) {
                JSON_FIELD_STR("machine_reason", to_str(event.machine_reason)) JSON_COMMA;
            }

            // Relevant "data" block, if any

            // Note: this would very much like to be a switch. Nevertheless, the
            // JSON_START/macros are already a big and quite nasty switch, and the
            // JSON_... macros don't work in a nested switch :-(.
            if (event.type == EventType::Info) {
                JSON_FIELD_OBJ("data");
                    JSON_FIELD_STR("firmware", info.firmware_version) JSON_COMMA;
                    JSON_FIELD_STR_FORMAT("printer_type", "%hhu.%hhu.%hhu", params.version.type, params.version.version, params.version.subversion) JSON_COMMA;
                    JSON_FIELD_STR("sn", info.serial_number.begin()) JSON_COMMA;
                    JSON_FIELD_BOOL("appendix", info.appendix) JSON_COMMA;
                    JSON_FIELD_STR("fingerprint", info.fingerprint) JSON_COMMA;
                    // TODO: Deprecated, kept for now for backwards compatibility. Parts of the tools object.
                    // Remove eventually.
                    JSON_FIELD_FFIXED("nozzle_diameter", params.slots[params.preferred_head()].nozzle_diameter, 2) JSON_COMMA;
                    JSON_FIELD_BOOL("transfer_paused", !params.can_start_download) JSON_COMMA;
                    if (strlen(creds.pl_password) > 0) {
                        JSON_FIELD_STR("api_key", creds.pl_password) JSON_COMMA;
                    }
                    JSON_FIELD_ARR("storages");
                    if (params.has_usb) {
                        JSON_OBJ_START;
                            // TODO: We may want to send a bit more info, just
                            //   for the user comfort, in particular:
                            // * Number of files directly under the root
                            // * Sizes (total/free/...)
                            // * Name of the filesystem if it is set/known.
                            JSON_FIELD_STR("mountpoint", "/usb") JSON_COMMA;
                            JSON_FIELD_STR("type", "USB") JSON_COMMA;
                            JSON_FIELD_BOOL("read_only", false) JSON_COMMA;
                            JSON_FIELD_INT("free_space", params.usb_space_free) JSON_COMMA;
                            JSON_FIELD_BOOL("is_sfn", true);
                        JSON_OBJ_END;
                    }
                    JSON_ARR_END JSON_COMMA;
                    JSON_FIELD_OBJ("network_info");
                        if (state.lan.has_value()) {
                            JSON_MAC("lan_mac", state.lan->mac) JSON_COMMA;
                            JSON_IP("lan_ipv4", state.lan->ip) JSON_COMMA;
                        }
                        if (state.wifi.has_value()) {
                            if (strlen(creds.ssid) > 0) {
                                JSON_FIELD_STR("wifi_ssid", creds.ssid) JSON_COMMA;
                            }
                            JSON_MAC("wifi_mac", state.wifi->mac) JSON_COMMA;
                            JSON_IP("wifi_ipv4", state.wifi->ip) JSON_COMMA;
                        }
                        JSON_FIELD_STR("hostname", creds.hostname);
                    JSON_OBJ_END JSON_COMMA;

                    JSON_FIELD_OBJ("tools");
                        for (state.iter = 0, state.need_comma = false; state.iter < Printer::NUMBER_OF_SLOTS; state.iter ++) {
                            if (params.slot_mask & (1 << state.iter)) {
                                if (state.need_comma) {
                                    JSON_COMMA;
                                }

                                JSON_CUSTOM("\"%zu\":{", state.iter + 1);
                                    JSON_FIELD_FFIXED("nozzle_diameter", params.slots[state.iter].nozzle_diameter, 2) JSON_COMMA;
                                    JSON_FIELD_BOOL("high_flow", params.slots[state.iter].high_flow) JSON_COMMA;
                                    JSON_FIELD_BOOL("hardened", params.slots[state.iter].hardened) JSON_COMMA;
                                    JSON_FIELD_STR("material", *params.slots[state.iter].material.data() ? params.slots[state.iter].material.data() : "---");
                                JSON_OBJ_END;

                                state.need_comma = true;
                            }
                        }
                    JSON_OBJ_END JSON_COMMA;

#if XL_ENCLOSURE_SUPPORT()
                    if (params.enclosure_info.present) {
                        JSON_FIELD_OBJ("enclosure");
                            JSON_FIELD_BOOL("enabled", params.enclosure_info.enabled) JSON_COMMA;
                            JSON_FIELD_BOOL("printing_filtration", params.enclosure_info.printing_filtration) JSON_COMMA;
                            JSON_FIELD_BOOL("post_print", params.enclosure_info.post_print) JSON_COMMA;
                            JSON_FIELD_INT("post_print_filtration_time", params.enclosure_info.post_print_filtration_time) JSON_COMMA;
                            JSON_FIELD_INT("filter_lifetime", buddy::chamber_filtration().filter_lifetime_s()) JSON_COMMA;
                            JSON_FIELD_ARR("filtration_filaments");
                            for (state.iter = 0, state.need_comma = false; state.iter <all_filament_types.size(); state.iter++) {
                                if(!all_filament_types[state.iter].parameters().requires_filtration) {
                                    continue;
                                }
                                if (state.need_comma) {
                                    JSON_COMMA;
                                }
                                JSON_CUSTOM("\"%s\"",  all_filament_types[state.iter].parameters().name.data());
                                state.need_comma = true;
                            }
                            JSON_ARR_END;
                        JSON_OBJ_END JSON_COMMA;
                    }
#endif
#if HAS_MMU2()
                    JSON_FIELD_OBJ("mmu");
                        JSON_FIELD_BOOL("enabled", params.enabled_tool_cnt() > 1) JSON_COMMA;
                        JSON_FIELD_STR_FORMAT("version", "%d.%d.%d", params.mmu_version.major, params.mmu_version.minor, params.mmu_version.build);
                    JSON_OBJ_END JSON_COMMA;
#endif
#if PRINTER_IS_PRUSA_COREONE()
                    JSON_FIELD_BOOL("addon_power", params.addon_power) JSON_COMMA;
#endif
                    JSON_FIELD_INT("slots", params.enabled_tool_cnt());
                JSON_OBJ_END JSON_COMMA;
            } else if (event.type == EventType::JobInfo) {
                JSON_FIELD_OBJ("data");
                    if (job_state != nullopt) {
                        JSON_FIELD_STR("state", to_str(job_state.value()));
                    } else {
                        if (params.state.device_state == DeviceState::Printing) {
                            JSON_FIELD_STR("state", "PRINTING") JSON_COMMA;
                        } else {
                            JSON_FIELD_STR("state", "PAUSED") JSON_COMMA;
                        }
                        // The JobInfo doesn't claim the buffer, so we get it to store the path.
                        assert(params.job_path() != nullptr);
                        if (state.has_stat) {
                            JSON_FIELD_INT("size", state.st.st_size) JSON_COMMA;
                            JSON_FIELD_INT("m_timestamp", state.st.st_mtime) JSON_COMMA;
                        }
                        if (params.job_lfn() != nullptr) {
                            JSON_FIELD_STR("display_name", params.job_lfn());
                        } else {
                            JSON_FIELD_STR("display_name", basename_b(params.job_path()));
                        }
                        JSON_COMMA;
                        if (event.start_cmd_id.has_value()) {
                            JSON_FIELD_INT("start_cmd_id", *event.start_cmd_id) JSON_COMMA;
                        }
                        JSON_FIELD_STR("path", params.job_path());
                    }
                JSON_OBJ_END JSON_COMMA;
            } else if (event.type == EventType::FileInfo) {
                JSON_FIELD_OBJ("data");
                    // Note: This chunk might or might not render anything.
                    //
                    // * In theory, it can be EmptyRenderer (though that should not happen in practice?)
                    // * In case of the PreviewRenderer, it could be that it is
                    //   not a gcode at all or doesn't contain the preview.

                    //
                    // For that reason, the renderer is responsible for
                    // rendering a trailing comma if it outputs anything at
                    // all.
                    JSON_CHUNK(state.file_extra.renderer);

                    // BEWARE:
                    // If you add another field below, make sure to also
                    // include it in the blacklist of meta headers (see MetaFilter::Ignore).
                    if (state.has_stat) {
                        // has_stat might be off in case of /usb, that one acts
                        // "weird", as it is root of the FS.
                        JSON_FIELD_INT("size", state.st.st_size) JSON_COMMA;
                        JSON_FIELD_INT("m_timestamp", state.st.st_mtime) JSON_COMMA;
                    }
                    JSON_FIELD_BOOL("read_only", state.read_only) JSON_COMMA;
                    // Warning: the path->name() is there (hidden) for FileInfo
                    // but _not_ for JobInfo. Do not just copy that into that
                    // part!
                    //
                    // XXX: Can the name be SFN?
                    JSON_FIELD_STR("display_name", event.path->name()) JSON_COMMA;
                    JSON_FIELD_STR("type", state.file_extra.renderer.holds_alternative<DirRenderer>() ? "FOLDER" : file_type_by_ext(event.path->path())) JSON_COMMA;
                    JSON_FIELD_STR("path", event.path->path());
                JSON_OBJ_END JSON_COMMA;
            } else if (event.type == EventType::TransferInfo) {
                JSON_FIELD_OBJ("data");
                if (transfer_status.has_value()) {
                    // Warning: The transfer_status was observed to have a
                    // value. But as we don't want to copy to the render state,
                    // we re-acquire it at every resume of this "coroutine".
                    //
                    // And it may become nullopt at that point (because the
                    // transfer has changed in between and we don't want to mix
                    // two inconsistent values).
                    //
                    // Therefore, we use the guards here ‒ in the very rare
                    // occasion (one transfer would have to end and another
                    // _start_ between the callS), we would just abort and
                    // hopefully retry / get asked to retry later on.
                    //
                    // And we really do need the guard on each one, because we
                    // can resume at each spot.
                    JSON_FIELD_INT_G(transfer_status.has_value(), "size", transfer_status->expected) JSON_COMMA;
                    JSON_FIELD_INT_G(transfer_status.has_value(), "transferred", transfer_status->download_progress.get_valid_size()) JSON_COMMA;
                    JSON_FIELD_FFIXED_G(transfer_status.has_value(), "progress", transfer_status->progress_estimate() * 100.0, 1) JSON_COMMA;
                    JSON_FIELD_INT_G(transfer_status.has_value(), "time_remaining", transfer_status->time_remaining_estimate()) JSON_COMMA;
                    JSON_FIELD_INT_G(transfer_status.has_value(), "time_transferring", transfer_status->time_transferring()) JSON_COMMA;
                    // Note: This works, because destination cannot go from non null to null
                    // (if one transfer ends and another starts mid report, we bail out)
                    if (transfer_status->destination) {
                        // FIXME: This one is problematic, part is SFN, part is LFN.
                        //
                        // For now, we consider it SFN (because that always produces valid utf8 at least), needs fix later on.
                        JSON_FIELD_STR_G(transfer_status.has_value(), "path", transfer_status->destination) JSON_COMMA;
                    }
                    if (event.start_cmd_id.has_value()) {
                        JSON_FIELD_INT("start_cmd_id", *event.start_cmd_id) JSON_COMMA;
                    }
                    JSON_FIELD_STR_G(transfer_status.has_value(), "type", to_str(transfer_status->type));
                } else {
                    JSON_FIELD_STR("type", "NO_TRANSFER");
                }
                JSON_OBJ_END JSON_COMMA;
            } else if (event.type == EventType::TransferStopped || event.type == EventType::TransferAborted || event.type == EventType::TransferFinished) {
                if (event.start_cmd_id.has_value()) {
                    JSON_FIELD_OBJ("data");
                        JSON_FIELD_INT("start_cmd_id", *event.start_cmd_id);
                    JSON_OBJ_END JSON_COMMA;
                }
            } else if (event.type == EventType::FileChanged) {
                // FIXME: This is just an educated guess, the exact protocol has not been decided yet.
                JSON_FIELD_OBJ("data");
                    if (params.has_usb) {
                        JSON_FIELD_INT("free_space", params.usb_space_free) JSON_COMMA;
                    }
                    if (event.incident == transfers::ChangedPath::Incident::Created) {
                        JSON_FIELD_STR("new_path", event.path->path()) JSON_COMMA;
                    } else if (event.incident == transfers::ChangedPath::Incident::Deleted) {
                        JSON_FIELD_STR("old_path", event.path->path()) JSON_COMMA;
                    } else /*Combined*/ {
                        JSON_FIELD_STR("new_path", event.path->path()) JSON_COMMA;
                        JSON_FIELD_BOOL("rescan", true) JSON_COMMA;
                    }
                    JSON_FIELD_OBJ("file")
                        if (state.has_stat) {
                            // has_stat might be off in case of /usb, that one acts
                            // "weird", as it is root of the FS.
                            JSON_FIELD_INT("size", state.st.st_size) JSON_COMMA;
                            JSON_FIELD_INT("m_timestamp", state.st.st_mtime) JSON_COMMA;
                        }
                        JSON_FIELD_STR("type", event.is_file ? file_type_by_ext(event.path->path()) : "FOLDER" ) JSON_COMMA;
                        JSON_FIELD_STR("name", event.path->name());
                    JSON_OBJ_END;
                JSON_OBJ_END JSON_COMMA;
            } else if (event.type == EventType::CancelableChanged) {
#if HAS_CANCEL_OBJECT()
                JSON_FIELD_OBJ("data");
                    JSON_FIELD_ARR("objects");
                        state.iter = 0;

                        // Note: Because we're reading out object_count and is_object_cancelled directly,
                        // we can end up with inconsistent data being rendered.
                        // But that is fine, if that happens, cancel_object.revision changes and new render will be issued later, so we will eventually end up being consistent

                        while (static_cast<buddy::CancelObject::ObjectID>(state.iter) < buddy::cancel_object().object_count()) {
                            if (state.iter != 0) {
                                JSON_COMMA;
                            }
                            JSON_OBJ_START;
                                // is_object_cancelled will work even if i is outside of bounds, so having object_count inconsistent is fine
                                JSON_FIELD_BOOL("canceled", buddy::cancel_object().is_object_cancelled(state.iter)) JSON_COMMA;
                                JSON_FIELD_INT("id", state.iter);
                            JSON_OBJ_END;
                            state.iter++;
                        }
                    JSON_ARR_END;
                JSON_OBJ_END JSON_COMMA;
#endif
            } else if (event.type == EventType::StateChanged) {
                JSON_FIELD_OBJ("data");
                    // Unfortunately, we don't have any field that would be
                    // guaranteed to be present, so we need to do this insanity
                    // just to avoid a trailing comman, which is forbidden in
                    // JSON :-(
                    state.need_comma = false;

                    if (params.state.has_code()) {
                        state.need_comma = true;
                        // The additional value() check is there for the event
                        // where the below doesn't fit, we get resumed and
                        // the code disappears in between - in that case we
                        // kind of send a wrong value, but we will generate a
                        // new one soon after.
                        //
                        // (We could use the _GUARD version, but that one seems
                        // too drastic for this case).
                        JSON_FIELD_STR_FORMAT("code", "%05" PRIu16, params.state.code_num());
                    }

                    if (params.state.title()) {
                        if (state.need_comma) {
                            JSON_COMMA;
                        }

                        state.need_comma = true;

                        // Similar trick as above for the suspend/resume-race.
                        JSON_FIELD_STR("title", params.state.title() ? : "");
                    }

                    if (params.state.text()) {
                        if (state.need_comma) {
                            JSON_COMMA;
                        }

                        state.need_comma = true;

                        JSON_FIELD_STR("text", params.state.text() ? : "");
                    }

                    // We store the buttons here to preserve them across the
                    // resume points. This is fine, as these are all static
                    // global variables, nothing allocated dynamically.
                    //
                    // We do so to:
                    // * Make the iteration code simpler (no need to worry about changes).
                    // * Make sure the result is consistent set of buttons that
                    //   make sense to at least some dialog.
                    if ((state.buttons = params.state.buttons()) != nullptr) {
                        if (state.need_comma) {
                            JSON_COMMA;
                        }

                        state.need_comma = true;

                        JSON_FIELD_ARR("buttons");
                        state.iter = 0;
                        while (state.iter < MAX_RESPONSES) {
                            if (state.buttons[state.iter] == Response::_none) {
                                // We've run out of buttons.
                                break;
                            }
                            if (state.iter > 0) {
                                JSON_COMMA;
                            }
                            JSON_CUSTOM("\"%s\"", to_str(state.buttons[state.iter]));
                            state.iter ++;
                        }
                        JSON_ARR_END;
                    }
                JSON_OBJ_END JSON_COMMA;
            }

            if (params.state.dialog.has_value()) {
                JSON_FIELD_INT_G(params.state.dialog.has_value(), "dialog_id", params.state.dialog->dialog_id.to_uint32_t()) JSON_COMMA;
            }
            JSON_FIELD_STR("state", to_str(params.state.device_state)) JSON_COMMA;
            if (event.command_id.has_value()) {
                JSON_FIELD_INT("command_id", *event.command_id) JSON_COMMA;
            }
            if (state.transfer_id.has_value()) {
                JSON_FIELD_INT("transfer_id", (*state.transfer_id).to_uint32_t()) JSON_COMMA;
            }
            JSON_FIELD_STR("event", to_str(event.type));
        JSON_OBJ_END;
        JSON_END;
    // clang-format on
}

} // namespace connect_client::detail
