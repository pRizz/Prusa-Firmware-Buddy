#include "marlin_server.hpp"

#include <freertos/critical_section.hpp>
#include <marlin_stubs/skippable_gcode.hpp>
#include "marlin_client_queue.hpp"
#include "marlin_server_request.hpp"
#include <inttypes.h>
#include <stdarg.h>
#include <cstdint>
#include <stdio.h>
#include <string.h> //strncmp
#include <assert.h>
#include <charconv>

#include "adc.hpp"
#include "marlin_events.h"
#include "marlin_print_preview.hpp"
#include "utils/exponential_backoff.hpp"
#include "bsod.h"
#include "module/prusa/tool_mapper.hpp"
#include "module/prusa/spool_join.hpp"
#include "print_utils.hpp"
#include "random.h"
#include "timing.h"
#include "cmsis_os.h"
#include <logging/log.hpp>
#include <bsod_gui.hpp>
#include <usb_host.h>
#include <usb_host.h>
#include <lfn.h>
#include <media_prefetch/media_prefetch.hpp>
#include <gcode/gcode_reader_restore_info.hpp>
#include <dirent.h>
#include <scope_guard.hpp>
#include <tools_mapping.hpp>
#include <RAII.hpp>
#include <inject_queue.hpp>
#include <buddy/unreachable.hpp>
#include <utils/string_builder.hpp>
#include <utils/mutex_atomic.hpp>
#include <feature/safety_timer/safety_timer.hpp>
#include <feature/stepper_timeout/stepper_timeout.hpp>

#include "../Marlin/src/lcd/extensible_ui/ui_api.h"
#include "../Marlin/src/gcode/queue.h"
#include "../Marlin/src/gcode/parser.h"
#include "../Marlin/src/module/planner.h"
#include "../Marlin/src/module/stepper.h"
#include "../Marlin/src/module/endstops.h"
#include "../Marlin/src/module/temperature.h"
#include "../Marlin/src/module/probe.h"
#include "../Marlin/src/module/configuration_store.h"
#include "../Marlin/src/module/printcounter.h"
#include "../Marlin/src/feature/babystep.h"
#include "../Marlin/src/feature/bedlevel/bedlevel.h"
#include "../Marlin/src/feature/input_shaper/input_shaper.hpp"
#include "../Marlin/src/feature/pause.h"
#include "../Marlin/src/feature/prusa/measure_axis.h"
#include "../Marlin/src/core/language.h" //GET_TEXT(MSG)
#include "../Marlin/src/gcode/gcode.h"
#include "../Marlin/src/gcode/lcd/M73_PE.h"
#include "../Marlin/src/feature/print_area.h"
#include "../Marlin/src/Marlin.h"
#include "utility_extensions.hpp"
#include <common/gcode/gcode_info_scan.hpp>

#if ENABLED(PRUSA_MMU2)
    #include "../Marlin/src/feature/prusa/MMU2/mmu2_mk4.h"
#endif

#include <option/has_cancel_object.h>
#if HAS_CANCEL_OBJECT()
    #include <feature/cancel_object/cancel_object.hpp>
#endif

#include "hwio.h"
#include "wdt.hpp"
#include "../marlin_stubs/M123.hpp"
#include "fsm_states.hpp"
#include "odometer.hpp"
#include "metric.h"
#include "app_metrics.h"
#include "media_prefetch_instance.hpp"
#include <common/sensor_data.hpp>

#include <option/has_leds.h>

#include "fanctl.hpp"
#include "lcd/extensible_ui/ui_api.h"

#include <option/has_gui.h>
#include <option/has_toolchanger.h>
#include <option/has_selftest.h>
#include <option/has_mmu2.h>
#include <option/has_dwarf.h>
#include <option/has_remote_bed.h>
#include <option/has_modular_bed.h>
#include <option/has_loadcell.h>
#include <option/has_nfc.h>
#include <option/has_sheet_profiles.h>
#include <option/has_i2c_expander.h>
#include <option/has_chamber_api.h>
#include <option/xbuddy_extension_variant_standard.h>
#include <option/has_emergency_stop.h>
#include <option/has_uneven_bed_prompt.h>
#include <option/has_chamber_vents.h>

#if HAS_DWARF()
    #include <puppies/Dwarf.hpp>
#endif /*HAS_DWARF()*/

#if HAS_REMOTE_BED()
    #include <common/feature/remote_bed/remote_bed.hpp>
#endif

#if HAS_SELFTEST()
    #include "printer_selftest.hpp"
    #include "i_selftest.hpp"
    #include "selftest_axis.h"
#endif

#if HAS_SHEET_PROFILES()
    #include "SteelSheets.hpp"
#endif

#if ENABLED(CRASH_RECOVERY)
    #include "../Marlin/src/feature/prusa/crash_recovery.hpp"
    #include "crash_recovery_type.hpp"
#endif

#if ENABLED(POWER_PANIC)
    #include "power_panic.hpp"
#endif

#if ENABLED(PRUSA_TOOLCHANGER)
    #include "module/prusa/toolchanger.h"
#endif

