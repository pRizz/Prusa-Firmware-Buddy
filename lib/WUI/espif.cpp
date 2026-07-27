#include "espif.h"
#include "espif_internal.hpp"

#include <algorithm>
#include <array>
#include <bit>
#include <cstring>
#include <cstdint>
#include <atomic>
#include <cassert>
#include <cinttypes>
#include <timing.h>
#include <mutex>
#include <memory>

#include <FreeRTOS.h>
#include <freertos/binary_semaphore.hpp>
#include <freertos/mutex.hpp>
#include <common/metric.h>
#include <common/crc32.h>
#include <device/peripherals_uart.hpp>
#include <device/peripherals.h>
#include <freertos/queue.hpp>
#include <task.h>
#include <semphr.h>
#include <buddy/ccm_thread.hpp>
#include <bsod.h>
#include <lwip/netifapi.h>

#include <buddy/esp_uart_dma_buffer_rx.hpp>
#include "data_exchange.hpp"
#include "pbuf_rx.h"
#include "scope_guard.hpp"
#include "wui.h"
#include <tasks.hpp>
#include <option/has_embedded_esp32.h>
#include <random.h>

#include <lwip/def.h>
#include <lwip/ethip6.h>
#include <lwip/etharp.h>
#include <lwip/sys.h>

#include <logging/log.hpp>

LOG_COMPONENT_DEF(ESPIF, logging::Severity::info);

static_assert(std::endian::native == std::endian::little, "STM<->ESP protocol assumes all involved CPUs are little endian.");
static_assert(ETHARP_HWADDR_LEN == 6);

/*
 * UART and other pin configuration for ESP01 module
 *
 * UART:                USART6
 * STM32 TX (ESP RX):   GPIOC, GPIO_PIN_6
 * STM32 RX (ESP TX):   GPIOC, GPIO_PIN_7
 * RESET:               GPIOC, GPIO_PIN_13
 * GPIO0:               GPIOE, GPIO_PIN_6
 * GPIO2:               not connected
 * CH_PD:               connected to board 3.3 V
 *
 * UART_DMA:           DMA2
 * UART_RX_STREAM      STREAM_1
 * UART_TX_STREAM      STREAM_6
 */

/*
 * ESP UART NIC
 *
 * This provides a LwIP NIC implementation on top of a simple UART protocol used to communicate MAC address, link
 * status and packets with ESP8266 attached on the other end of the UART. This requires custom FW running in the ESP
 * implementing the protocol.
 *
 * Known issues:
 * - This does not use netif state. All the state is kept in static varibles -> only on NIC is supported
 *   (Maybe it is worh encapsulating the state just for the sake of code clarity.)
 * - This runs at 1Mbaud even when ESP support 4.5Mbaud. There is some wierd coruption at higher speeds
 *   (ESP seems to miss part of the packet data)
 * - This does not offload checksum computation to ESP. Would be nice to enable parity and make the protocol more
 *   robust (i.e using some counter to match packet begin and end while ensuring no data is lost). Provided UART
 *   can be trusted not to alternate packet content the ESP would be able to compute packet checksums.
 *
 */

// NIC state
std::atomic<uint8_t> fw_version;
std::atomic<ESPIFOperatingMode> esp_operating_mode = ESPIF_UNINITIALIZED_MODE;
std::atomic<bool> associated = false;
std::atomic<netif *> active_esp_netif;
// 10 seconds (20 health-check loops spaced 500ms from each other)
std::atomic<uint8_t> init_countdown = 20;
std::atomic<bool> seen_intron = false;
std::atomic<bool> seen_pong = false;
std::atomic<bool> reset_parser = false;
// 0 means "unknown" or "not associated"
std::atomic<int8_t> signal_strength = 0;

// UART
std::atomic<bool> esp_detected;
// Have we seen the ESP alive at least once?
// (so we never ever report it as not there or no firmware or whatever).
std::atomic<bool> esp_was_ok = false;
uint8_t dma_buffer_rx[RX_BUFFER_LEN];
static size_t old_dma_pos = 0;
static freertos::Mutex uart_write_mutex;
static std::atomic<bool> uart_error_occured = false;
// Note: We never transmit more than one message so we might as well allocate statically.
TxMessage tx_message = {
    .intron = { 'U', 'N', '\x00', '\x01', '\x02', '\x03', '\x04', '\x05' },
    .type = 0,
    .byte = 0,
    .size = 0,
};

