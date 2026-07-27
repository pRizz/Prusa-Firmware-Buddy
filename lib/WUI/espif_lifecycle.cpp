#include "espif_internal.hpp"

#include "data_exchange.hpp"
#include "pbuf_rx.h"
#include "wui.h"

#include <algorithm>
#include <cassert>
#include <cinttypes>
#include <common/metric.h>
#include <cstring>
#include <device/peripherals.h>
#include <logging/log.hpp>
#include <lwip/etharp.h>
#include <lwip/netifapi.h>
#include <tasks.hpp>
#include <timing.h>

LOG_COMPONENT_REF(ESPIF);

void espif_receive_data() {
    if (running_in_tester_mode()) {
        // block esp in tester mode
    } else {
        notify_esp_data();
    }
}

static void hard_reset_device() {
    HAL_GPIO_WritePin(ESP_RST_GPIO_Port, ESP_RST_Pin, GPIO_PIN_RESET);
    osDelay(100);
    HAL_GPIO_WritePin(ESP_RST_GPIO_Port, ESP_RST_Pin, GPIO_PIN_SET);
    esp_detected = false;
}

bool is_running(ESPIFOperatingMode mode) {
    switch (mode) {
    case ESPIF_UNINITIALIZED_MODE:
    case ESPIF_FLASHING_ERROR_NOT_CONNECTED:
    case ESPIF_FLASHING_ERROR_OTHER:
    case ESPIF_WRONG_FW:
    case ESPIF_SCANNING_MODE:
    case ESPIF_ERROR:
        return false;
    case ESPIF_WAIT_INIT:
    case ESPIF_NEED_AP:
    case ESPIF_RUNNING_MODE:
    case ESPIF_CONNECTING_AP:
        return true;
    }

    assert(0);
    return false;
}

bool can_recieve_data(ESPIFOperatingMode mode) {
    switch (mode) {
    case ESPIF_UNINITIALIZED_MODE:
    case ESPIF_FLASHING_ERROR_OTHER:
    case ESPIF_WRONG_FW:
    case ESPIF_ERROR:
        return false;
    case ESPIF_FLASHING_ERROR_NOT_CONNECTED:
    case ESPIF_WAIT_INIT:
    case ESPIF_NEED_AP:
    case ESPIF_RUNNING_MODE:
    case ESPIF_CONNECTING_AP:
    case ESPIF_SCANNING_MODE:
        return true;
    }

    assert(0);
    return false;
}

static void process_mac(uint8_t *data, struct netif *netif) {
    log_info(ESPIF, "MAC: %02x:%02x:%02x:%02x:%02x:%02x", data[0], data[1], data[2], data[3], data[4], data[5]);
    netif->hwaddr_len = ETHARP_HWADDR_LEN;
    memcpy(netif->hwaddr, data, ETHARP_HWADDR_LEN);

    ESPIFOperatingMode old = ESPIF_WAIT_INIT;
    if (esp_operating_mode.compare_exchange_strong(old, ESPIF_NEED_AP)) {
        const uint8_t version = fw_version.load();
        if (version != SUPPORTED_FW_VERSION) {
            log_warning(ESPIF, "Firmware version mismatch: %u != %u",
                version, static_cast<unsigned>(SUPPORTED_FW_VERSION));
            esp_operating_mode = ESPIF_WRONG_FW;
            return;
        }
        esp_operating_mode = ESPIF_NEED_AP;
        esp_was_ok = true;
        log_info(ESPIF, "Waiting for AP");
    } else {
        // FIXME: Actually, the ESP sends the MAC twice during it's lifetime.
        // BFW-5609.
        log_error(ESPIF, "ESP operating mode mismatch: %d", static_cast<int>(old));
    }
}

bool espif_link() {
    return associated;
}

