# Testing Patterns

**Analysis Date:** 2026-06-01

## Test Framework

**Runner:**

- C++ unit tests use Catch2 from `lib/Catch2/`, registered through CMake in `tests/unit/CMakeLists.txt` with `catch_discover_tests(...)`.
- The shared C++ test entrypoint is `tests/unit/test_main.cpp`, which defines `CATCH_CONFIG_MAIN` and is linked through the `catch_main` library in `tests/unit/CMakeLists.txt`.
- Pytest is used for simulator integration tests in `tests/integration/`, block-device tests in `tests/blockdevice/`, legacy tests in `tests/integration_old/`, and Python binding tests in `src/common/marlin_server_types/python_binding/tests/`.
- `requirements.txt` pins `pytest~=7.3.2` and `pytest-asyncio~=0.21`; `pyproject.toml` sets `asyncio_mode = "auto"`.
- CMake enables unit tests only for native builds: `CMakeLists.txt` guards `enable_testing()` and `add_subdirectory(tests)` behind `if(NOT CMAKE_CROSSCOMPILING)` and `UNITTESTS_ENABLE`.

**Assertion Library:**

- C++ tests use Catch2 assertions such as `REQUIRE(...)`, `CHECK(...)`, `SECTION(...)`, and generators from `catch2/catch.hpp`, as in `tests/unit/common/str_utils_test.cpp`, `tests/unit/connect/planner.cpp`, and `tests/unit/transfers/transfer_tests.cpp`.
- Python tests use plain `assert`, `pytest.raises(...)`, `pytest.fail(...)`, pytest fixtures, and pytest markers, as in `tests/integration/test_prusa_link.py`, `tests/integration/conftest.py`, and `src/common/marlin_server_types/python_binding/tests/test_basic.py`.

**Run Commands:**

```bash
mkdir build_tests
cd build_tests
cmake .. -G Ninja -DBOARD=BUDDY
ninja tests
ctest .
```

```bash
mkdir build-tests
cd build-tests
cmake .. -DBOARD=BUDDY
make tests
ctest .
```

```bash
pytest tests/integration --firmware <firmware.bin>
```

```bash
pytest tests/blockdevice --device <block-device-path>
```

```bash
pip install src/common/marlin_server_types/python_binding/ --target=<install-dir>
PYTHONPATH="$PYTHONPATH:<install-dir>" pytest src/common/marlin_server_types/python_binding/tests/
```

- No watch-mode command is documented in `README.md`, `tests/unit/README.md`, or `tests/integration/README.md`.
- No coverage command or coverage threshold is detected in `CMakeLists.txt`, `pyproject.toml`, `requirements.txt`, `tests/`, or `utils/holly/build-pr.jenkins`.

## Test File Organization

**Location:**

- C++ unit tests live under `tests/unit/<subsystem>/`, with registration in `tests/unit/<subsystem>/CMakeLists.txt`; examples include `tests/unit/common/`, `tests/unit/connect/`, `tests/unit/gui/`, `tests/unit/lang/`, and `tests/unit/persistent_stores/`.
- Shared C++ test stubs live under `tests/stubs/`, with extra subsystem mocks under paths such as `tests/unit/connect/`, `tests/unit/mock/`, and `tests/unit/lib/WUI/nhttp/`.
- Simulator integration tests live in `tests/integration/` and are documented by `tests/integration/README.md`.
- Device-backed block tests live in `tests/blockdevice/` and require `--device` from `tests/blockdevice/conftest.py`.
- Older manual or stale integration material lives in `tests/integration_old/`; `tests/CMakeLists.txt` comments out `tests/module/Connect` as outdated manual test material.
- Python binding package tests live in `src/common/marlin_server_types/python_binding/tests/`, and CI invokes them from `utils/holly/build-pr.jenkins`.

**Naming:**

- C++ test files use `*_test.cpp`, `*_tests.cpp`, or a target-oriented file name such as `tests/unit/connect/planner.cpp`.
- C++ test targets usually end with `_tests`, such as `str_utils_tests`, `connect_tests`, `connect_planner_tests`, and `eeprom_unit_tests` in `tests/unit/*/CMakeLists.txt`.
- Pytest modules use `test_*.py`, as in `tests/integration/test_basic_examples.py`, `tests/integration/test_safety.py`, and `tests/blockdevice/test_block_device.py`.