freertos::Mutex ScanData::get_ap_info_mutex {};
freertos::Queue<APInfo, 1> ScanData::ap_info_queue;

ScanData scan;

void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart) {
    if (huart == &uart_handle_for_esp) {
        uart_error_occured = true;
    }
}

// A semaphore by which an interrupt informs a (single) initiating task that
// its DMA transfer into the UART is finished.
//
// The atomic pointer to this is additional safety measure. This way we can
// prove (and double-check by asserts) that we get exactly one release for one
// request. Using some other, unrelated variable to make sure could be OK, but
// it would be significantly harder to prove that.
static freertos::BinarySemaphore tx_semaphore;
static std::atomic<freertos::BinarySemaphore *> tx_semaphore_active;

struct PBufDeleter {
    inline void operator()(pbuf *data) {
        pbuf_free(data);
    }
};
using pbuf_smart = std::unique_ptr<pbuf, PBufDeleter>;
using pbuf_variant = std::variant<pbuf *, pbuf_smart>;
static pbuf_variant tx_pbuf = nullptr; // only valid when tx_waiting == true

void espif_tx_callback() {
    if (auto *semaphore = tx_semaphore_active.exchange(nullptr); semaphore != nullptr) {
        semaphore->release_from_isr();
    }
}

static void espif_tx_update_metrics(uint32_t len) {
    METRIC_DEF(metric_esp_out, "esp_out", METRIC_VALUE_CUSTOM, 1000, METRIC_ENABLED);
    static uint32_t bytes_sent = 0;
    bytes_sent += len;
    metric_record_custom(&metric_esp_out, " sent=%" PRIu32 "i", bytes_sent);
}

// FIXME: This casually uses HAL_StatusTypeDef as a err_t, which works for the OK case (both 0), but it is kinda sketchy.
static err_t espif_tx_buffer(const uint8_t *data, size_t len) {
    // We are supposed to be under a mutex by the caller.
    [[maybe_unused]] auto old_semaphore = tx_semaphore_active.exchange(&tx_semaphore);
    assert(old_semaphore == nullptr);
    assert(can_be_used_by_dma(data));
    HAL_StatusTypeDef tx_result = HAL_UART_Transmit_DMA(&uart_handle_for_esp, data, len);

    if (tx_result == HAL_OK) {
        tx_semaphore.acquire();
    } else {
        [[maybe_unused]] auto withdrawn = tx_semaphore_active.exchange(nullptr);
        // It's the one we put in
        assert(withdrawn == &tx_semaphore);
    }

    return tx_result;
}

// FIXME: This casually uses HAL_StatusTypeDef as a err_t, which works for the OK case (both 0), but it is kinda sketchy.
[[nodiscard]] static err_t espif_tx_raw(uint8_t message_type, uint8_t message_byte, pbuf_variant p) {
    std::lock_guard lock { uart_write_mutex };

    const uint16_t size = std::visit([](const auto &pbuf) { return pbuf != nullptr ? pbuf->tot_len : 0; }, p);
    espif_tx_update_metrics(sizeof(tx_message) + size);
    tx_message.type = message_type;
    tx_message.byte = message_byte;
    tx_message.size = htons(size);

    auto tx_result = espif_tx_buffer((const uint8_t *)&tx_message, sizeof(tx_message));
    if (tx_result != HAL_OK) {
        log_error(ESPIF, "HAL_UART_Transmit_DMA() failed: %d", tx_result);
        return tx_result;
    }

    pbuf *tx_pbuf;
    if (std::holds_alternative<pbuf *>(p)) {
        tx_pbuf = std::get<pbuf *>(p);
    } else {
        tx_pbuf = std::get<pbuf_smart>(p).get();
    }

    while (tx_pbuf != nullptr) {
        // Predictive flow control - delay for ESP to load big enough buffer into UART driver
        // This is hotfix for not supplying buffers fast enough
        // Possibly, this slows down upload a little bit, but it is still faster than handling corruption.
        osDelay(1);
        tx_result = espif_tx_buffer((const uint8_t *)tx_pbuf->payload, tx_pbuf->len);
        if (tx_result != HAL_OK) {
            log_error(ESPIF, "HAL_UART_Transmit_DMA() failed: %d", tx_result);
            return tx_result;
        }
        tx_pbuf = tx_pbuf->next;
    }

    return tx_result;
}

