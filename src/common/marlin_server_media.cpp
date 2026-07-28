#include "marlin_server_internal.hpp"

using namespace ExtUI;

LOG_COMPONENT_REF(MarlinServer);

namespace marlin_server {
using namespace internal;

void print_start(const char *filename, const GCodeReaderPosition &resume_pos, marlin_server::PreviewSkipIfAble skip_preview) {
#if HAS_SELFTEST()
    if (SelftestInstance().IsInProgress()) {
        return;
    }
#endif
    if (filename == nullptr) {
        return;
    }

    // Clear warnings before print, like heaters disabled after 30 minutes.
    clear_warning(WarningType::HeatersTimeout);

    switch (server.print_state) {

        // handle preview / reprint
    case State::Finished:
    case State::Aborted:
        // correctly end previous print
        finalize_print(server.print_state == State::Finished);
        if (fsm_states.is_active(ClientFSM::Printing)) {
            // exit from print screen, if opened
            fsm_destroy(ClientFSM::Printing);
        }
        break;

    case State::Idle:
    case State::PrintPreviewInit:
    case State::PrintPreviewImage:
    case State::PrintPreviewConfirmed:
    case State::PrintPreviewQuestions:
#if HAS_TOOLCHANGER() || HAS_MMU2()
    case State::PrintPreviewToolsMapping:
#endif
        // These are acceptable states from which we can start the print -> continue executing the function
        break;

    default:
        // Do not start the print from other states
        return;
    }

    print_state = {};

    if (filename) {
        // Avoid possible deadlocks by disabling a gcode scan, if there's any.
        //
        // The deadlock could happen if:
        // * We started to download a file.
        // * We start to show the preview, but it's not yet downloaded enough
        //   to show on screen, in which case the scan _waits_ for it to become
        //   downloaded enough.
        // * Connect gets a command to start a print, forwarding it to us here.
        // * We would have to wait of that one to finish below (the async job thing).
        // * And we would be blocking Connect by not answering, therefore it
        //   would not be updating the file downloaded range... not unblocking
        //   the scan.
        gcode_info_scan::cancel_scan();
        // We need a copy of the sfn as well because get_LFN needs the address mutable :/
        std::array<char, FILE_PATH_BUFFER_LEN> filepath_sfn;
        strlcpy(filepath_sfn.data(), filename, filepath_sfn.size());

        std::array<char, FILE_NAME_BUFFER_LEN> filename_lfn;

        // Do this in the async job thread to prevent blocking Marlin on I/O and possibly causing a watchdog reset
        AsyncJob async_job;
        async_job.issue([&](AsyncJobExecutionControl &) {
            get_LFN(filename_lfn.data(), filename_lfn.size(), filepath_sfn.data());
        });
        while (async_job.is_active()) {
            ::idle(true);
        }

        // Update marlin vars
        {
            MarlinVarsLockGuard lock;

            // update media_SFN_path
            strlcpy(marlin_vars().media_SFN_path.get_modifiable_ptr(lock), filepath_sfn.data(), marlin_vars().media_SFN_path.max_length());

            // set media_LFN
            strlcpy(marlin_vars().media_LFN.get_modifiable_ptr(lock), filename_lfn.data(), marlin_vars().media_LFN.max_length());
        }

        // Update GCodeInfo
        GCodeInfo::getInstance().set_gcode_file(filepath_sfn.data(), filename_lfn.data());
    }

    set_media_position(resume_pos.offset);
    print_state.media_restore_info = resume_pos.restore_info;
    media_prefetch_start();

    server.print_state = State::WaitGui;

    PrintPreview::Instance().set_skip_if_able(skip_preview);
}

void media_prefetch_start() {
    print_state.file_open_reported = false;
    media_prefetch.start(marlin_vars().media_SFN_path.get_ptr(), GCodeReaderPosition { stream_restore_info(), media_position() });
    media_prefetch.issue_fetch();
}

void internal::schedule_media_retry() {
    const auto backoff_time = print_state.recover_media_error_backoff.fail();
    print_state.recover_media_error_at = ticks_s() + backoff_time;
    log_info(MarlinServer, "Scheduled media retry at %" PRIu32 ", backoff %" PRIu32, *print_state.recover_media_error_at, backoff_time);
}

void internal::clear_media_error() {
    if (!print_state.recover_media_error_backoff.get().has_value()) {
        return;
    }

    print_state.recover_media_error_at.reset();
    print_state.recover_media_error_backoff.reset();

    clear_warning(WarningType::USBFlashDiskError);
    clear_warning(WarningType::GcodeCorruption);
    clear_warning(WarningType::NotDownloaded);
}

std::optional<WarningType> internal::prefetch_status_to_warning(MediaPrefetchManager::Status status) {
    using Status = MediaPrefetchManager::Status;

    switch (status) {

    case Status::usb_error:
        return WarningType::USBFlashDiskError;

    case Status::corruption:
        return WarningType::GcodeCorruption;

    case Status::not_downloaded:
        return WarningType::NotDownloaded;

    case Status::ok:
    case Status::end_of_buffer:
    case Status::end_of_file:
        return std::nullopt;
    }

    BUDDY_UNREACHABLE();
}

void media_print_loop() {
    /// Size of the gcode queue
    METRIC_DEF(metric_gcode_queue_size, "gcd_que_sz", METRIC_VALUE_INTEGER, 100, METRIC_ENABLED);
    metric_record_integer(&metric_gcode_queue_size, queue.length);

    while (queue.length < MEDIA_FETCH_GCODE_QUEUE_FILL_TARGET) {
        MediaPrefetchManager::ReadResult data;
        using Status = MediaPrefetchManager::Status;
        const auto status = media_prefetch.read_command(data);
        const auto metrics = media_prefetch.get_metrics();

        /// Status of the last media_prefetch.read_command. 0 = ok, 1 = end of file, other = error (means that we're stalling)
        METRIC_DEF(metric_fetch_status, "ftch_status", METRIC_VALUE_INTEGER, 100, METRIC_ENABLED);
        metric_record_integer(&metric_fetch_status, static_cast<int>(status.status));

        /// Status at the end of the buffer - for early error indication
        METRIC_DEF(metric_fetch_tail_status, "ftch_tstatus", METRIC_VALUE_INTEGER, 100, METRIC_ENABLED);
        metric_record_integer(&metric_fetch_tail_status, static_cast<int>(metrics.tail_status));

        /// Occupancy of the media prefetch buffer, in percent of the buffer size
        METRIC_DEF(metric_prefetch_buffer_occupancy, "ftch_occ", METRIC_VALUE_INTEGER, 100, METRIC_ENABLED);
        metric_record_integer(&metric_prefetch_buffer_occupancy, metrics.buffer_occupancy_percent);

        /// Number of commands in the prefetch buffer
        METRIC_DEF(metric_prefetch_buffer_commands, "ftch_cmds", METRIC_VALUE_INTEGER, 100, METRIC_ENABLED);
        metric_record_integer(&metric_prefetch_buffer_commands, metrics.commands_in_buffer);

        if (!print_state.file_open_reported && metrics.stream_size_estimate) {
            print_state.file_open_reported = true;

            // Do not remove, needed for 3rd party tools such as octoprint to get status about the gcode file being opened
            SERIAL_ECHOLNPAIR(MSG_SD_FILE_OPENED, marlin_vars().media_SFN_path.get_ptr(), " Size:", metrics.stream_size_estimate);
        }

        switch (status.status) {

        case Status::ok:
            if (print_state.skip_gcode) {
                print_state.skip_gcode = false;
                continue;
            }

            clear_media_error();

            print_state.media_restore_info = data.replay_pos.restore_info;
            queue.sdpos = data.replay_pos.offset;
            if (!queue.enqueue_one(data.gcode.data(), false)) {
                bsod("enqueue_one failed");
            }
            log_debug(MarlinServer, "Enqueue: %" PRIu32 " %s", data.replay_pos.offset, data.gcode.data());

            // Issue another fetch if the media prefetch buffer is running empty
            if (metrics.buffer_occupancy_percent < 60 && metrics.tail_status != Status::end_of_file) {
                media_prefetch.issue_fetch();
            }

            if (data.cropped) {
                set_warning(WarningType::GcodeCropped);
            }

            break;

        case Status::end_of_file:
            clear_media_error();

            // We've read everything -> start finishing up the print, return from this function completely
            server.print_state = State::Finishing_WaitIdle;
            return;

        case Status::end_of_buffer:
            // Defnitely issue a prefetch here
            media_prefetch.issue_fetch();
            return;

        case Status::usb_error:
        case Status::corruption:
        case Status::not_downloaded: {
            if (status.fetch_active) {
                // There's still a fetch running, this isn't completely final ‒ the
                // fetch itself can recover from the error (and sometimes it does,
                // but the actual recovery takes time). Wait for the final verdict.
                return;
            }

            set_warning(*prefetch_status_to_warning(status.status));
            schedule_media_retry();
            print_pause();
            return;
        }
        }
    }
}

/// Update SFN filepath from LFN.
/// The SFN of the file could have been changed by the user during the pause (for example by re-uploading a damaged file).
/// BFW-5775
void internal::update_sfn() {
    // Put into one struct so that we can squeeze it through a std::inplace_function capture
    struct {
        MutablePath filepath_sfn;
        const char *lfn;
        bool found = false;
    } d;

    // Copy the current SFN + LFN from marlin vars
    marlin_vars().media_SFN_path.copy_to(d.filepath_sfn.get_buffer(), d.filepath_sfn.maximum_length());
    log_info(MarlinServer, "Old SFN: %s", d.filepath_sfn.get());

    // Pop filename, leave path only
    d.filepath_sfn.pop();

    // This is done on the marlin thread, so we can keep using the pointer
    d.lfn = marlin_vars().media_LFN.get_ptr();

    // Do this in the async job thread to prevent blocking Marlin on I/O and possibly causing a watchdog reset
    AsyncJob async_job;
    async_job.issue([&d](AsyncJobExecutionControl &) {
        DIR *dir = opendir(d.filepath_sfn.get());
        if (!dir) {
            return;
        }
        ScopeGuard dir_guard([&] { closedir(dir); });

        struct dirent *ent;
        while ((ent = readdir(dir))) {
            if ((strcasecmp(ent->d_name, d.lfn) == 0) || (strcasecmp(ent->lfn, d.lfn) == 0)) {
                break;
            }
        }

        if (!ent) {
            return;
        }

        d.found = true;
        d.filepath_sfn.push(ent->d_name);
    });

    while (async_job.is_active()) {
        ::idle(true);
    }

    // We haven't found the file -> do nothing. Fail open is sorted out later in the code.
    if (!d.found) {
        return;
    }

    // Update the relevant variables
    log_info(MarlinServer, "New SFN: %s", d.filepath_sfn.get());
    marlin_vars().media_SFN_path.set(d.filepath_sfn.get());
    GCodeInfo::getInstance().set_gcode_file(d.filepath_sfn.get(), d.lfn);
}

void print_resume(void) {
    if (server.print_state == State::Paused) {
        update_sfn();

        if (server.print_is_serial) {
            server.print_state = State::Resuming_Begin;
        } else {
            server.print_state = State::Resuming_BufferData;
            media_prefetch_start();
        }

        // pause queuing commands from serial, until resume sequence is finished.
        GCodeQueue::pause_serial_commands = true;

    } else if (is_resuming_state(server.print_state)) {
        // Do nothing

    } else if (is_pausing_state(server.print_state)) {
        print_state.resume_pending = true;

#if ENABLED(POWER_PANIC)
    } else if (server.print_state == State::PowerPanic_AwaitingResume) {
        power_panic::resume_continue();
        server.print_state = State::PowerPanic_Resume;
#endif
    } else {
        print_start(nullptr, GCodeReaderPosition(), marlin_server::PreviewSkipIfAble::all);
    }
}

void internal::try_recover_from_media_error() {
    if (server.print_state == State::Printing) {
        // If we're printing, simply try issuing a fetch to make sure everything's fine
        media_prefetch.issue_fetch();

    } else if (server.print_state == State::Paused && print_state.recover_media_error_backoff.get().has_value()) {
        // Do NOT reset - will be reset if the resume is successful
        // print_state.recover_media_error_backoff.get().reset();
        server.print_state = State::MediaErrorRecovery_BufferData;
        update_sfn();
        media_prefetch_start();

    } else {
        // We cannot attempt recovery right now, but recover_media_error_backoff should make us retry sometime later
    }
}

bool internal::process_media_recovery_state(State state) {
    switch (state) {
    case State::Resuming_BufferData:
    case State::MediaErrorRecovery_BufferData: {
        const auto metrics = media_prefetch.get_metrics();
        if (metrics.is_fetching) {
            // Wait till the media prefetch finishes
            break;
        }

        using Status = MediaPrefetchManager::Status;

        switch (metrics.tail_status) {

        case Status::ok:
        case Status::end_of_file:
        case Status::end_of_buffer:
            // The media_prefetch feched something successfully, let's continue with resuming!
            server.print_state = State::Resuming_Begin;
            clear_media_error();
            break;

        case Status::usb_error:
        case Status::corruption:
        case Status::not_downloaded: {
            // Still failing.
            schedule_media_retry();
            media_prefetch.stop();

            // Show a warning, but only if the unpause was requested by the user explicitly
            // Do not spam warnings when we're doing background periodic media error recoveries
            if (server.print_state != State::MediaErrorRecovery_BufferData) {
                set_warning(*prefetch_status_to_warning(metrics.tail_status));
            }

            // Go back to Paused (the only state where we could have come from).
            server.print_state = State::Paused;
        }
        }
        break;
    }

    default:
        return false;
    }
    return true;
}

} // namespace marlin_server