**Structure:**

```text
tests/
├── CMakeLists.txt                  # Enables C++ unit tests and FreeRTOS stubs
├── unit/                           # Catch2 unit tests by subsystem
├── stubs/                          # Header and C/C++ substitutions for firmware dependencies
├── integration/                    # pytest simulator tests
├── blockdevice/                    # pytest tests for block devices
├── integration_old/                # legacy/manual integration tests
└── module/Connect/                 # disabled manual Connect tests
```

## Test Structure

**Suite Organization:**

```cpp
#include "catch2/catch.hpp"

namespace {
struct Test {
    Test();
    void consume_telemetry();
};
} // namespace

TEST_CASE("Retries early") {
    Test test(ActionResult::Failed);

    Duration sleep1 = test.consume_sleep();
    test.event_info();
    test.planner.action_done(ActionResult::Failed);

    Duration sleep2 = test.consume_sleep();
    REQUIRE(sleep1 < sleep2);
}
```

```python
pytestmark = pytest.mark.asyncio

@pytest.fixture
async def wui_client(printer):
    await utils.wait_for_bootstrap(printer)
    async with aiohttp.ClientSession(base_url=wui_base_url(printer)) as session:
        yield session

async def test_web_interface_is_accessible(wui_client):
    response = await wui_client.get('/')
    assert response.ok
```

**Patterns:**

- C++ tests are grouped by CMake executable and discovered by Catch2 through `add_catch_test(...)` in `tests/unit/CMakeLists.txt`.
- C++ tests use `TEST_CASE("behavior name")` and `SECTION("case name")`; examples are `tests/unit/common/str_utils_test.cpp`, `tests/unit/common/circular_buffer_test.cpp`, and `tests/unit/transfers/transfer_tests.cpp`.
- Test-local helper structs and fixtures are usually placed in anonymous namespaces, as in `tests/unit/connect/planner.cpp`.
- Use `REQUIRE(...)` when later assertions depend on the condition and `CHECK(...)` when the test can continue collecting failures; both appear in `tests/unit/common/str_utils_test.cpp` and `tests/unit/puppies/fifo_coder_tests.cpp`.
- Pytest integration tests centralize simulator setup and shared fixtures in `tests/integration/conftest.py`, then keep scenario logic in modules such as `tests/integration/test_basic_examples.py` and `tests/integration/test_prusa_link.py`.
- Bright Builds `standards/core/testing.md` applies because `standards-overrides.md` has no active override: new unit tests for pure or business logic should keep one concern per test and make Arrange, Act, Assert clear. Existing Catch2 tests often use `TEST_CASE` and `SECTION` names instead of explicit comments, so add explicit `// Arrange`, `// Act`, and `// Assert` comments when the test body is not immediately obvious.

## Mocking

**Framework:** hand-written stubs and CMake source substitution

**Patterns:**

```cpp
class MockPrinter : public Printer {
public:
    std::vector<std::string> submitted_gcodes;

    virtual GcodeResult submit_gcode(const char *gcode) override {
        submitted_gcodes.push_back(gcode);
        return GcodeResult::Submitted;
    }
};
```

```cpp
uint32_t ticks_ms() {
    return mock_time;
}

void _bsod(const char *fmt, const char *file_name, int line_number, ...) {
    throw std::runtime_error(fmt);
}
```

```python
@pytest_asyncio.fixture
async def printer(printer_factory):
    async with printer_factory() as printer:
        yield printer
```

**What to Mock:**