// Note: Use this if you are absolutely sure that `buffer` is large enough to accomodate `data`.
[[nodiscard]] static FORCE_INLINE uint8_t *buffer_append_unsafe(uint8_t *buffer, const uint8_t *data, size_t size) {
    memcpy(buffer, data, size);
    return buffer + size;
}

[[nodiscard]] static err_t espif_tx_msg_clientconfig_v2(const char *ssid, const char *pass) {
    if (scan.is_running) {
        log_error(ESPIF, "Client config while running scan");
        return ERR_IF;
    }

    std::array<uint8_t, sizeof(tx_message.intron)> new_intron {};

    for (uint i = 0; i < 2; i++) {
        new_intron[i] = tx_message.intron[i];
    }

    for (uint i = 2; i < new_intron.size(); i++) {
        new_intron[i] = rand_u();
    }

    const uint8_t ssid_len = strlen(ssid);
    const uint8_t pass_len = strlen(pass);
    const uint16_t length = sizeof(new_intron) + sizeof(ssid_len) + ssid_len + sizeof(pass_len) + pass_len;

    auto pbuf = pbuf_smart { pbuf_alloc(PBUF_RAW, length, PBUF_RAM) };
    if (!pbuf) {
        log_error(ESPIF, "Low mem for client config");
        return ERR_MEM;
    }

    {
        assert(pbuf->tot_len == length);
        uint8_t *buffer = (uint8_t *)pbuf->payload;
        buffer = buffer_append_unsafe(buffer, new_intron.data(), sizeof(new_intron));
        buffer = buffer_append_unsafe(buffer, &ssid_len, sizeof(ssid_len));
        buffer = buffer_append_unsafe(buffer, (uint8_t *)ssid, ssid_len);
        buffer = buffer_append_unsafe(buffer, &pass_len, sizeof(pass_len));
        buffer = buffer_append_unsafe(buffer, (uint8_t *)pass, pass_len);
        assert(buffer == (uint8_t *)pbuf->payload + length);
    }

    err_t err = espif_tx_raw(MSG_CLIENTCONFIG_V2, 0, pbuf_variant { std::move(pbuf) });
    if (err == ERR_OK) {
        std::lock_guard lock { uart_write_mutex };
        std::copy_n(new_intron.begin(), sizeof(tx_message.intron), tx_message.intron);
        log_info(ESPIF, "Client config complete, have new intron");
    } else {
        log_error(ESPIF, "Client config failed: %d", static_cast<int>(err));
    }

    return err;
}

[[nodiscard]] static err_t espif_tx_msg_packet(pbuf *p) {
    constexpr uint8_t up = 1;
    return espif_tx_raw(MSG_PACKET_V2, up, p);
}

