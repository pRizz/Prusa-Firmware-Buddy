# External Integrations

**Analysis Date:** 2026-06-01

## APIs & External Services

**Prusa Connect Cloud:**

- Prusa Connect telemetry, events, registration, downloads, and command channel are implemented in `src/connect/`, with the default compressed host defined by `src/persistent_stores/store_instances/config_store/defaults.hpp` and host decompression rules in `src/connect/hostname.cpp`.
  - SDK/Client: custom HTTP/WebSocket client code in `src/connect/connect.cpp`, `src/connect/registrator.cpp`, `src/connect/connection_cache.cpp`, `src/common/http/`, and `src/connect/tls/`.
  - Auth: Connect `Token` and printer `Fingerprint` headers are sent by `src/connect/connect.cpp`; token storage is defined by `connect_token` in `src/persistent_stores/store_instances/config_store/store_definition.hpp`.
- Registration uses `/p/register` request/response headers in `src/connect/registrator.cpp`; the registration code is reported from the `Code` header and the permanent token is taken from the `Token` header.
- Telemetry and events use `/p/telemetry` and `/p/events` POST requests in `src/connect/connect.cpp`; WebSocket commands use `/p/ws` with protocol `prusa-connect` in `src/connect/connect.cpp`.
- Connect host, port, TLS, proxy host, proxy port, enablement, token, and custom certificate flags are configurable through `src/persistent_stores/store_instances/config_store/store_definition.hpp` and documented settings keys in `doc/prusa_printer_settings.ini`.
- Connect proxy support is implemented by `src/connect/connection_cache.cpp` and `src/common/http/proxy.cpp`; behavior and limitations are documented in `doc/proxy_support.md`.

**PrusaLink Local HTTP/API:**

- The printer exposes a local HTTP service on port 80 through `lib/WUI/http_lifetime.cpp`, `lib/WUI/nhttp/server.cpp`, and `lib/WUI/wui.cpp`.
  - SDK/Client: custom server framework in `lib/WUI/nhttp/` with generated HTTP parsing support from `utils/gen-automata/`.
  - Auth: Digest authentication and API-key authentication are handled in `lib/WUI/nhttp/req_parser.cpp`; username/password helpers live in `lib/WUI/wui_api.h` and `lib/WUI/wui.cpp`.
- PrusaLink API v1 handlers live in `lib/WUI/link_content/prusa_link_api_v1.cpp`, covering storage, info, job, status, transfer, and file operations.
- OctoPrint-compatible API handlers live in `lib/WUI/link_content/prusa_link_api_octo.cpp`, covering version, job, printer, files, download, and transfer endpoints.
- Static web UI and file-serving routes are registered in `lib/WUI/http_lifetime.cpp` and supporting `lib/WUI/link_content/` files.

**HTTP Download Sources:**

- Remote file transfer/download support is implemented in `src/transfers/download.cpp`, with command initiation coming from Connect command types in `src/connect/command.hpp`.
  - SDK/Client: custom HTTP client and parser code in `src/common/http/` plus transfer orchestration in `src/transfers/`.
  - Auth: source-specific URL/headers are command-driven; encrypted payload handling uses `src/transfers/decrypt.hpp`.
- Downloads support range requests and optional AES-CTR content encryption through headers handled in `src/transfers/download.cpp` and decryption helpers in `src/transfers/decrypt.hpp`.
- Download proxy behavior reuses Connect proxy configuration from `src/persistent_stores/store_instances/config_store/store_definition.hpp` and transport code in `src/transfers/download.cpp`.

**Time, Discovery, and Name Resolution:**

- SNTP/NTP is integrated through `lib/WUI/sntp/`; the default server is configured in `lib/WUI/sntp/sntp_opts.h`, and network startup is coordinated by `lib/WUI/wui.cpp`.
  - SDK/Client: LwIP SNTP and DNS facilities configured by `include/buddy/lwipopts.h`.
  - Auth: not applicable.
