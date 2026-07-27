#include "marlin_printer.hpp"

#include <client_response.hpp>
#include <common/sys.hpp>
#include <state/printer_state.hpp>

#include <algorithm>
#include <cassert>

using printer_state::DeviceState;
using printer_state::get_state;
using std::nullopt;

namespace connect_client {

bool MarlinPrinter::job_control(JobControl control) {
    // Renew was presumably called before short.
    DeviceState state = get_state(false);

    switch (control) {
    case JobControl::Pause:
        if (state == DeviceState::Printing) {
            marlin_client::print_pause();
            return true;
        }
        return false;
    case JobControl::Resume:
        if (state == DeviceState::Paused) {
            marlin_client::print_resume();
            return true;
        }
        return false;
    case JobControl::Stop:
        if (state == DeviceState::Paused || state == DeviceState::Printing || state == DeviceState::Attention) {
            marlin_client::print_abort();
            return true;
        }
        return false;
    }
    assert(0);
    return false;
}

bool MarlinPrinter::set_ready(bool ready) {
    // Just wrapping the static method into the virtual one...
    return set_printer_ready(ready);
}

bool MarlinPrinter::set_idle() {
    const auto state = printer_state::get_state(false);
    if (state == printer_state::DeviceState::Finished || state == printer_state::DeviceState::Stopped) {
        marlin_client::print_exit();
        return true;
    }
    return false;
}

bool MarlinPrinter::is_printing() const {
    return marlin_client::is_printing();
}

bool MarlinPrinter::is_in_error() const {
    // This is true in redscreens, bluescreens and similar. These don't even
    // initialize a MarlinPrinter but ErrorPrinter.
    return false;
}

bool MarlinPrinter::is_idle() const {
    return marlin_client::is_idle();
}

bool MarlinPrinter::is_printer_ready() {
    // The value is brought down (maybe with some delay) when we start printing
    // or something like that. Therefore it is enough to just read the flag.
    return ready;
}

bool MarlinPrinter::set_printer_ready(bool ready) {
    if (ready && !printer_state::remote_print_ready(false)) {
        return false;
    }

    MarlinPrinter::ready = ready;
    return true;
}

void MarlinPrinter::reset_printer() {
    sys_reset();
}

const char *MarlinPrinter::dialog_action(printer_state::DialogId dialog_id, Response response) {
    const fsm::States fsm_states = marlin_vars().get_fsm_states();
    const std::optional<fsm::States::Top> top = fsm_states.get_top();

    // We always send dialog from the top FSM, so we can
    // just check the dialog_id and if it is the same
    // we know it is for the top one
    if (!top) {
        return "No buttons";
    }

    if (fsm_states.get_state_id() != dialog_id) {
        return "Invalid dialog id";
    }

    const PhaseResponses &valid_responses = ClientResponses::get_fsm_responses(top->fsm_type, top->data.GetPhase());
    if (std::find(valid_responses.begin(), valid_responses.end(), response) == valid_responses.end()) {
        return "Invalid button for dialog";
    }

    marlin_client::FSM_encoded_response(EncodedFSMResponse {
        .response = FSMResponseVariant::make(response),
        .fsm_and_phase = FSMAndPhase(top->fsm_type, top->data.GetPhase()),
    });
    return nullptr;
}

std::optional<MarlinPrinter::FinishedJobResult> MarlinPrinter::get_prior_job_result(uint16_t job_id) const {
    auto result = marlin_vars().get_job_result(job_id);
    if (!result.has_value()) {
        return nullopt;
    }

    switch (result.value()) {
    case marlin_vars_t::JobInfo::JobResult::aborted:
        return FinishedJobResult::FIN_STOPPED;
    case marlin_vars_t::JobInfo::JobResult::finished:
        return FinishedJobResult::FIN_OK;
    }

    return nullopt;
}

} // namespace connect_client