void espif_input_once(struct netif *netif) {
    if (!can_recieve_data(esp_operating_mode)) {
        return;
    }

    bool error = true;
    uart_error_occured.compare_exchange_strong(error, false);
    if (error) {
        // FIXME: There is a burst of these errors after the ESP boots, because bootloader prints
        //        on the serial line with different baudrate.
        //        It could help to only start receiving after some time, but we do not
        //        want to miss the initial packet from our ESP firmware.
        //        It doesn't matter too much besides spamming the log, so this remains
        //        to be fixed later...
        log_warning(ESPIF, "Recovering from UART error");

        __HAL_UART_DISABLE_IT(&uart_handle_for_esp, UART_IT_IDLE);
        auto enable_idle_iterrupt = ScopeGuard { [&] { __HAL_UART_ENABLE_IT(&uart_handle_for_esp, UART_IT_IDLE); } };

        HAL_UART_DeInit(&uart_handle_for_esp);
        if (const HAL_StatusTypeDef status = HAL_UART_Init(&uart_handle_for_esp); status != HAL_OK) {
            log_warning(ESPIF, "HAL_UART_Init() failed: %d", status);
            uart_error_occured = true;
            return;
        }
        assert(can_be_used_by_dma(dma_buffer_rx));
        if (const HAL_StatusTypeDef status = HAL_UART_Receive_DMA(&uart_handle_for_esp, (uint8_t *)dma_buffer_rx, RX_BUFFER_LEN); status != HAL_OK) {
            log_warning(ESPIF, "HAL_UART_Receive_DMA() failed: %d", status);
            uart_error_occured = true;
            return;
        }
        old_dma_pos = 0;

        return;
    }

    uint32_t dma_bytes_left = __HAL_DMA_GET_COUNTER(uart_handle_for_esp.hdmarx); // no. of bytes left for buffer full
    const size_t pos = sizeof(dma_buffer_rx) - dma_bytes_left;
    if (pos != old_dma_pos) {
        if (pos > old_dma_pos) {
            uart_input(&dma_buffer_rx[old_dma_pos], pos - old_dma_pos, netif);
        } else {
            uart_input(&dma_buffer_rx[old_dma_pos], sizeof(dma_buffer_rx) - old_dma_pos, netif);
            if (pos > 0) {
                uart_input(&dma_buffer_rx[0], pos, netif);
            }
        }
        old_dma_pos = pos;
        if (old_dma_pos == sizeof(dma_buffer_rx)) {
            old_dma_pos = 0;
        }
    }
}

[[nodiscard]] err_t espif_scan_start() {
    return espif::scan::start();
}

[[nodiscard]] err_t espif::scan::start() {
    // TODO: Validate that we can start a scan
    ::scan.is_running.exchange(true);

    const auto err = espif_tx_raw(MSG_SCAN_START, 0, nullptr);

    if (err == ERR_OK) {
        ::scan.prescan_op_mode = esp_operating_mode.exchange(ESPIF_SCANNING_MODE);
        ::scan.ap_count = 0;
    } else {
        ::scan.is_running.exchange(false);
    }
    return err;
}

bool espif_scan_is_running() { return espif::scan::is_running(); }
bool espif::scan::is_running() { return ::scan.is_running.load(std::memory_order_relaxed); }

[[nodiscard]] err_t espif_scan_stop() {
    return espif::scan::stop();
}

[[nodiscard]] err_t espif::scan::stop() {
    if (!::scan.is_running.load(std::memory_order_relaxed)) {
        log_error(ESPIF, "Unable to stop scan if none is running. Ivalid state: %d", esp_operating_mode.load());
        return ERR_IF;
    }

    const auto err = espif_tx_raw(MSG_SCAN_STOP, 0, nullptr);
    if (err == ERR_OK) {
        ::scan.is_running.exchange(false);
        auto expected = ESPIF_SCANNING_MODE;
        esp_operating_mode.compare_exchange_weak(expected, ::scan.prescan_op_mode);
    }
    return err;
}

[[nodiscard]] uint8_t espif_scan_get_ap_count() {
    return espif::scan::get_ap_count();
}

uint8_t espif::scan::get_ap_count() {
    return ::scan.ap_count.load();
}

[[nodiscard]] err_t espif_scan_get_ap_ssid(uint8_t index, uint8_t *ssid_buffer, uint8_t ssid_len, bool *needs_password) {
    if (ssid_buffer == nullptr || needs_password == nullptr) {
        return ERR_IF;
    }
    return espif::scan::get_ap_info(index, std::span { ssid_buffer, ssid_len }, *needs_password);
}