#if HAS_MMU2()
    #include <mmu2/mmu2_fsm.hpp>
    #include <mmu2/maintenance.hpp>
#endif

#include <config_store/store_instance.hpp>

#if XL_ENCLOSURE_SUPPORT()
    #include "xl_enclosure.hpp"
#endif

#if HAS_NFC()
    #include <nfc.hpp>
    #include <fsm_network_setup.hpp>
#endif

#if HAS_CHAMBER_API()
    #include <feature/chamber/chamber.hpp>
#endif

#include <option/has_chamber_filtration_api.h>
#if HAS_CHAMBER_FILTRATION_API()
    #include <feature/chamber_filtration/chamber_filtration.hpp>
#endif

#if XBUDDY_EXTENSION_VARIANT_STANDARD()
    #include <feature/xbuddy_extension/xbuddy_extension.hpp>
#endif
#if HAS_EMERGENCY_STOP()
    #include <feature/emergency_stop/emergency_stop.hpp>
#endif

#include <option/has_ceiling_clearance.h>
#if HAS_CEILING_CLEARANCE()
    #include <feature/ceiling_clearance/ceiling_clearance.hpp>
#endif

#include <option/has_auto_retract.h>
#if HAS_AUTO_RETRACT()
    #include <feature/auto_retract/auto_retract.hpp>
    #include <feature/retract_tracker/retract_tracker.hpp>
#endif

#include <option/buddy_enable_wui.h>
#if BUDDY_ENABLE_WUI()
    #include <wui.h>
#endif

#include <feature/print_status_message/print_status_message_mgr.hpp>

namespace marlin_client {
extern osThreadId marlin_client_task[MARLIN_MAX_CLIENTS];
extern marlin_client::ClientQueue marlin_client_queue[MARLIN_MAX_CLIENTS];
} // namespace marlin_client

namespace marlin_server {

using ClientQueue = marlin_client::ClientQueue;

void media_prefetch_start();
void media_print_loop();
bool active_extruder_fan_checks();
void gui_ready_to_print();
void gui_cant_print();
void print_exit();

namespace internal {

    struct ServerState {
        EventMask notify_events[MARLIN_MAX_CLIENTS];
        EventMask notify_changes[MARLIN_MAX_CLIENTS];
        EventMask client_events[MARLIN_MAX_CLIENTS];
        State print_state;
        bool print_is_serial = false;
#if ENABLED(CRASH_RECOVERY)
        bool aborting_did_crash_trigger = false;
#endif
        resume_state_t resume;
        uint32_t last_update;
        uint16_t flags;
        int32_t knob_position = 0;
#if ENABLED(AXIS_MEASURE)
        xy_float_t axis_length = { -1, -1 };
        Measure_axis *measure_axis = nullptr;
#endif
        bool was_print_time_saved = false;
#if HAS_MMU2()
        bool mmu_maintenance_checked = false;
#endif
    };

    struct PrintState {
        bool resume_pending = false;
        std::optional<uint32_t> recover_media_error_at;
        buddy::ExponentialBackoff<uint32_t, 30, 300> recover_media_error_backoff;
        GCodeReaderStreamRestoreInfo media_restore_info;
        bool skip_gcode = false;
        bool file_open_reported = false;
    };

    enum class PauseType {
        Pause,
        Crash,
    };

#if ENABLED(AXIS_MEASURE)
    enum class Axis_length_t {
        shorter,
        longer,
        ok,
    };

    Axis_length_t xy_axes_length_ok();
#endif

    extern ServerState server;
    extern PrintState print_state;
    extern fsm::States fsm_states;

    void pause_print(PauseType type = PauseType::Pause);
    void handle_warnings();
    void server_print_loop();
    void process_request_flags();
    bool process_server_request(const Request &request);
    void server_update_vars_now();
    uint64_t send_notify_events_to_client(int client_id, ClientQueue &queue, uint64_t event_mask);
    uint8_t send_notify_event(Event event, uint32_t user32, uint16_t user16);
    bool send_notify_event_to_client(int client_id, ClientQueue &queue, Event event, uint32_t user32, uint16_t user16);
    void settings_load();
    void safely_unload_filament_from_nozzle_to_mmu();
    void finalize_print(bool finished);
    void pre_finalize_print(bool finished);
    void fsm_destroy_and_create(ClientFSM old_type, ClientFSM new_type, fsm::BaseData data);
    void schedule_media_retry();
    void clear_media_error();
    std::optional<WarningType> prefetch_status_to_warning(MediaPrefetchManager::Status status);
    void update_sfn();
    void try_recover_from_media_error();
    void measure_axes_and_home();
    void resuming_reheating();
    bool process_preview_and_start_state(State state, bool &did_not_start_print);
    bool process_pause_state(State state);
    bool process_media_recovery_state(State state);
    bool process_resume_state(State state, bool &abort_resuming);
    bool process_finish_state(State state);
    bool process_crash_state(State state);
    bool process_power_panic_state(State state);
    void run_safety_checks();
    bool hotend_error_failed();
    bool consume_postponed_full_fan();
    void reset_safety_errors();

} // namespace internal
} // namespace marlin_server
