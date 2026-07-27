#include "gcode_reader_any.hpp"
#include "catch2/catch.hpp"

#include <deque>
#include <iostream>
#include <fstream>
#include <sys/stat.h>

namespace {

constexpr static const char *PLAIN_TEST_FILE = "test_plain.gcode";

constexpr static const std::string_view DUMMY_DATA_LONG = "; Short line\n"
                                                          ";Long line012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789\n"
                                                          ";Another short line";
constexpr static const std::string_view DUMMY_DATA_EXACT = ";01234567890123456789012345678901234567890123456789012345678901234567890123456789\n"
                                                           ";Another line";
constexpr static const std::string_view DUMMY_DATA_EXACT_EOF = ";01234567890123456789012345678901234567890123456789012345678901234567890123456789";
constexpr static const std::string_view DUMMY_DATA_ERR = ";01234567890123456789012345678901234567890123456789012345678901234567890123456789012345";

using std::string_view;

struct DummyReader : public GcodeReaderCommon {
    std::deque<char> data;
    Result_t final_result;

    DummyReader(const std::string_view &input, Result_t final_result)
        : data(input.begin(), input.end())
        , final_result(final_result) {
        // Grouchy Smurf: I hate pointer-to-member-function casts
        ptr_stream_getc = static_cast<stream_getc_type>(&DummyReader::dummy_getc);
    }

    virtual bool stream_metadata_start() override {
        return true;
    }

    virtual Result_t stream_gcode_start(uint32_t) override {
        return Result_t::RESULT_OK;
    }

    virtual AbstractByteReader *stream_thumbnail_start(uint16_t, uint16_t, ImgType, bool) override {
        return nullptr;
    }

    virtual uint32_t get_gcode_stream_size_estimate() override {
        return 0;
    }

    virtual uint32_t get_gcode_stream_size() override {
        return 0;
    }

    virtual FileVerificationResult verify_file(FileVerificationLevel, std::span<uint8_t>) const override {
        return FileVerificationResult { true };
    }

    virtual bool valid_for_print() override {
        return true;
    }

    virtual Result_t stream_get_line(GcodeBuffer &buffer, Continuations continuations) {
        return stream_get_line_common(buffer, continuations);
    }

    Result_t dummy_getc(char &out) {
        if (data.empty()) {
            return final_result;
        } else {
            out = data.front();
            data.pop_front();
            return Result_t::RESULT_OK;
        }
    }

    virtual StreamRestoreInfo get_restore_info() override { return {}; }

    virtual void set_restore_info(const StreamRestoreInfo &) override {}
};

} // namespace

TEST_CASE("Reader: Long comment, split") {
    DummyReader reader(DUMMY_DATA_LONG, IGcodeReader::Result_t::RESULT_EOF);
    GcodeBuffer buffer;

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == "; Short line");
    // Checking both, because len bases it on end-begin, strlen on \0 position
    REQUIRE(buffer.line.len() == 12);
    REQUIRE(strlen(buffer.line.c_str()) == 12);
    REQUIRE(buffer.line_complete);

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == ";Long line01234567890123456789012345678901234567890123456789012345678901234567890");
    // Note: In the split mode, it is _not_ \0 terminated here.
    // Therefore, no strlen and using all 81 characters.
    REQUIRE(buffer.line.len() == 81);
    REQUIRE_FALSE(buffer.line_complete);

    // The continuation
    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == "1234567890123456789012345678901234567890123456789");
    REQUIRE(buffer.line.len() == 49);
    REQUIRE(strlen(buffer.line.c_str()) == 49);
    REQUIRE(buffer.line_complete);

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == ";Another short line");
    REQUIRE(buffer.line.len() == 19);
    REQUIRE(strlen(buffer.line.c_str()) == 19);
    REQUIRE(buffer.line_complete);

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_EOF);
}

TEST_CASE("Reader: Long comment, discard") {
    DummyReader reader(DUMMY_DATA_LONG, IGcodeReader::Result_t::RESULT_EOF);
    GcodeBuffer buffer;

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Discard) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == "; Short line");
    // Checking both, because len bases it on end-begin, strlen on \0 position
    REQUIRE(buffer.line.len() == 12);
    REQUIRE(strlen(buffer.line.c_str()) == 12);
    REQUIRE(buffer.line_complete);

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Discard) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == ";Long line0123456789012345678901234567890123456789012345678901234567890123456789");
    REQUIRE(buffer.line.len() == 80);
    REQUIRE(strlen(buffer.line.c_str()) == 80);
    REQUIRE_FALSE(buffer.line_complete);

    // The continuation is not present

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Discard) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == ";Another short line");
    REQUIRE(buffer.line.len() == 19);
    REQUIRE(strlen(buffer.line.c_str()) == 19);
    REQUIRE(buffer.line_complete);

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Discard) == IGcodeReader::Result_t::RESULT_EOF);
}