- mDNS is optionally included through `lib/WUI/mdns/` and enabled by the `MDNS` option in `ProjectOptions.cmake`.
- DNS resolution for Connect, metrics, syslog, downloads, and networking flows is provided by LwIP integration in `include/buddy/lwipopts.h`, `src/connect/tls/net_sockets.cpp`, `src/syslog/syslog_transport.cpp`, and `src/transfers/download.cpp`.

**Developer/Diagnostic Services:**

- Metrics can be emitted in an InfluxDB-line-protocol-compatible syslog envelope by `src/common/metric.cpp`, `src/common/metric_handlers.cpp`, and `src/syslog/syslog_transport.cpp`.
  - SDK/Client: custom UDP/syslog transport in `src/syslog/syslog_transport.cpp`; host collector tooling in `utils/metrics/collect.py`.
  - Auth: no firmware-side auth detected; destination host and ports are configured in `src/persistent_stores/store_instances/config_store/store_definition.hpp`.
- Host-side metrics development stack uses InfluxDB/Grafana container wiring in `utils/metrics/docker-compose.yml`, collector code in `utils/metrics/collect.py`, and documentation in `doc/metrics.md`.
- Host-side dump and phase-stepping utilities use Flask/serial/data-science packages declared in `utils/dumpserver/requirements.txt` and `utils/phase_stepping/requirements.txt`.

## Data Storage

**Databases:**

- No application database is embedded in the firmware; persistent runtime configuration is stored by the firmware config store defined in `src/persistent_stores/store_instances/config_store/store_definition.hpp` with defaults in `src/persistent_stores/store_instances/config_store/defaults.hpp`.
  - Connection: internal persistent store and flash-backed storage managed by `src/persistent_stores/` and board storage code under `src/buddy/`.
  - Client: generated/typed config-store accessors created from `src/persistent_stores/store_instances/config_store/store_definition.hpp`.
- Host metrics tooling can write to InfluxDB through `utils/metrics/collect.py`; the local container topology is declared in `utils/metrics/docker-compose.yml` and described in `doc/metrics.md`.
  - Connection: host-side environment/configuration for `utils/metrics/collect.py`; firmware sends UDP to `metrics_host`/`metrics_port` from `src/persistent_stores/store_instances/config_store/store_definition.hpp`.
  - Client: `aioinflux` dependency declared in `utils/metrics/requirements.txt`.

**File Storage:**

- USB/removable media storage uses FatFs through `lib/Middlewares/Third_Party/FatFs/CMakeLists.txt`, `src/buddy/filesystem_fatfs.cpp`, and `src/buddy/usbh_diskio.cpp`.
- Internal resources/configurable images use littlefs through `lib/Middlewares/Third_Party/littlefs/CMakeLists.txt`, `src/buddy/filesystem_littlefs.cpp`, `src/buddy/filesystem_littlefs_bbf.cpp`, `cmake/Littlefs.cmake`, and `utils/mklittlefs.py`.
- Firmware/resource artifacts are packed by `utils/pack_fw.py`, `cmake/Littlefs.cmake`, and packaging targets in `CMakeLists.txt`.
- Semihosting filesystem support for development/debug flows is implemented in `src/buddy/filesystem_semihosting.cpp`.

**Caching:**

- Connect transport caching/reuse is implemented by `src/connect/connection_cache.cpp`.
- HTTP parser and transfer buffering are implemented inside `src/common/http/`, `lib/WUI/nhttp/`, and `src/transfers/`.
- Metrics/syslog buffering uses queues and memory pools in `src/common/metric.cpp`, `src/common/metric_handlers.cpp`, and `src/syslog/syslog_transport.cpp`.

## Authentication & Identity

**Auth Provider:**

- Prusa Connect uses custom token identity, not a third-party auth provider; token, fingerprint, host, and TLS options are implemented in `src/connect/connect.cpp`, `src/connect/registrator.cpp`, and `src/persistent_stores/store_instances/config_store/store_definition.hpp`.
  - Implementation: registration code flow in `src/connect/registrator.cpp`, token persistence in `src/persistent_stores/store_instances/config_store/store_definition.hpp`, and per-request headers in `src/connect/connect.cpp`.