void process_link_change(bool link_up, struct netif *netif) {
    assert(netif != nullptr);
    if (link_up) {
        if (!scan.is_running) {
            // Don't change the esp mode if the scan is running
            esp_operating_mode = ESPIF_RUNNING_MODE;
        }
        if (!associated.exchange(true)) {
            netifapi_netif_set_link_up(netif);
        }
    } else {
        if (associated.exchange(false)) {
            netifapi_netif_set_link_down(netif);
        }
    }
}

static void process_scan_ap_count(uint8_t ap_count) {
    scan.ap_count.exchange(ap_count);
}

static void process_scan_ssid() {
    ScanData::ap_info_queue.send(::scan.result);
}

void uart_input(uint8_t *data, size_t size, struct netif *netif) {
    esp_detected = true;

    // record metrics
    METRIC_DEF(metric_esp_in, "esp_in", METRIC_VALUE_CUSTOM, 1000, METRIC_ENABLED);
    static uint32_t bytes_received = 0;
    bytes_received += size;
    metric_record_custom(&metric_esp_in, " recv=%" PRIu32 "i", bytes_received);

    static enum ProtocolState {
        Intron,
        HeaderByte0,
        HeaderByte1,
        HeaderByte2,
        HeaderByte3,
        PacketData,
        PacketDataThrowaway,
        MACData,
        APData,
    } state
        = Intron;

    static uint intron_read = 0;

    static uint8_t message_type = MSG_CLIENTCONFIG_V2; // might as well initialize to something invalid

    static uint mac_read = 0; // Amount of MAC bytes already read
    static uint8_t mac_data[ETHARP_HWADDR_LEN];

    static uint16_t rx_len = 0; // Length of RX packet

    static struct pbuf *rx_buff = NULL; // First RX pbuf for current packet (chain head)
    static struct pbuf *rx_buff_cur = NULL; // Current pbuf for data receive (part of rx_buff chain)
    static uint32_t rx_read = 0; // Amount of bytes already read into rx_buff_cur

    bool did_reset = true;
    if (reset_parser.compare_exchange_strong(did_reset, false, std::memory_order_release, std::memory_order_relaxed)) {
        log_info(ESPIF, "Reseting uart input parser");
        state = Intron;
        rx_len = 0;
        rx_read = 0;
        intron_read = 0;
        mac_read = 0;
        scan.ap_ssid_read = 0;
        if (rx_buff != nullptr) {
            pbuf_free(rx_buff);
            rx_buff = nullptr;
            rx_buff_cur = nullptr;
        }
    }

    const uint8_t *end = &data[size];
    for (uint8_t *c = &data[0]; c < end;) {
        switch (state) {
        case Intron:
            if (*c++ == tx_message.intron[intron_read]) {
                intron_read++;
                if (intron_read >= sizeof(tx_message.intron)) {
                    state = HeaderByte0;
                    intron_read = 0;
                    seen_intron = true;
                }
            } else {
                intron_read = 0;
            }

            break;

        case HeaderByte0:
            message_type = *c++;
            switch (message_type) {
            case MSG_DEVINFO_V2:
            case MSG_PACKET_V2:
            case MSG_SCAN_AP_GET:
            case MSG_SCAN_AP_CNT:
                state = HeaderByte1;
                break;
            default:
                log_warning(ESPIF, "Unknown message type: %d", message_type);
                state = Intron;
            }
            break;

        case HeaderByte1:
            switch (message_type) {
            case MSG_DEVINFO_V2:
                fw_version.store(*c++);
                if (fw_version < 10) {
                    process_mac(mac_data, netif);
                    state = Intron;
                } else {
                    state = HeaderByte2;
                }
                break;
            case MSG_SCAN_AP_CNT:
                process_scan_ap_count(*c++);
                state = HeaderByte2;
                break;
            case MSG_SCAN_AP_GET:
                state = HeaderByte2;
                ::scan.result.ap_index = *c++;
                break;
            case MSG_SCAN_STOP:
                state = HeaderByte2;
                c++;
                break;
            case MSG_PACKET_V2: {
                // The byte holds both link status and the signal strength.
                //
                // * 1: (historically / backwards compatible mode) ‒ link up, unknown signal strength
                // * 0: Link down
                // * negative: Link up, number meaning the signal strength.
                int8_t signal = static_cast<int8_t>(*c++);
                signal_strength.store(signal > 0 ? 0 : signal);
                process_link_change(signal, netif);
                state = HeaderByte2;
                break;
            }
            default:
                assert(false && "internal inconsistency");
                state = Intron;
            }
            break;

        case MACData:
            while (c < end && mac_read < sizeof(mac_data)) {
                mac_data[mac_read++] = *c++;
            }
            if (mac_read == sizeof(mac_data)) {
                process_mac(mac_data, netif);
                mac_read = 0;
                state = Intron;
            }
            break;

        case APData:
            assert(rx_len == 33);

            while (c < end && scan.ap_ssid_read < config_store_ns::wifi_max_ssid_len) {
                scan.result.ssid[scan.ap_ssid_read++] = *c++;
            }
            if (scan.ap_ssid_read == config_store_ns::wifi_max_ssid_len && c != end) {
                scan.result.requires_password = static_cast<bool>(*c++);
                process_scan_ssid();
                scan.ap_ssid_read = 0;
                state = Intron;
            }
            break;

        case HeaderByte2:
            rx_len = (*c++) << 8;
            state = HeaderByte3;
            break;

        case HeaderByte3:
            rx_len = rx_len | (*c++);
            switch (message_type) {
            case MSG_DEVINFO_V2:
                state = MACData;
                break;
            case MSG_SCAN_AP_GET:
                state = APData;
                break;
            case MSG_SCAN_AP_CNT:
                state = Intron;
                break;
            case MSG_PACKET_V2:
                if (rx_len == 0) {
                    state = Intron;
                    seen_pong = true;
                    break;
                }
                rx_buff = pbuf_alloc_rx(rx_len);
                if (rx_buff) {
                    rx_buff_cur = rx_buff;
                    rx_read = 0;
                    state = PacketData;
                } else {
                    log_warning(ESPIF, "pbuf_alloc_rx(%zu) failed, dropping packet", static_cast<size_t>(rx_len));
                    rx_read = 0;
                    state = PacketDataThrowaway;
                }
                break;
            default:
                assert(false && "internal inconsistency");
                state = Intron;
            }
            break;
        case PacketData: {
            // Copy input to current pbuf (until end of input or current pbuf)
            const uint32_t to_read = std::min(rx_buff_cur->len - rx_read, (uint32_t)(end - c));
            memcpy((uint8_t *)rx_buff_cur->payload + rx_read, c, to_read);
            c += to_read;
            rx_read += to_read;

            // Switch to next pbuf
            if (rx_read == rx_buff_cur->len) {
                rx_buff_cur = rx_buff_cur->next;
                rx_read = 0;
            }

            // Filled all pbufs in a packet (current set to next = NULL)
            if (!rx_buff_cur) {
                if (netif->input(rx_buff, netif) != ERR_OK) {
                    log_warning(ESPIF, "tcpip_input() failed, dropping packet");
                    pbuf_free(rx_buff);
                    rx_buff = nullptr;
                    state = Intron;
                    break;
                } else {
                    // We've passed the ownership to netif->input, it'll free
                    // it. Forget about it on our side, so we never ever touch
                    // it by accident.
                    rx_buff = rx_buff_cur = nullptr;
                }
                seen_pong = true;
                state = Intron;
            }
        } break;
        case PacketDataThrowaway:
            const uint32_t to_read = std::min(rx_len - rx_read, (uint32_t)(end - c));
            c += to_read;
            rx_read += to_read;
            if (rx_read == rx_len) {
                state = Intron;
            }
            break;
        }
    }
}

