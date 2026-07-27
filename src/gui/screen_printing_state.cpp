// screen_printing.cpp
#include "screen_printing.hpp"
#include "marlin_client.hpp"
#include <marlin_stubs/skippable_gcode.hpp>
#include "print_utils.hpp"
#include <buddy/ffconf.h>
#include "ScreenHandler.hpp"
#include <ctime>
#include "../lang/format_print_will_end.hpp"
#include "utility_extensions.hpp"
#include "odometer.hpp"
#include "liveadjust_z.hpp"
#include "screen_move_z.hpp"
#include "metric.h"
#include "screen_menu_tune.hpp"
#include <guiconfig/guiconfig.h>
#include <img_resources.hpp>
#include <option/has_human_interactions.h>
#include <option/has_loadcell.h>
#include <option/has_mmu2.h>
#include <option/has_toolchanger.h>
#include <buddy/unreachable.hpp>
#include <utils/string_builder.hpp>

#if HAS_MMU2()
    #include <feature/prusa/MMU2/mmu2_mk4.h>
    #include <window_msgbox.hpp>
    #include <mmu2/maintenance.hpp>
#endif

#include <feature/print_status_message/print_status_message_mgr.hpp>
#include <feature/print_status_message/print_status_message_formatter_buddy.hpp>

#include "Marlin/src/module/motion.h"

#if ENABLED(CRASH_RECOVERY)
    #include "../Marlin/src/feature/prusa/crash_recovery.hpp"
#endif

#include <option/buddy_enable_connect.h>
#if BUDDY_ENABLE_CONNECT()
    #include <connect/connect.hpp>
    #include <connect/marlin_printer.hpp>
#endif

using namespace marlin_server;

printing_state_t screen_printing_data_t::GetState() const {
    return state__readonly__use_change_print_state;
}

static bool is_waiting_for_connect_set_ready() {
#if BUDDY_ENABLE_CONNECT()
    return connect_client::is_connect_registered() && !connect_client::MarlinPrinter::is_printer_ready();
#else
    return false;
#endif
}

void screen_printing_data_t::tuneAction() {
    if (buttons[std::to_underlying(BtnSocket::Left)].IsShadowed()) {
        return;
    }
    switch (GetState()) {
    case printing_state_t::PRINTING:
    case printing_state_t::SKIPPABLE_OPERATION:
    case printing_state_t::PAUSED:
        Screens::Access()->Open(ScreenFactory::Screen<ScreenMenuTune>);
        break;
    case printing_state_t::PRINTED:
        if (is_waiting_for_connect_set_ready()) {
#if BUDDY_ENABLE_CONNECT()
            connect_client::MarlinPrinter::set_printer_ready(true);
#endif
            set_tune_icon_and_label(); // Disable Set Ready button
        }
    default:
        break;
    }
}

void screen_printing_data_t::pauseAction() {
    if (buttons[std::to_underlying(BtnSocket::Middle)].IsShadowed()) {
        return;
    }
    switch (GetState()) {
    case printing_state_t::PRINTING:
        marlin_client::print_pause();
        change_print_state();
        break;
    case printing_state_t::SKIPPABLE_OPERATION:
        skippable_gcode().request_skip();
        change_print_state();
        break;
    case printing_state_t::PAUSED:
        marlin_client::print_resume();
        change_print_state();
        break;
    case printing_state_t::STOPPED:
    case printing_state_t::PRINTED:
        screen_printing_reprint();
        change_print_state();
        break;
    default:
        break;
    }
}

void screen_printing_data_t::stopAction() {
    if (buttons[std::to_underlying(BtnSocket::Right)].IsShadowed()) {
        return;
    }
    switch (GetState()) {
    case printing_state_t::STOPPED:
    case printing_state_t::PRINTED:
        marlin_client::print_exit();
        return;
    case printing_state_t::PAUSING:
    case printing_state_t::RESUMING:
        return;
    default: {
        if (MsgBoxWarning(_("Are you sure to stop this printing?"), Responses_YesNo, 1)
            == Response::Yes) {
            stop_pressed = true;
            waiting_for_abort = true;
            marlin_client::print_abort();
            change_print_state();
        } else {
            return;
        }
    }
    }
}