- PrusaLink uses local printer credentials; password generation/storage is implemented by `lib/WUI/wui.cpp`, auth parsing is in `lib/WUI/nhttp/req_parser.cpp`, and credential display flows live in `src/gui/screen_prusa_link.cpp`.
  - Implementation: Digest auth and API-key auth in `lib/WUI/nhttp/req_parser.cpp`; username and helper API declarations in `lib/WUI/wui_api.h`.
- WiFi identity is local network credential storage; SSID/password fields are declared in `src/persistent_stores/store_instances/config_store/store_definition.hpp` and settings-file keys are documented in `doc/prusa_printer_settings.ini`.
  - Implementation: network-device setup in `lib/WUI/netdev.c` and network manager startup in `lib/WUI/wui.cpp`.

**TLS and Certificates:**

- Connect TLS is implemented with mbedTLS in `src/connect/tls/tls.cpp`, socket glue in `src/connect/tls/net_sockets.cpp`, and certificate material declarations in `src/connect/tls/certificate.h`.
- TLS policy in `src/connect/tls/tls.cpp` requires certificate verification and uses an ECDHE/ECDSA AES-GCM TLS 1.2 cipher suite.
- Custom Connect CA support loads `/internal/connect/connect.der` when `connect_custom_tls_cert` is set in `src/persistent_stores/store_instances/config_store/store_definition.hpp`; DER handling is implemented in `src/connect/tls/tls.cpp`.
- Proxy tunneling for TLS uses HTTP CONNECT in `src/common/http/proxy.cpp` and connection selection in `src/connect/connection_cache.cpp`; `doc/proxy_support.md` documents proxy behavior and lack of proxy authentication.

## Monitoring & Observability

**Error Tracking:**

- No SaaS error-tracking integration is detected in repository configuration files such as `CMakeLists.txt`, `requirements.txt`, `.github/workflows/`, and `utils/holly/build-pr.jenkins`.
- Firmware error-code taxonomy is integrated through `lib/AddPrusaErrorCodes.cmake`, `lib/Prusa-Error-Codes/`, and UI/diagnostic code under `src/`.

**Logs:**

- Firmware logging destinations include syslog-style UDP output implemented in `src/logging/log_dest_syslog.cpp` and transported by `src/syslog/syslog_transport.cpp`.
- Runtime metrics/log destination settings are defined by `metrics_host`, `metrics_port`, `syslog_port`, and `metrics_allow` in `src/persistent_stores/store_instances/config_store/store_definition.hpp`.
- Development builds can default metrics to a Prusa internal host through `src/persistent_stores/store_instances/config_store/defaults.hpp`; production defaults are disabled/empty in the same defaults file.
- Metrics configuration and host collector usage are documented in `doc/metrics.md`.

## CI/CD & Deployment

**Hosting:**

- Firmware artifacts are produced locally/CI into `build/products` by `utils/build.py`; root packaging rules for `.bin`, `.bbf`, `.dfu`, and map files live in `CMakeLists.txt`.
- Flash/update flows for supported printer boards and XL puppy firmware are documented in `README.md`, with puppy sub-firmware build wiring in `CMakeLists.txt` and `ProjectOptions.cmake`.
- No hosted web application deployment is detected; local web assets are compiled into firmware resources through `src/resources/`, `lib/WUI/`, `cmake/Littlefs.cmake`, and `utils/pack_fw.py`.

**CI Pipeline:**

- Main firmware CI uses Jenkins/Holly pipeline code in `utils/holly/build-pr.jenkins` and a CI image definition in `utils/holly/Dockerfile`.
- Jenkins/Holly runs formatting checks, CMake builds, DFU generation, and host tests through commands in `utils/holly/build-pr.jenkins`, including `python3 utils/build.py --generate-dfu --skip-bootstrap` and CTest stages.
- GitHub Actions workflows in `.github/workflows/bright-builds-auto-update.yml` and `.github/workflows/stale.yml` handle repository maintenance rather than primary firmware build/test coverage.
- Jenkins credential usage is referenced by credential ID in `utils/holly/build-pr.jenkins`; secret values are not stored in this document.