static void force_down() {
    log_info(ESPIF, "Force down");
    struct netif *iface = active_esp_netif; // Atomic load
    assert(iface != nullptr); // Already initialized
    process_link_change(false, iface);
}

void espif_reset_connection() {
    esp_operating_mode.exchange(ESPIF_NEED_AP);
    process_link_change(false, active_esp_netif.load());
}

bool espif_need_ap() {
    return esp_operating_mode == ESPIF_NEED_AP;
}

void espif_reset() {
    if (!can_recieve_data(esp_operating_mode)) {
        log_error(ESPIF, "Can't reset ESP");
        return;
    }
    log_info(ESPIF, "Reset ESP");
    // Don't touch it in case we are flashing right now. If so, it'll get reset
    // when done.
    reset_intron();
    force_down();
    hard_reset_device(); // Reset device to receive MAC address
    esp_operating_mode = ESPIF_WAIT_INIT;
    reset_parser = true;
}

void espif_notify_flash_result(FlashResult result) {
    switch (result) {
    case FlashResult::success:
        esp_operating_mode = ESPIF_WAIT_INIT;
        break;
    case FlashResult::not_connected:
        esp_operating_mode = ESPIF_FLASHING_ERROR_NOT_CONNECTED;
        break;
    case FlashResult::failure:
        esp_operating_mode = ESPIF_FLASHING_ERROR_OTHER;
        break;
    }
}