void screen_printing_data_t::screen_printing_reprint() {
    print_begin(GCodeInfo::getInstance().GetGcodeFilepath(), marlin_server::PreviewSkipIfAble::preview);
    screen_printing_data_t::updateTimes(); // reinit, but should be already set correctly
    SetButtonIconAndLabel(BtnSocket::Middle, BtnRes::Stop, LabelRes::Stop);
    header.SetText(_(caption));
}

void screen_printing_data_t::set_pause_icon_and_label() {
    switch (GetState()) {
    case printing_state_t::INITIAL:
    case printing_state_t::PRINTING:
        EnableButton(BtnSocket::Middle);
        SetButtonIconAndLabel(BtnSocket::Middle, BtnRes::Pause, LabelRes::Pause);
        break;
    case printing_state_t::SKIPPABLE_OPERATION:
        EnableButton(BtnSocket::Middle);
        SetButtonIconAndLabel(BtnSocket::Middle, BtnRes::Resume, LabelRes::Skip);
        break;
    case printing_state_t::PAUSING:
        DisableButton(BtnSocket::Middle);
        SetButtonIconAndLabel(BtnSocket::Middle, BtnRes::Pause, LabelRes::Pausing);
        break;
    case printing_state_t::PAUSED:
        EnableButton(BtnSocket::Middle);
        SetButtonIconAndLabel(BtnSocket::Middle, BtnRes::Resume, LabelRes::Resume);
        if (!marlin_vars().media_inserted) {
            DisableButton(BtnSocket::Middle);
        }
        break;
    case printing_state_t::RESUMING:
        DisableButton(BtnSocket::Middle);
        SetButtonIconAndLabel(BtnSocket::Middle, BtnRes::Resume, LabelRes::Resuming);
        break;
    case printing_state_t::REHEATING:
        DisableButton(BtnSocket::Middle);
        SetButtonIconAndLabel(BtnSocket::Middle, BtnRes::Resume, LabelRes::Reheating);
        break;
    case printing_state_t::STOPPED:
    case printing_state_t::PRINTED:
        EnableButton(BtnSocket::Middle);
        SetButtonIconAndLabel(BtnSocket::Middle, BtnRes::Reprint, LabelRes::Reprint);
        break;
    case printing_state_t::ABORTING:
        DisableButton(BtnSocket::Middle);
        break;
    }

    switch (GetState()) {
    case printing_state_t::PAUSING:
        header.SetText(_("PAUSING ..."));
        break;
    case printing_state_t::PAUSED:
        header.SetText(_("PAUSED"));
        break;
    case printing_state_t::ABORTING:
        header.SetText(_("ABORTING ..."));
        break;
    case printing_state_t::STOPPED:
        header.SetText(_("STOPPED"));
        break;
    case printing_state_t::PRINTED:
        header.SetText(_("FINISHED"));
        break;
    default: // else printing
        header.SetText(_(caption));
        break;
    }
}

void screen_printing_data_t::set_tune_icon_and_label() {
    SetButtonIconAndLabel(BtnSocket::Left, BtnRes::Settings, LabelRes::Settings);

    switch (GetState()) {
    case printing_state_t::PRINTING:
    case printing_state_t::SKIPPABLE_OPERATION:
    case printing_state_t::PAUSED:
        EnableButton(BtnSocket::Left);
        break;
    case printing_state_t::ABORTING:
        DisableButton(BtnSocket::Left);
        break;
    case printing_state_t::PRINTED:
        if (is_waiting_for_connect_set_ready()) {
            EnableButton(BtnSocket::Left);
            SetButtonIconAndLabel(BtnSocket::Left, BtnRes::SetReady, LabelRes::SetReady);
        } else {
            DisableButton(BtnSocket::Left);
        }
        break;
    default:
        DisableButton(BtnSocket::Left);
        break;
    }
}

void screen_printing_data_t::set_stop_icon_and_label() {
    switch (GetState()) {
    case printing_state_t::STOPPED:
    case printing_state_t::PRINTED:
        EnableButton(BtnSocket::Right);
        SetButtonIconAndLabel(BtnSocket::Right, BtnRes::Home, LabelRes::Home);
        break;
    case printing_state_t::PAUSING:
    case printing_state_t::RESUMING:
        DisableButton(BtnSocket::Right);
        SetButtonIconAndLabel(BtnSocket::Right, BtnRes::Stop, LabelRes::Stop);
        break;
    case printing_state_t::REHEATING:
        EnableButton(BtnSocket::Right);
        SetButtonIconAndLabel(BtnSocket::Right, BtnRes::Stop, LabelRes::Stop);
        break;
    case printing_state_t::ABORTING:
        DisableButton(BtnSocket::Right);
        break;
    default:
        EnableButton(BtnSocket::Right);
        SetButtonIconAndLabel(BtnSocket::Right, BtnRes::Stop, LabelRes::Stop);
        break;
    }
}