[[nodiscard]] err_t espif::scan::get_ap_info(uint8_t index, std::span<uint8_t> buffer, bool &needs_password) {
    assert(index < ::scan.ap_count);
    assert(buffer.size() >= config_store_ns::wifi_max_ssid_len);
    std::lock_guard lock(ScanData::get_ap_info_mutex);
    ::scan.result.ssid = buffer;

    int tries = 4;

    err_t last_error = ERR_OK;
    APInfo info {};
    while (tries >= 0) {
        --tries;
        const auto err = espif_tx_raw(MSG_SCAN_AP_GET, index, nullptr);

        if (err != ERR_OK) {
            last_error = err;
            continue;
        }

        // There can be some old data in the queue if we just didn't make the timeout
        if (ScanData::ap_info_queue.try_receive(info, ScanData::SYNC_EVENT_TIMEOUT) && info.ap_index == index && info.ssid.data() == buffer.data()) {
            last_error = ERR_OK;
            break;
        } else {
            last_error = ERR_IF;
        }
    }

    if (last_error != ERR_OK) {
        return last_error;
    }
    needs_password = info.requires_password;
    return ERR_OK;
}

/**
 * @brief Send packet using ESPIF NIC
 *
 * @param netif Output NETIF handle
 * @param p buffer (chain) to send
 */
static err_t low_level_output([[maybe_unused]] struct netif *netif, struct pbuf *p) {
    if (!is_running(esp_operating_mode)) {
        log_error(ESPIF, "Cannot send packet, not in running mode.");
        return ERR_IF;
    }

    if (espif_tx_msg_packet(p) != ERR_OK) {
        log_error(ESPIF, "espif_tx_msg_packet() failed");
        return ERR_IF;
    }
    return ERR_OK;
}

void reset_intron() {
    log_debug(ESPIF, "Reset intron");
    std::lock_guard lock { uart_write_mutex };
    for (uint i = 2; i < sizeof(tx_message.intron); i++) {
        tx_message.intron[i] = i - 2;
    }
}

/**
 * @brief Initalize ESPIF network interface
 *
 * This initializes NET interface. This is supposed to be called at most once.
 *
 * @param netif Interface to initialize
 * @return err_t Possible error encountered during initialization
 */
err_t espif_init(struct netif *netif) {
    struct netif *previous = active_esp_netif.exchange(netif);
    assert(previous == nullptr);
    (void)previous; // Avoid warnings in release

    // Initialize lwip netif
    netif->name[0] = 'w';
    netif->name[1] = 'l';
    netif->output = etharp_output;
#if LWIP_IPV6
    netif->output_ip6 = ethip6_output;
#endif
    netif->linkoutput = low_level_output;

    // LL init
    netif->hwaddr_len = 0;
    // TODO: This assumes LwIP can live with hwaddr not being set until ESP reports it
    netif->mtu = 1500;
    netif->flags = NETIF_FLAG_BROADCAST | NETIF_FLAG_ETHARP;

    reset_intron();
    return ERR_OK;
}

/**
 * @brief Ask ESP to join AP
 *
 * This, just sends join command. It is not a big problem if network interface is not configured.
 *
 * @param ssid SSID
 * @param pass Password
 * @return err_t
 */
err_t espif_join_ap(const char *ssid, const char *pass) {
    if (!is_running(esp_operating_mode)) {
        return ERR_IF;
    }
    log_info(ESPIF, "Joining AP %s:*(%d)", ssid, strlen(pass));

    err_t err = espif_tx_msg_clientconfig_v2(ssid, pass);

    switch (err) {
    case ERR_OK:
        esp_operating_mode = ESPIF_CONNECTING_AP;
        break;
    case ERR_MEM:
        // Wait in error state for another reset, done by the wui.cpp on too
        // long inactivity. Once it resets us, we'll try again from the start.
        esp_operating_mode = ESPIF_ERROR;
        break;
    default:
        break;
    }

    return err;
}

bool espif_tick() {
    const auto current_init = init_countdown.load();
    if (current_init > 0) {
        // In theory, this load - condition - store sequence is racy.
        // Nevertheless, we have only one thread that writes in there and it's
        // atomic to allow reading things at the same time.
        init_countdown.store(current_init - 1);
    }

    if (espif_link()) {
        const bool was_alive = seen_pong.exchange(false);
        seen_intron.store(false);
        if (is_running(esp_operating_mode)) {
            log_debug(ESPIF, "Ping ESP");
            // Poke the ESP somewhat to see if it's still alive and provoke it to
            // do some activity during next round.
            std::ignore = espif_tx_msg_packet(nullptr);
        }
        return was_alive;
    }

    return false;
}