EspFwState esp_fw_state() {
    ESPIFOperatingMode mode = esp_operating_mode.load();
    const bool detected = esp_detected.load();
    // Once we see the ESP work at least once, we never ever complain about
    // it not having firmware or similar. If we didn't do this, we could report
    // it to be missing just after it is reset for inactivity. It'll likely
    // just wake up in a moment.
    const bool seen_ok = esp_was_ok.load();
    switch (mode) {
    case ESPIF_UNINITIALIZED_MODE:
        if (seen_ok) {
            return EspFwState::Ok;
        }
        return EspFwState::Unknown;
    case ESPIF_FLASHING_ERROR_NOT_CONNECTED:
        return EspFwState::FlashingErrorNotConnected;
    case ESPIF_FLASHING_ERROR_OTHER:
        return EspFwState::FlashingErrorOther;
    case ESPIF_WAIT_INIT:
        if (seen_ok) {
            return EspFwState::Ok;
        }
        if (detected) {
            if (init_countdown > 0) {
                return EspFwState::Unknown;
            } else {
                return EspFwState::NoFirmware;
            }
        } else {
            return EspFwState::NoEsp;
        }
    case ESPIF_NEED_AP:
    case ESPIF_CONNECTING_AP:
    case ESPIF_RUNNING_MODE:
        return EspFwState::Ok;
    case ESPIF_WRONG_FW:
        return EspFwState::WrongVersion;
    case ESPIF_SCANNING_MODE:
        return EspFwState::Scanning;
    case ESPIF_ERROR:
        return EspFwState::Unknown;
    }
    assert(0);
    return EspFwState::NoEsp;
}

EspLinkState esp_link_state() {
    ESPIFOperatingMode mode = esp_operating_mode.load();
    switch (mode) {
    case ESPIF_WAIT_INIT:
    case ESPIF_WRONG_FW:
    case ESPIF_UNINITIALIZED_MODE:
    case ESPIF_FLASHING_ERROR_NOT_CONNECTED:
    case ESPIF_FLASHING_ERROR_OTHER:
    case ESPIF_SCANNING_MODE:
    case ESPIF_ERROR:
        return EspLinkState::Init;
    case ESPIF_NEED_AP:
    case ESPIF_CONNECTING_AP:
        return EspLinkState::NoAp;
    case ESPIF_RUNNING_MODE: {
        if (espif_link()) {
            if (seen_intron) {
                return EspLinkState::Up;
            } else {
                return EspLinkState::Silent;
            }
        } else {
            return EspLinkState::NoAp;
        }
    }
    }
    assert(0);
    return EspLinkState::Init;
}

std::optional<int8_t> esp_signal_strength() {
    int8_t result = signal_strength.load();
    if (result == 0) {
        return std::nullopt;
    } else {
        return result;
    }
}
