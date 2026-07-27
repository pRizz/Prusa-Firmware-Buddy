#include "render.hpp"
#include "render_internal.hpp"
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

namespace connect_client {

namespace {

    std::optional<off_t> child_size(const char *base_path, const char *child_name) {
        char path_buf[FILE_PATH_BUFFER_LEN];
        int formatted = snprintf(path_buf, sizeof(path_buf), "%s/%s", base_path, child_name);
        // Name didn't fit. That, in theory, should not happen, but better safe than sorry...
        if (formatted >= FILE_NAME_BUFFER_LEN) {
            return {};
        }
        struct stat st = {};
        if (stat(path_buf, &st) == 0) {
            return st.st_size;
        } else {
            return {};
        }
    }

    enum class MetaFilter {
        Ignore,
        String,
        Int,
        Float,
        Bool,
    };

    struct MetaRecord {
        const char *name;
        MetaFilter filter;
    };

    // TODO: We probably can come up with some way of not storing the long
    // strings in here and save some flash size with maybe CRCs of the strings?
    static constexpr MetaRecord meta_records[] = {
        { "filament cost", MetaFilter::Float },
        { "filament used [mm]", MetaFilter::Float },
        { "filament used [cm3]", MetaFilter::Float },
        { "filament used [mm3]", MetaFilter::Float },
        { "filament used [m]", MetaFilter::Float },
        { "bed_temperature", MetaFilter::Int },
        { "brim_width", MetaFilter::Int },
        { "layer_height", MetaFilter::Float },
        { "temperature", MetaFilter::Int },
        // Note: These two should actually be Bools. But it seems the server is
        // currently expecting 0/1, the gcode also contains 0/1, so we adhere
        // to the rest because of compatibility.
        { "ironing", MetaFilter::Int },
        { "support_material", MetaFilter::Int },
        { "max_layer_z", MetaFilter::Float },
        { "estimated_print_time", MetaFilter::Int },
        { "total filament used for wipe tower [g]", MetaFilter::Float },

        // Blacklist of names not to send.
        // These really aren't metadata headers in common gcode files as far as
        // we know. But these are some additional fields we include in the data
        // object of the FILE_INFO event, so we protect against a collision by
        // malicious or confused gcode file.
        { "preview", MetaFilter::Ignore },
        { "size", MetaFilter::Ignore },
        { "m_timestamp", MetaFilter::Ignore },
        { "read_only", MetaFilter::Ignore },
        { "display_name", MetaFilter::Ignore },
        { "type", MetaFilter::Ignore },
        { "path", MetaFilter::Ignore },
    };

    MetaFilter meta_filter(const char *name) {
        for (size_t i = 0; i < sizeof meta_records / sizeof *meta_records; i++) {
            if (strcmp(name, meta_records[i].name) == 0) {
                return meta_records[i].filter;
            }
        }

        return MetaFilter::String;
    }
} // namespace

namespace detail {
    JsonResult render_msg(size_t, JsonOutput &, const RenderState &, const Sleep &) {
        // Sleep is handled on upper layers, not through renderer.
        assert(0);
        return JsonResult::Abort;
    }