void screen_printing_data_t::change_print_state() {
    printing_state_t st = [&] {
        switch (marlin_vars().print_state) {
        case State::Idle:
        case State::WaitGui:
        case State::PrintPreviewInit:
        case State::PrintPreviewImage:
        case State::PrintPreviewConfirmed:
        case State::PrintPreviewQuestions:
#if HAS_TOOLCHANGER() || HAS_MMU2()
        case State::PrintPreviewToolsMapping:
#endif
        case State::PrintInit:
            return printing_state_t::INITIAL;
        case State::Printing:
            return printing_state_t::PRINTING;
        case State::PowerPanic_AwaitingResume:
        case State::MediaErrorRecovery_BufferData:
        case State::Paused:
            // stop_pressed = false;
            return printing_state_t::PAUSED;
        case State::Pausing_Begin:
        case State::Pausing_Failed_Code:
        case State::Pausing_WaitIdle:
        case State::Pausing_ParkHead:
// When print is paused, progress screen needs to reinit it's thumbnail file handler
// because USB removal error crashes file handler access. Progress screen should not be enabled during pause -> reinit on EVERY pause
#if HAS_LARGE_DISPLAY()
            print_progress.Pause();
#endif
            return printing_state_t::PAUSING;
        case State::Resuming_Reheating:
            stop_pressed = false;
            return printing_state_t::REHEATING;
        case State::Resuming_BufferData:
        case State::Resuming_Begin:
        case State::Resuming_UnparkHead_XY:
        case State::Resuming_UnparkHead_ZE:
        case State::CrashRecovery_Begin:
        case State::CrashRecovery_Retracting:
        case State::CrashRecovery_Lifting:
        case State::CrashRecovery_ToolchangePowerPanic:
        case State::CrashRecovery_XY_Measure:
#if HAS_TOOLCHANGER()
        case State::CrashRecovery_Tool_Pickup:
#endif
        case State::CrashRecovery_XY_HOME:
        case State::CrashRecovery_HOMEFAIL:
        case State::CrashRecovery_Axis_NOK:
        case State::CrashRecovery_Repeated_Crash:
        case State::PowerPanic_Resume:
            stop_pressed = false;
#if HAS_LARGE_DISPLAY()
            print_progress.Resume();
#endif
            return printing_state_t::RESUMING;
        case State::Aborting_Begin:
        case State::Aborting_WaitIdle:
        case State::Aborting_UnloadFilament:
        case State::Aborting_ParkHead:
        case State::Aborting_Preview:
            stop_pressed = false;
            return printing_state_t::ABORTING;
        case State::Finishing_WaitIdle:
        case State::Finishing_UnloadFilament:
        case State::Finishing_ParkHead:
            return printing_state_t::PRINTING;
        case State::Aborted:
            stop_pressed = false;
            return printing_state_t::STOPPED;
        case State::Finished:
        case State::Exit:
            return printing_state_t::PRINTED;
        case State::PowerPanic_acFault:
        case State::SerialPrintInit:
            // It is questionable in this case if it is really printing at this
            // point. But at least in case of power panic, it _can_ happen. It
            // won't show on the screen, but we don't want to BSOD.
            //
            // In that case, the display is turned off, but the GUI thread
            // still runs (even though it doesn't show anywhere).
            return printing_state_t::PRINTING;
        }
        BUDDY_UNREACHABLE();
    }();
    if (stop_pressed) {
        st = printing_state_t::ABORTING;
    }
    if (skippable_gcode().is_running()) {
        st = printing_state_t::SKIPPABLE_OPERATION;
    }
    if (state__readonly__use_change_print_state != st) {
        state__readonly__use_change_print_state = st;
        set_pause_icon_and_label();
        set_tune_icon_and_label();
        set_stop_icon_and_label();
    }
    if (st == printing_state_t::PRINTED || st == printing_state_t::STOPPED || st == printing_state_t::PAUSED) {
        Odometer_s::instance().force_to_eeprom();
    }
}
