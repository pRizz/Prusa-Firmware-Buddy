#pragma once

#include "espif.h"

#include <atomic>
#include <freertos/mutex.hpp>
#include <freertos/queue.hpp>
#include <lwip/netif.h>
#include <span>

enum ESPIFOperatingMode {
    ESPIF_UNINITIALIZED_MODE,
    ESPIF_WAIT_INIT,
    ESPIF_NEED_AP,
    ESPIF_CONNECTING_AP,
    ESPIF_RUNNING_MODE,
    ESPIF_SCANNING_MODE,
    ESPIF_WRONG_FW,
    ESPIF_FLASHING_ERROR_NOT_CONNECTED,
    ESPIF_FLASHING_ERROR_OTHER,
    ESPIF_ERROR,
};

enum MessageType {
    MSG_DEVINFO_V2 = 0,
    MSG_CLIENTCONFIG_V2 = 6,
    MSG_PACKET_V2 = 7,
    MSG_SCAN_START = 8,
    MSG_SCAN_STOP = 9,
    MSG_SCAN_AP_CNT = 10,
    MSG_SCAN_AP_GET = 11,
};

inline constexpr uint8_t SUPPORTED_FW_VERSION = 13;

extern std::atomic<uint8_t> fw_version;
extern std::atomic<ESPIFOperatingMode> esp_operating_mode;
extern std::atomic<bool> associated;
extern std::atomic<netif *> active_esp_netif;
extern std::atomic<uint8_t> init_countdown;
extern std::atomic<bool> seen_intron;
extern std::atomic<bool> seen_pong;
extern std::atomic<bool> reset_parser;
extern std::atomic<int8_t> signal_strength;
extern std::atomic<bool> esp_detected;
extern std::atomic<bool> esp_was_ok;

struct __attribute__((packed)) TxMessage {
    uint8_t intron[8];
    uint8_t type;
    uint8_t byte;
    uint16_t size;
};

extern TxMessage tx_message;

struct APInfo {
    std::span<uint8_t> ssid;
    uint8_t ap_index;
    bool requires_password;
};

struct ScanData {
    std::atomic<bool> is_running;
    APInfo result;
    uint16_t ap_ssid_read = 0;
    ESPIFOperatingMode prescan_op_mode = ESPIF_UNINITIALIZED_MODE;
    std::atomic<uint8_t> ap_count = 0;
    static constexpr auto SYNC_EVENT_TIMEOUT = 10 /*ms*/;
    static freertos::Mutex get_ap_info_mutex;
    static freertos::Queue<APInfo, 1> ap_info_queue;
};

extern ScanData scan;

bool is_running(ESPIFOperatingMode mode);
bool can_recieve_data(ESPIFOperatingMode mode);
void process_link_change(bool link_up, netif *netif);
void uart_input(uint8_t *data, size_t size, netif *netif);
void reset_intron();