## Environment Configuration

**Required env vars:**

- `BUDDY_NO_VIRTUALENV` optionally disables virtualenv management in `utils/bootstrap.py` and `cmake/Utilities.cmake`.
- `BRIGHT_BUILDS_PUSH_TOKEN` is required by `.github/workflows/bright-builds-auto-update.yml` for automated Bright Builds update PRs.
- Firmware signing uses a `SIGNING_KEY` CMake cache path configured by `ProjectOptions.cmake` and `utils/build.py`; private key material must remain outside committed source/docs.
- Runtime network and service values are stored in config-store fields declared by `src/persistent_stores/store_instances/config_store/store_definition.hpp`, including WiFi credentials, PrusaLink password, Connect token/host/proxy/TLS options, metrics host/ports, and syslog port.
- Settings-file import/export examples are documented in `doc/prusa_printer_settings.ini`; only key names should be referenced in docs and code comments, not sample credential values.

**Secrets location:**

- No `.env`-based application secret system is detected; runtime secrets are firmware config-store values defined by `src/persistent_stores/store_instances/config_store/store_definition.hpp`.
- Signing key material is external to the source tree and referenced only by path through `SIGNING_KEY` in `ProjectOptions.cmake` and `utils/build.py`.
- Jenkins/GitHub secrets are referenced through CI configuration in `utils/holly/build-pr.jenkins` and `.github/workflows/bright-builds-auto-update.yml`, with secret values managed by the CI providers.

## Webhooks & Callbacks

**Incoming:**

- Local PrusaLink HTTP/API requests are accepted on port 80 by `lib/WUI/http_lifetime.cpp`, routed through `lib/WUI/nhttp/server.cpp`, and handled by `lib/WUI/link_content/prusa_link_api_v1.cpp` and `lib/WUI/link_content/prusa_link_api_octo.cpp`.
- USB mass-storage and local file access are handled through `src/buddy/usb_host.cpp`, `src/buddy/usbh_diskio.cpp`, and `src/buddy/filesystem_fatfs.cpp`.
- Serial/UART hardware integrations include ESP flashing in `src/buddy-esp-serial-flasher/`, MMU communication in `src/mmu2/`, and puppy/RS485 Modbus support in `src/puppies/` and `src/puppy/shared/`.

**Outgoing:**

- Prusa Connect HTTPS/WebSocket traffic is initiated by `src/connect/connect.cpp`, `src/connect/registrator.cpp`, `src/connect/connection_cache.cpp`, and `src/connect/tls/`.
- Connect/download HTTP requests can target command-provided remote hosts through `src/transfers/download.cpp` and `src/common/http/`.
- Metrics and syslog UDP traffic is sent by `src/common/metric_handlers.cpp`, `src/logging/log_dest_syslog.cpp`, and `src/syslog/syslog_transport.cpp`.
- SNTP/NTP requests are sent by `lib/WUI/sntp/` using defaults in `lib/WUI/sntp/sntp_opts.h` and network setup in `lib/WUI/wui.cpp`.
- Optional mDNS announcements and multicast traffic use `lib/WUI/mdns/` when enabled by `ProjectOptions.cmake`.
- ESP network-module flashing traffic is sent over UART by `src/buddy-esp-serial-flasher/esp_flash.cpp`, using support libraries in `lib/esp-serial-flasher/` and firmware projects in `lib/esp32-nic/` and `lib/esp8266-nic/`.
- XL/Dwarf/Modular Bed/xBuddy Extension Modbus traffic is sent through `src/puppies/PuppyModbus.cpp`, `include/puppies/modbus.h`, and shared RS485 code in `src/puppy/shared/`.

______________________________________________________________________

*Integration audit: 2026-06-01*
