#include <catch2/catch.hpp>
#include <cstring>
#include <random>
#include <sstream>
#include <filesystem>
#include <fstream>

// We're naughty and want full access to MediaPrefetchManager
#define private   public
#define protected public
#include <media_prefetch.hpp>
#include <prefetch_compression.hpp>
#undef private
#undef protected

#include <test_tools/gcode_provider.hpp>

using namespace media_prefetch;

using S = MediaPrefetchManager::Status;
using RR = MediaPrefetchManager::ReadResult;
using R = GCodeReaderResult;

static std::string read_gcode(MediaPrefetchManager &mp, bool cropped = false) {
    MediaPrefetchManager::ReadResult c;
    return (mp.read_command(c).status == S::ok && c.cropped == cropped) ? std::string(c.gcode.data()) : std::string {};
}

TEST_CASE("media_prefetch::file_handle_tests") {
    MediaPrefetchManager::ReadResult c;

    SECTION("File gets closed after reading the whole file") {
        StubGcodeProviderMemory p;
        p.add_gcode("G0");

        MediaPrefetchManager mp;
        mp.start(p.filename(), {});
        mp.issue_fetch();
        CHECK(!mp.worker_state.gcode_reader.is_open());
    }

    SECTION("File stays closed after exhaustion") {
        StubGcodeProviderMemory p;
        p.add_gcode("G0");

        MediaPrefetchManager mp;
        mp.start(p.filename(), {});
        mp.issue_fetch();
        REQUIRE(read_gcode(mp) == "G0");
        REQUIRE(mp.read_command(c).status == S::end_of_file);
        CHECK(!mp.worker_state.gcode_reader.is_open());

        // Stays closed even if more issue_fetches are called
        mp.issue_fetch();

        CHECK(!mp.worker_state.gcode_reader.is_open());
        REQUIRE(mp.read_command(c).status == S::end_of_file);

        mp.issue_fetch();

        // It stays closed even if the reader _would_ return an error.
        p.add_breakpoint(R::RESULT_ERROR);
        CHECK(!mp.worker_state.gcode_reader.is_open());
        REQUIRE(mp.read_command(c).status == S::end_of_file);
    }

    SECTION("File gets closed after an error") {
        StubGcodeProviderMemory p;
        p.add_gcode("G0");
        p.add_breakpoint(R::RESULT_ERROR);
        p.add_gcode("G1");

        MediaPrefetchManager mp;
        mp.start(p.filename(), {});
        mp.issue_fetch();

        REQUIRE(read_gcode(mp) == "G0");
        REQUIRE(mp.read_command(c).status == S::usb_error);
        REQUIRE(!mp.worker_state.gcode_reader.is_open());

        mp.issue_fetch();
        REQUIRE(read_gcode(mp) == "G1");
        REQUIRE(mp.read_command(c).status == S::end_of_file);
        REQUIRE(!mp.worker_state.gcode_reader.is_open());
    }

    SECTION("File gets closed after calling stop()") {
        StubGcodeProviderMemory p;
        p.add_breakpoint(R::RESULT_TIMEOUT);

        MediaPrefetchManager mp;
        mp.start(p.filename(), {});
        mp.issue_fetch();

        REQUIRE(mp.read_command(c).status == S::end_of_buffer);
        REQUIRE(mp.worker_state.gcode_reader.is_open());

        mp.stop();
        REQUIRE(!mp.worker_state.gcode_reader.is_open());
    }
}