    JsonResult render_msg(size_t, JsonOutput &, const RenderState &, const ReadCommand &) {
        // Not a message to send to server
        assert(0);
        return JsonResult::Abort;
    }

} // namespace detail

tuple<JsonResult, size_t> PreviewRenderer::render(uint8_t *buffer, size_t buffer_size) {
    // base64 encodes 3 bytes to 4 ASCII chars, decoding needs to happen in multiples of this to work
    constexpr static size_t encoded_chunk_size = 4;
    constexpr static size_t decoded_chunk_size = 3;

    constexpr static const char *intro = "\"preview\":\"";
    constexpr static const char *outro = "\",";
    constexpr static size_t intro_len = strlen(intro);
    // Ending quote and comma
    constexpr static size_t outro_len = strlen(outro);
    // Don't bother with too small buffers to make the code easier. Extra char
    // for trying out there's some preview in there.
    constexpr static size_t min_len = intro_len + outro_len + encoded_chunk_size;

    if (buffer_size < min_len) {
        // Will be retried next time with bigger buffer.
        return make_tuple(JsonResult::BufferTooSmall, 0);
    }

    size_t written = 0;
    if (!thumbnail_reader) {
        // get any thumbnail bigger than 17x17
        thumbnail_reader = gcode->stream_thumbnail_start(17, 17, IGcodeReader::ImgType::PNG, true);
        if (!thumbnail_reader) {
            // no thumbnail found in gcode, just dont send anything
            return make_tuple(JsonResult::Complete, 0);
        }
        // write intro
        memcpy(buffer, intro, intro_len);
        written += intro_len;
        buffer += intro_len;
    }

    bool write_end = false;
    while ((buffer_size - written) >= (encoded_chunk_size + 1)) { // if there is space for another chunk (and ending \0)
        // read chunk of decoded data
        uint8_t dec_chunk[decoded_chunk_size] = { 0 };
        size_t decoded_len = thumbnail_reader->read({ dec_chunk, decoded_chunk_size }).size();
        if (decoded_len != decoded_chunk_size) {
            // probably end of data, or error. Either way stop reading and send whatever was read till now.
            // if error happens while sending thumbnail, there is not much that can be done to signal that anyway.
            write_end = true;
            break;
        }
        [[maybe_unused]] size_t encoded_len;
        // note that mbedtls_base64_encode also writes ending zero, but we want to skip that
        [[maybe_unused]] auto res = mbedtls_base64_encode(buffer, encoded_chunk_size + 1, &encoded_len, dec_chunk, decoded_len);
        assert(res == 0 && encoded_len == encoded_chunk_size); // should not fail, buffer should always be big enough
        written += encoded_chunk_size;
        buffer += encoded_chunk_size;
    }

    if (write_end && (buffer_size - written) >= outro_len) {
        // This is the end!
        memcpy(buffer, outro, outro_len);
        written += outro_len;
        return make_tuple(JsonResult::Complete, written);
    }

    return make_tuple(JsonResult::Incomplete, written);
}

void GcodeMetaRenderer::reset_buffer() {
    gcode_line_buffer.line = GcodeBuffer::String();
    parsed.reset();
}

JsonResult GcodeMetaRenderer::out_str_chunk(JsonOutput &output, const GcodeBuffer::String &str) {
    auto result = output.output_str_chunk(0, str.begin, str.len());

    if (result == JsonResult::Complete && gcode_line_buffer.line_complete) {
        result = output.output(0, "\"");
    }

    if (result == JsonResult::Complete) {
        // Adjust this only if we were successful - if not, we'll retry with the same stuff.
        str_continuation = !gcode_line_buffer.line_complete;
    }

    return result;
}

tuple<JsonResult, size_t> GcodeMetaRenderer::render(uint8_t *buffer, size_t buffer_size) {
    if (first_run) {
        reset_buffer();
        if (!gcode->stream_metadata_start()) {
            return make_tuple(JsonResult::Complete, 0);
        }
        first_run = false;
    }

    size_t buffer_size_rest = buffer_size;
    // We are reusing the JsonOutput here, but not using the resume point
    // feature of it. We still need to provide the variable to it, though.
    size_t resume_point = 0;
    JsonOutput output(buffer, buffer_size_rest, resume_point);
    // The output does track how much it used. But we need to track it in the
    // whole fields resolution, including commas ‒ otherwise the code would
    // become significantly more complicated by a comma being able to overflow
    // to the next buffer of data.
    size_t pos = 0;

    // This code iterates though metadata, and only if entire  key:value, fits to output buffer, send it.
    // If just part of the string fits, skip it and try to place it into next packed.
    while (true) {
        if (gcode_line_buffer.line.is_empty()) {
            // line is empty, that indicates that last line was already processed and we need to fetch another one
            if (gcode->stream_get_line(gcode_line_buffer, IGcodeReader::Continuations::Split) != IGcodeReader::Result_t::RESULT_OK) {
                break;
            }
        }

        // Either result of putting something to the buffer, or nullopt if this line should be skipped.
        std::optional<JsonResult> result = nullopt;

        if (str_continuation) {
            // Will adjust str_continuation as needed
            result = out_str_chunk(output, gcode_line_buffer.line);
        } else {
            // Disallow terminating the value in case it's taking all the 81 chars
            // ‒ that could touch the 82th char and we don't have that one.
            // (possibility with Split continuation of reading).
            //
            // (It probably can happen only in case the line_complete == false, but
            // that would look like a fragile assumption, so basing it off the real
            // "problem").
            const bool full_size = gcode_line_buffer.line.len() == gcode_line_buffer.buffer.size();
            if (!parsed.has_value()) {
                parsed = gcode_line_buffer.line.parse_metadata(!full_size);
            }
            if (parsed->first.begin == nullptr || parsed->second.begin == nullptr) {
                reset_buffer(); // reset buffer to fetch another line
                continue;
            }

            auto filter = meta_filter(parsed->first.c_str());

            // Too large headers are only handled and allowed for strings, others
            // aren't expected to exceed 80 chars.
            if (filter != MetaFilter::String && (full_size || !gcode_line_buffer.line_complete)) {
                // Eat the rest of the header.
                bool error = false;
                while (!gcode_line_buffer.line_complete) {
                    if (gcode->stream_get_line(gcode_line_buffer, IGcodeReader::Continuations::Split) != IGcodeReader::Result_t::RESULT_OK) {
                        error = true;
                        break;
                    }
                }

                if (error) {
                    break;
                }

                filter = MetaFilter::Ignore;
            }

            switch (filter) {
            case MetaFilter::Ignore:
                // do nothing, just go o next line
                break;
            case MetaFilter::String:
                // Only the name of the field and starting "
                result = output.output(0, "\"%s\":\"", parsed->first.c_str());
                if (result == JsonResult::Complete) {
                    // Will adjust the str_continuation as needed.
                    result = out_str_chunk(output, parsed->second);
                }
                break;

            case MetaFilter::Float: {
                char *end = nullptr;
                double v = strtod(parsed->second.c_str(), &end);
                if (end != nullptr && *end != '\0') {
                    // unable to parse, skip this
                } else {
                    result = output.output_field_float_fixed(0, parsed->first.c_str(), v, 2);
                }
                break;
            }

            case MetaFilter::Int:
            case MetaFilter::Bool: {
                char *end = nullptr;
                long v = strtol(parsed->second.c_str(), &end, 10);
                if (end != nullptr && *end != '\0') {
                    // Not really an int there. Skip this line.
                } else {
                    if (filter == MetaFilter::Int) {
                        result = output.output_field_int(0, parsed->first.c_str(), v);
                    } else {
                        // The gcode encodes bools as 0/1, JSON has True and False.
                        result = output.output_field_bool(0, parsed->first.c_str(), v);
                    }
                }
                break;
            }
            }
        }

        if (!result.has_value()) {
            // no result obtained from this line -> skip it
            reset_buffer();
            continue;
        }

        if (result.value() == JsonResult::Complete && !str_continuation) {
            // Line successfully put to buffer - now put ending ","
            result = output.output(0, ",");
        }

        switch (result.value()) {
        case JsonResult::Complete:
            // Successfully put content into into the buffer. update pos, and reset buffer to go to next line
            pos = buffer_size - buffer_size_rest;
            reset_buffer();
            break;
        case JsonResult::Abort:
            // We use only the primitive output functions and they are not
            // capable of returning Abort.
            assert(0);
            break;
        case JsonResult::Incomplete:
        case JsonResult::BufferTooSmall:
            // The primitive functions get "confused" a little bit by always
            // using the resume point of 0 and reports BufferTooSmall. But
            // that's fine, we don't really need to make that distinction here.
            return make_tuple(JsonResult::Incomplete, pos);
        }
    }

    return make_tuple(JsonResult::Complete, pos);
}

DirRenderer::DirRenderer(const char *base_path, unique_dir_ptr dir)
    : JsonRenderer(DirState { move(dir), base_path }) {}

JsonResult DirRenderer::renderState(size_t resume_point, json::JsonOutput &output, DirState &state) const {
    // Keep the indentation of the JSON in here!
    // clang-format off
    JSON_START;
    JSON_FIELD_ARR("children");
    while (state.dir.get() && (state.ent = readdir(state.dir.get()))) {
        if (const char *lfn = dirent_lfn(state.ent); lfn && lfn[0] == '.') {
            // Skip dot-files (should be hidden).
            continue;
        }

        state.childsize = nullopt;
        if (state.ent->d_type == DT_DIR && filename_is_transferrable(state.ent->d_name)) {
            // Suspicion: This might actualy be a partial file. Check and decide what to do about it.
            const bool is_printable = filename_is_printable(state.ent->d_name);
            MutablePath path(state.base_path);
            path.push(state.ent->d_name);
            auto st_opt = transfers::Transfer::get_transfer_partial_file_stat(path);
            if (st_opt.has_value() && is_printable) {
                // A print file ‒ report it even while we are downloading, it can be printed right away.
                state.ent->d_type = DT_REG;
                state.childsize = st_opt->st_size;
                state.read_only = true;
            } else if (st_opt.has_value()) {
                // This is a bbf that's being transfered. Hide it completely until it is complete.
                continue;
            } else {
                // It is a directory with a stupid name, but not a running
                // transfer. Act as if it is just a directory.
                state.read_only = false;
                state.childsize = child_size(state.base_path, state.ent->d_name);
            }
        } else {
            state.read_only = false;
            state.childsize = child_size(state.base_path, state.ent->d_name);
        }

        state.child_cnt ++;

        if (!state.first) {
            JSON_COMMA;
        } else {
            state.first = false;
        }

        JSON_OBJ_START;
            JSON_FIELD_STR("name", state.ent->d_name) JSON_COMMA;
            JSON_FIELD_STR("display_name", dirent_lfn(state.ent)) JSON_COMMA;
            JSON_FIELD_INT("size", state.childsize.value_or(0)) JSON_COMMA;
#ifdef UNITTESTS
            // While "our" dirent contains time, the "real" one doesn't, so disable for unit tests
            JSON_FIELD_INT("m_timestamp", 0) JSON_COMMA;
#else
            JSON_FIELD_INT("m_timestamp", state.ent->time) JSON_COMMA;
#endif
            JSON_FIELD_BOOL("read_only", state.read_only) JSON_COMMA;
            JSON_FIELD_STR("type", file_type(state.ent));
        JSON_OBJ_END;
    }
    JSON_ARR_END JSON_COMMA;
    JSON_FIELD_INT("file_count", state.child_cnt) JSON_COMMA;
    JSON_END;
    // clang-format on
}

FileExtra::FileExtra(std::unique_ptr<AnyGcodeFormatReader> gcode_reader_)
    : gcode_reader(std::move(gcode_reader_))
    , renderer(std::move(GcodeExtra(PreviewRenderer(gcode_reader->get()), GcodeMetaRenderer(gcode_reader->get())))) {}

FileExtra::FileExtra(const char *base_path, unique_dir_ptr dir)
    : renderer(move(DirRenderer(base_path, move(dir)))) {}

RenderState::RenderState(const Printer &printer, const Action &action, optional<CommandId> background_command_id)
    : printer(printer)
    , action(action)
    , lan(printer.net_info(Printer::Iface::Ethernet))
    , wifi(printer.net_info(Printer::Iface::Wifi))
    , transfer_id(Monitor::instance.id())
    , background_command_id(background_command_id) {
    memset(&st, 0, sizeof st);

    if (const auto *event = get_if<Event>(&action); event != nullptr) {
        const char *path = nullptr;
        const auto params = printer.params();
        bool error = false;

        switch (event->type) {
        case EventType::JobInfo:
            if (params.has_job) {
                path = params.job_path();
            }
            break;
        case EventType::FileInfo: {
            assert(event->path.has_value());
            SharedPath spath = event->path.value();
            path = spath.path();

            if (auto reader = std::make_unique<AnyGcodeFormatReader>(path); reader->is_open()) {
                // AnyGcodeFormatReader also handles partial files - so if this is actualy directory with partial file, it will be handled here
                if ((*reader)->fully_valid()) {
                    file_extra = FileExtra(std::move(reader));
                } else {
                    // Avoid trying to send metadata/previews from partially transfered files, because:
                    // * We are not sure this'll succeed, maybe we don't have
                    //   enough downloaded. In that case we would abort sending
                    //   the data, kill the connection and do other ugly things.
                    // * Sending the data is very expensive and competes for
                    //   resources with the download. By postponing the send of
                    //   the data _after_ it was fully downloaded (which we
                    //   trigger on our own), we try to avoid some of it.
                    file_extra = FileExtra();
                }
            } else if (unique_dir_ptr d(opendir(path)); d.get() != nullptr) {
                file_extra = FileExtra(path, std::move(d));
            } else if (unique_file_ptr f(fopen(path, "r")); f != nullptr) {
                // Non-gcode but existing file
                file_extra = FileExtra();
            } else {
                error = true;
            }
            // We are being rude here a bit. While the event is const, we modify the shared buffer. Nevertheless:
            // * The shared buffer is not shared into other threads, so nobody
            //   is reading it at the same time as we are writing into it.
            // * If this is ever called multiple times (it can be, if the same
            //   event needs to be resent), it results into the same values
            //   there.
            get_SFN_path(spath.path());
            get_LFN(spath.name(), FILE_NAME_BUFFER_LEN, spath.path());
            break;
        }
        case EventType::FileChanged: {
            assert(event->path.has_value());
            SharedPath spath = event->path.value();
            path = spath.path();

            get_SFN_path(spath.path());
            get_LFN(spath.name(), FILE_NAME_BUFFER_LEN, spath.path());
        }
        default:;
        }

        if (!error && path) {
            MutablePath mut_path(path);
            // Note: We allow only printable partial files in output and hide
            // all the rest. Other files are not usable until fully downloaded
            // & put into place (eg. a bbf), so we make sure Connect doesn't
            // get ideas about trying to use them.
            if (auto st_opt = transfers::Transfer::get_transfer_partial_file_stat(mut_path); st_opt.has_value() && filename_is_printable(path)) {
                has_stat = true;
                st = st_opt.value();
                read_only = true;
            } else if (stat(path, &st) == 0) {
                has_stat = true;
            }
        }

        // Some events override their transfer_id from another source, so we
        // replace it here to simplify the actual rendering. These events are
        // "after the fact" reports about the transfer, because they are
        // generated at the time when the transfer is _no longer running_.
        if (event->transfer_id.has_value()) {
            transfer_id = event->transfer_id;
        }
    }
}

JsonResult Renderer::renderState(size_t resume_point, JsonOutput &output, RenderState &state) const {
    return visit([&](auto action) -> JsonResult {
        return detail::render_msg(resume_point, output, state, action);
    },
        state.action);
}

} // namespace connect_client