- Mock firmware interfaces that would otherwise hit hardware, firmware globals, FreeRTOS, networking, or fatal handlers. Examples include `tests/unit/connect/mock_printer.h`, `tests/unit/connect/time_mock.cpp`, `tests/unit/mock/bsod.cpp`, and `tests/stubs/logging/log.hpp`.
- Prefer stubs in `tests/stubs/` when a header must shadow production includes, such as `tests/stubs/host/libintl.h`, `tests/stubs/logging/log.hpp`, and `tests/stubs/FreeRTOS/`.
- Use local C++ source substitutions in the test target's `CMakeLists.txt` when a subsystem needs fake implementations, as in `tests/unit/connect/CMakeLists.txt` with `partial_file_mock.cpp`, `gui_media_events_mock.cpp`, `buddy_chamber_mock.cpp`, and `time_mock.cpp`.
- Use pytest fixtures for simulator processes, temporary flash/eeprom state, network ports, and authenticated HTTP clients, as in `tests/integration/conftest.py` and `tests/integration/test_prusa_link.py`.

**What NOT to Mock:**

- Do not mock pure parsing, transformation, and core business logic that is cheap to run directly; examples include `tests/unit/common/str_utils_test.cpp`, `tests/unit/common/circular_buffer_test.cpp`, and `tests/unit/module/utils/timer_tests.cpp`.
- Do not mock generated automata when the generator itself is under test; `tests/unit/common/automata/CMakeLists.txt` generates automata into the build directory and tests them through `tests/unit/common/automata/generated.cpp` and `tests/unit/common/automata/traversal.cpp`.
- Do not hide production include-order assumptions in tests; if a test depends on stubs shadowing real headers, declare the include order in the owning `CMakeLists.txt`, as in `tests/unit/connect/CMakeLists.txt`.

## Fixtures and Factories

**Test Data:**

```cpp
inline Printer::Params params_idle() {
    Printer::Params params(std::nullopt);
    params.job_id = 13;
    params.state = printer_state::DeviceState::Idle;
    return params;
}
```

```python
DEFAULT_EEPROM_CONTENT = {
    'Run Selftest': struct.pack('<B', False),
    'Run XYZ Calibration': struct.pack('<B', False),
}
```

**Location:**

- C++ fixture helpers live beside the tests that own them, such as `tests/unit/connect/mock_printer.h`, `tests/unit/connect/time_mock.h`, and `tests/unit/logging/utils.hpp`.
- Shared C/C++ stubs live in `tests/stubs/`, including `tests/stubs/FreeRTOS/`, `tests/stubs/host/libintl.h`, and `tests/stubs/jsmn_impl.c`.
- Integration fixtures live in `tests/integration/conftest.py`; reusable simulator actions live in `tests/integration/actions/`.
- Integration binary data and G-code fixtures live in `tests/integration/data/`, `tests/unit/transfers/`, and `tests/unit/common/filament_sensor/`.
- Python binding test fixtures are minimal and live in `src/common/marlin_server_types/python_binding/tests/test_basic.py`.

## Coverage

**Requirements:** None enforced in detected repository configuration.

**View Coverage:**

```bash
# Not detected: no gcov/lcov/coverage.py command is configured in repo docs or CI.
```

- `utils/holly/build-pr.jenkins` archives CTest failure logs from `build-test/Testing/Temporary/LastTest.log`, but does not publish coverage.
- No `coverage`, `pytest-cov`, `gcov`, `lcov`, or CMake coverage target is detected in `requirements.txt`, `pyproject.toml`, `CMakeLists.txt`, `cmake/`, or `tests/`.

## Test Types

**Unit Tests:**

- C++ unit tests are the main fast verification surface. Build them with native CMake using `-DBOARD=BUDDY`, `ninja tests`, and `ctest .`, as documented in `tests/unit/README.md` and `README.md`.
- `tests/unit/CMakeLists.txt` defines `UNITTESTS`, turns RTTI on for tests, adds `catch_main`, and includes subsystem directories.
- Subsystems add executables with tested production sources plus test sources, then register them with `add_catch_test(...)`; examples are `tests/unit/common/CMakeLists.txt`, `tests/unit/connect/CMakeLists.txt`, and `tests/unit/logging/CMakeLists.txt`.

**Integration Tests:**

- Simulator integration tests are pytest async tests under `tests/integration/`, requiring a firmware binary with `--firmware` and optionally `--simulator`, `--enable-graphic`, and `--gdb` from `tests/integration/conftest.py`.
- `tests/integration/README.md` documents simulator test requirements, first-run OCR model download, cache behavior, logging flags, and debugger options.
- Integration tests use QEMU/simulator APIs from `utils/simulator/`, shared actions in `tests/integration/actions/`, and data files in `tests/integration/data/`.