TEST_CASE("Reader: Exact long, split") {
    DummyReader reader(DUMMY_DATA_EXACT, IGcodeReader::Result_t::RESULT_EOF);
    GcodeBuffer buffer;

    // The first line fits exactly. But the reader doesn't know it ended.
    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == ";01234567890123456789012345678901234567890123456789012345678901234567890123456789");
    REQUIRE(buffer.line.len() == 81);
    REQUIRE_FALSE(buffer.line_complete);

    // There's an empty continuation to mark it is complete
    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line.is_empty());
    REQUIRE(buffer.line_complete);

    // Then the rest can be read
    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == ";Another line");
    REQUIRE(buffer.line_complete);

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_EOF);
}

TEST_CASE("Reader: Exact long, discard") {
    DummyReader reader(DUMMY_DATA_EXACT, IGcodeReader::Result_t::RESULT_EOF);
    GcodeBuffer buffer;

    // The first line fits exactly. But the reader doesn't know it ended.
    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Discard) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == ";0123456789012345678901234567890123456789012345678901234567890123456789012345678");
    REQUIRE(buffer.line.len() == 80);
    REQUIRE_FALSE(buffer.line_complete);

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Discard) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == ";Another line");
    REQUIRE(buffer.line_complete);

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Discard) == IGcodeReader::Result_t::RESULT_EOF);
}

TEST_CASE("Reader: Exact at EOF, split") {
    DummyReader reader(DUMMY_DATA_EXACT_EOF, IGcodeReader::Result_t::RESULT_EOF);
    GcodeBuffer buffer;

    // The first line fits exactly. But the reader doesn't know it ended.
    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == ";01234567890123456789012345678901234567890123456789012345678901234567890123456789");
    REQUIRE(buffer.line.len() == 81);
    REQUIRE_FALSE(buffer.line_complete);

    // There's an empty continuation to mark it is complete
    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line.is_empty());
    REQUIRE(buffer.line_complete);

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_EOF);
}

TEST_CASE("Reader: Exact at EOF, discard") {
    DummyReader reader(DUMMY_DATA_EXACT_EOF, IGcodeReader::Result_t::RESULT_EOF);
    GcodeBuffer buffer;

    // The first line fits exactly. But the reader doesn't know it ended.
    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Discard) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == ";0123456789012345678901234567890123456789012345678901234567890123456789012345678");
    REQUIRE(buffer.line.len() == 80);
    REQUIRE_FALSE(buffer.line_complete);

    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Discard) == IGcodeReader::Result_t::RESULT_EOF);
}

TEST_CASE("Reader: Error in long, split") {
    DummyReader reader(DUMMY_DATA_ERR, IGcodeReader::Result_t::RESULT_ERROR);
    GcodeBuffer buffer;

    // The first line fits exactly. But the reader doesn't know it ended.
    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Split) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == ";01234567890123456789012345678901234567890123456789012345678901234567890123456789");
    REQUIRE(buffer.line.len() == 81);
    REQUIRE_FALSE(buffer.line_complete);

    // Error reading the continuation.
    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Discard) == IGcodeReader::Result_t::RESULT_ERROR);
}

TEST_CASE("Reader: Error in long, discard") {
    DummyReader reader(DUMMY_DATA_ERR, IGcodeReader::Result_t::RESULT_ERROR);
    GcodeBuffer buffer;

    // The first line fits exactly. But the reader doesn't know it ended.
    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Discard) == IGcodeReader::Result_t::RESULT_OK);
    REQUIRE(buffer.line == ";0123456789012345678901234567890123456789012345678901234567890123456789012345678");
    REQUIRE(buffer.line.len() == 80);
    REQUIRE_FALSE(buffer.line_complete);

    // Interestingly, this is not when reading the end of the line, but reading
    // the next line.. but it still results in ERROR.
    REQUIRE(reader.stream_get_line(buffer, IGcodeReader::Continuations::Discard) == IGcodeReader::Result_t::RESULT_ERROR);
}
