#include "printer_state.hpp"

#include <fsm_states.hpp>
#include <client_response.hpp>
#include <marlin_vars.hpp>
#include <fsm/safety_timer_phases.hpp>
#include <option/has_chamber_vents.h>
#include <option/has_gearbox_alignment.h>
#include <option/has_mmu2.h>
#include <option/has_dwarf.h>
#include <option/has_input_shaper_calibration.h>
#include <option/has_phase_stepping_calibration.h>
#include <option/xl_enclosure_support.h>
#include <option/has_uneven_bed_prompt.h>
#include <config_store/store_instance.hpp>
#include <option/has_remote_bed.h>
#include <option/has_chamber_filtration_api.h>
#include <option/has_door_sensor_calibration.h>
#include <option/xbuddy_extension_variant_standard.h>
#include <option/has_side_fsensor.h>
#include <option/has_belt_tuning.h>

#if HAS_LOADCELL()
    #include <fsm/nozzle_cleaning_failed_phases.hpp>
    #include <fsm/nozzle_cleaning_failed_mapper.hpp>
#endif

using namespace marlin_server;
using namespace printer_state;
using std::make_tuple;
using std::nullopt;
using std::optional;
using std::tuple;

namespace printer_state {

DeviceState get_print_state(State state, bool ready) {
    switch (state) {
    case State::PrintPreviewQuestions:
        // Should never happen, we catch this before with FSM states,
        // so that we can distinquish between various questions.
        // Nevertheless it has been seen to happen in connect somehow,
        // so make it Attention, so it in that rate occurrence still
        // kind of make sense.
        return DeviceState::Attention;
    case State::PowerPanic_AwaitingResume:
    case State::CrashRecovery_Axis_NOK:
    case State::CrashRecovery_Repeated_Crash:
    case State::CrashRecovery_HOMEFAIL:
        return DeviceState::Attention;
#if HAS_TOOLCHANGER()
    case State::CrashRecovery_Tool_Pickup:
        return DeviceState::Attention;
#endif
#if HAS_TOOLCHANGER() || HAS_MMU2()
    case State::PrintPreviewToolsMapping:
        return DeviceState::Attention;
#endif
    case State::Idle:
    case State::WaitGui:
    case State::PrintPreviewInit:
    case State::PrintPreviewImage:
    case State::PrintInit:
    case State::Exit:
        if (ready) {
            return DeviceState::Ready;
        } else {
            return DeviceState::Idle;
        }
    case State::Printing:
    case State::Aborting_Begin:
    case State::Aborting_WaitIdle:
    case State::Aborting_UnloadFilament:
    case State::Aborting_ParkHead:
    case State::Aborting_Preview:
    case State::Finishing_WaitIdle:
    case State::Finishing_UnloadFilament:
    case State::Finishing_ParkHead:
    case State::PrintPreviewConfirmed:
    case State::SerialPrintInit:
        return DeviceState::Printing;

    case State::PowerPanic_acFault:
    case State::PowerPanic_Resume:
    case State::CrashRecovery_Begin:
    case State::CrashRecovery_Retracting:
    case State::CrashRecovery_Lifting:
    case State::CrashRecovery_ToolchangePowerPanic:
    case State::CrashRecovery_XY_Measure:
    case State::CrashRecovery_XY_HOME:
        return DeviceState::Busy;

    case State::Pausing_Begin:
    case State::Pausing_WaitIdle:
    case State::Pausing_ParkHead:
    case State::Paused:

    case State::Resuming_BufferData:
    case State::MediaErrorRecovery_BufferData:
    case State::Resuming_Begin:
    case State::Resuming_Reheating:
    case State::Pausing_Failed_Code:
    case State::Resuming_UnparkHead_XY:
    case State::Resuming_UnparkHead_ZE:
        return DeviceState::Paused;
    case State::Finished:
        if (ready) {
            return DeviceState::Ready;
        } else {
            return DeviceState::Finished;
        }
    case State::Aborted:
        if (ready) {
            return DeviceState::Ready;
        } else {
            return DeviceState::Stopped;
        }
    }
    return DeviceState::Unknown;
}

const char *to_str(DeviceState state) {
    switch (state) {
    case DeviceState::Idle:
        return "IDLE";
    case DeviceState::Printing:
        return "PRINTING";
    case DeviceState::Paused:
        return "PAUSED";
    case DeviceState::Finished:
        return "FINISHED";
    case DeviceState::Stopped:
        return "STOPPED";
    case DeviceState::Ready:
        return "READY";
    case DeviceState::Error:
        return "ERROR";
    case DeviceState::Busy:
        return "BUSY";
    case DeviceState::Attention:
        return "ATTENTION";
    case DeviceState::Unknown:
    default:
        return "UNKNOWN";
    }
}

ErrCode warning_type_to_error_code(WarningType wtype) {
    switch (wtype) {
    case WarningType::HotendFanError:
        return ErrCode::CONNECT_HOTEND_FAN_ERROR;
    case WarningType::PrintFanError:
        return ErrCode::CONNECT_PRINT_FAN_ERROR;
    case WarningType::HotendTempDiscrepancy:
        return ErrCode::CONNECT_HOTEND_TEMP_DISCREPANCY;
    case WarningType::HeatersTimeout:
        return ErrCode::CONNECT_HEATERS_TIMEOUT;
    case WarningType::NozzleTimeout:
        return ErrCode::CONNECT_NOZZLE_TIMEOUT;
    case WarningType::USBFlashDiskError:
        return ErrCode::CONNECT_USB_FLASH_DISK_ERROR;
    case WarningType::USBDriveUnsupportedFileSystem:
        return ErrCode::WARNING_USB_DRIVE_UNSUPPORTED_FILE_SYSTEM;
    case WarningType::HeatBreakThermistorFail:
        return ErrCode::CONNECT_HEATBREAK_THERMISTOR_FAIL;
#if HAS_SELFTEST()
    case WarningType::ActionSelftestRequired:
        return ErrCode::ERR_SYSTEM_ACTION_SELFTEST_REQUIRED;
#endif
#if ENABLED(POWER_PANIC)
    case WarningType::HeatbedColdAfterPP:
        return ErrCode::CONNECT_POWER_PANIC_COLD_BED;
#endif
#if ENABLED(CALIBRATION_GCODE)
    case WarningType::NozzleDoesNotHaveRoundSection:
        return ErrCode::CONNECT_NOZZLE_DOES_NOT_HAVE_ROUND_SECTION;
#endif
    case WarningType::NotDownloaded:
        return ErrCode::CONNECT_NOT_DOWNLOADED;
    case WarningType::BuddyMCUMaxTemp:
        return ErrCode::CONNECT_BUDDY_MCU_MAX_TEMP;
#if HAS_ILI9488_DISPLAY()
    case WarningType::DisplayProblemDetected:
        return ErrCode::ERR_ELECTRO_DISPLAY_PROBLEM_DETECTED;
#endif
#if HAS_DWARF()
    case WarningType::DwarfMCUMaxTemp:
        return ErrCode::CONNECT_DWARF_MCU_MAX_TEMP;
#endif
#if HAS_REMOTE_BED()
    case WarningType::BedMCUMaxTemp:
        // TODO Rename this from "modular bed" to just "bed" in Prusa error codes.
        return ErrCode::CONNECT_MOD_BED_MCU_MAX_TEMP;
#endif
    case WarningType::ProbingFailed:
        return ErrCode::CONNECT_PROBING_FAILED;
    case WarningType::FilamentSensorStuckHelp:
        return ErrCode::ERR_MECHANICAL_FILAMENT_SENSOR_STUCK_HELP;
#if HAS_MMU2()
    case WarningType::FilamentSensorStuckHelpMMU:
        return ErrCode::ERR_MECHANICAL_FILAMENT_SENSOR_STUCK_HELP_MMU;
    case WarningType::MaintenanceWarningFails:
        return ErrCode::ERR_MECHANICAL_MAINTENANCE_WARNING_FAILS;
    case WarningType::MaintenanceWarningChanges:
        return ErrCode::ERR_MECHANICAL_MAINTENANCE_WARNING_CHANGES;
#endif
    case WarningType::FilamentSensorsDisabled:
        return ErrCode::ERR_MECHANICAL_FILAMENT_SENSORS_DISABLED;
#if _DEBUG
    case WarningType::SteppersTimeout:
        return ErrCode::CONNECT_STEPPERS_TIMEOUT;
#endif
#if XL_ENCLOSURE_SUPPORT()
    case WarningType::EnclosureFanError:
        return ErrCode::CONNECT_ENCLOSURE_FAN_ERROR;
#endif
#if HAS_CHAMBER_FILTRATION_API()
    case WarningType::EnclosureFilterExpirWarning:
        return ErrCode::CONNECT_ENCLOSURE_FILTER_EXPIRATION_WARNING;
    case WarningType::EnclosureFilterExpiration:
        return ErrCode::CONNECT_ENCLOSURE_FILTER_EXPIRATION;
#endif

#if ENABLED(DETECT_PRINT_SHEET)
    case WarningType::SteelSheetNotDetected:
        return ErrCode::ERR_MECHANICAL_STEEL_SHEET_NOT_DETECTED;
#endif

    case WarningType::GcodeCorruption:
        return ErrCode::ERR_SYSTEM_GCODE_CORRUPTION;
    case WarningType::GcodeCropped:
        return ErrCode::ERR_SYSTEM_GCODE_CROPPED;

    case WarningType::MetricsConfigChangePrompt:
        return ErrCode::ERR_CONNECT_GCODE_METRICS_CONFIG_CHANGE;
    case WarningType::AccelerometerCommunicationFailed:
        return ErrCode::ERR_ELECTRO_ACCELEROMETER_COMMUNICATION_FAILED;
    case WarningType::FilamentLoadingTimeout:
        return ErrCode::CONNECT_FILAMENT_LOADING_TIMEOUT;

#if HAS_EMERGENCY_STOP()
    case WarningType::DoorOpen:
        return ErrCode::ERR_MECHANICAL_DOOR_OPEN;
#endif
#if HAS_CHAMBER_API()
    case WarningType::FailedToReachChamberTemperature:
        return ErrCode::ERR_TEMPERATURE_CHAMBER_FAILED_TO_REACH_TEMP;
#endif

#if HAS_UNEVEN_BED_PROMPT()
    case WarningType::BedUnevenAlignmentPrompt:
        return ErrCode::ERR_MECHANICAL_UNEVEN_BED_ALIGN_PROMPT;
#endif
#if HAS_CHAMBER_API()
    case WarningType::ChamberOverheatingTemperature:
        return ErrCode::ERR_TEMPERATURE_CHAMBER_OVERHEATING_TEMP;
    case WarningType::ChamberCriticalTemperature:
        return ErrCode::ERR_TEMPERATURE_CHAMBER_CRITICAL_TEMP;
#endif

#if XBUDDY_EXTENSION_VARIANT_STANDARD() || XL_ENCLOSURE_SUPPORT()
    case WarningType::ChamberFiltrationFanError:
        return ErrCode::CONNECT_CHAMBER_FILTRATION_FAN_ERROR;
#endif

#if XBUDDY_EXTENSION_VARIANT_STANDARD()
    case WarningType::ChamberCoolingFanError:
        return ErrCode::CONNECT_CHAMBER_COOLING_FAN_ERROR;
#endif

#if HAS_CHAMBER_VENTS()
    case WarningType::OpenChamberVents:
        return ErrCode::CONNECT_OPEN_CHAMBER_VENTS;
    case WarningType::CloseChamberVents:
        return ErrCode::CONNECT_CLOSE_CHAMBER_VENTS;
#endif

#if HAS_CEILING_CLEARANCE()
    case WarningType::CeilingClearanceViolation:
        return ErrCode::ERR_MECHANICAL_CEILING_CLEARANCE_VIOLATION;
#endif

#if HAS_PRECISE_HOMING_COREXY()
    case WarningType::HomingCalibrationNeeded:
        return ErrCode::ERR_MECHANICAL_HOMING_CALIBRATION_NEEDED;

    case WarningType::HomingRefinementFailed:
        return ErrCode::ERR_MECHANICAL_PRECISE_REFINEMENT_FAILED;

    case WarningType::HomingCalibrationFromMenuNeeded:
        return ErrCode::ERR_MECHANICAL_HOMING_CALIBRATION_FROM_MENU_NEEDED;
#endif

#if HAS_SELFTEST()
    case WarningType::SelftestNotSuccessfullyCompleted:
        return ErrCode::CONNECT_UNFINISHED_SELFTEST;
#endif

    case WarningType::_cnt:
        // Fallthrough to unreachable
        break;
    }

    assert(false);
    return ErrCode::ERR_UNDEF;
}

} // namespace printer_state