**E2E Tests:**

- Simulator integration tests in `tests/integration/` are the closest E2E coverage detected. They boot firmware in a simulator, drive encoder/screen/network actions, and inspect HTTP and screen behavior in files such as `tests/integration/test_basic_examples.py` and `tests/integration/test_prusa_link.py`.
- `tests/blockdevice/` contains hardware/device-adjacent pytest tests that require a block device path and include benchmark-marked tests in `tests/blockdevice/test_block_device.py`.
- `tests/integration_old/` and `tests/module/Connect/` contain legacy/manual material; `tests/CMakeLists.txt` leaves `tests/module/Connect` commented out because it is outdated and does not compile.

## Common Patterns

**Async Testing:**

```python
pytestmark = pytest.mark.asyncio

async def test_max_temp_error_on_bed(printer):
    await utils.wait_for_bootstrap(printer)
    await temperature.set(printer, Thermistor.BED, 230)
    await screen.wait_for_text(printer, 'MAXTEMP ERROR')
```

**Error Testing:**

```cpp
SECTION("empty") {
    std::string str = "XX";
    res = from_chars_light(str.c_str(), str.c_str() + str.size(), val, 10);
    CHECK(res.ec == std::errc::invalid_argument);
}
```

```python
with pytest.raises(Exception):
    marlin_server_types.fsm_type_to_enum(None)
```

**Generated Inputs:**

- Tests that need generated automata use CMake `add_custom_command(...)` and depend on generator scripts in `utils/gen-automata/`, as in `tests/unit/common/automata/CMakeLists.txt` and `tests/unit/connect/CMakeLists.txt`.
- Persistent-store tests generate journal hashes through `tests/unit/persistent_stores/CMakeLists.txt` and `src/persistent_stores/GenerateJournalHashes.cmake`.

**Skipped or Flaky Tests:**

- Use `pytest.mark.skip()` for disabled simulator tests with nearby comments explaining the reason, as in `tests/integration/test_prusa_link.py` and `tests/integration/test_safety.py`.
- Keep legacy manual tests isolated under `tests/integration_old/` or explicitly disabled in CMake, as `tests/CMakeLists.txt` does for `tests/module/Connect`.

## CI and Pre-Commit Verification

**Pre-Commit:**

- `.pre-commit-config.yaml` runs `cmake-format`, `yapf`, local clang-format via `.dependencies/clang-format-16-83817c2f/clang-format`, logging overview generation, CMake preset generation, requirements synchronization, trailing whitespace, final newline, and mixed-line-ending checks.
- `utils/holly/build-pr.jenkins` runs `pre-commit run --source remotes/origin/${CHANGE_TARGET} --origin HEAD --show-diff-on-failure --hook-stage manual` for pull requests.
- `doc/contributing.md` instructs contributors to install hooks with `pre-commit install`; local changes should still be verified explicitly when hooks are not installed.

**CI Pipeline:**

- Firmware build stages in `utils/holly/build-pr.jenkins` call `python3 utils/build.py` with presets, `--generate-dfu`, `--skip-bootstrap`, and `-DCUSTOM_COMPILE_OPTIONS:STRING="-Werror"`.
- Unit test CI in `utils/holly/build-pr.jenkins` uses CTest build-and-test with Ninja, target `tests`, build option `-DBOARD=BUDDY`, and test command `ctest`.
- Python binding CI in `utils/holly/build-pr.jenkins` installs `src/common/marlin_server_types/python_binding/` into a target directory and runs pytest on `src/common/marlin_server_types/python_binding/tests/`.
- Pre-release checks in `utils/holly/build-pr.jenkins` run `utils/generate-error-codes-report.py` and `utils/translations_and_fonts/generate-translations-report.sh`, archiving report artifacts.
- GitHub Actions under `.github/workflows/` only contain Bright Builds auto-update and stale-issue workflows; main code CI is represented by `utils/holly/build-pr.jenkins`.

______________________________________________________________________

*Testing analysis: 2026-06-01*
