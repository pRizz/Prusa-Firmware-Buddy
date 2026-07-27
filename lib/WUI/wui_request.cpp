#include "wui.h"

#include "netdev.h"
#include "netif_settings.h"
#include "wui_api.h"

#include <option/mdns.h>
#if MDNS()
    #include "mdns/mdns.h"
    #include <lwip/igmp.h>
#endif

#include <cassert>
#include <config_store/store_instance.hpp>
#include <cstring>
#include <lwip/netif.h>
#include <random.h>

namespace {

char password_charset[] = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789";

template <class F>
void modify_flag(uint32_t netdev_id, F &&modify) {
    assert(netdev_id == NETDEV_ETH_ID || netdev_id == NETDEV_ESP_ID);

    const uint8_t old_flag = netdev_id == NETDEV_ETH_ID ? config_store().lan_flag.get() : config_store().wifi_flag.get();
    const uint8_t new_flag = modify(old_flag);
    if (old_flag == new_flag) {
        return;
    }

    if (netdev_id == NETDEV_ETH_ID) {
        config_store().lan_flag.set(new_flag);
    } else {
        config_store().wifi_flag.set(new_flag);
    }
    notify_reconfigure();
}

} // namespace

void wui_request_init_password() {
    if (!strcmp(config_store().prusalink_password.get().data(), "")) {
        char password[config_store_ns::pl_password_size] = { 0 };
        wui_generate_password(password, config_store_ns::pl_password_size);
        wui_store_password(password, config_store_ns::pl_password_size);
    }
}

#if MDNS()
void wui_request_init_mdns(netif *iface) {
    iface->flags |= NETIF_FLAG_IGMP;
    igmp_start(iface);
    mdns_resp_add_netif(iface);
    if (config_store().prusalink_enabled.get() == 1) {
        mdns_resp_add_service_prusalink(iface);
    }
}
#endif

void wui_generate_password(char *password, uint32_t length) {
    const uint32_t charset_length = sizeof(password_charset) / sizeof(char) - 1;
    uint32_t index = 0;

    while (index < length - 1) {
        uint32_t random = 0;
        if (!rand_u_secure(&random)) {
            password[0] = 0;
            return;
        }
        password[index++] = password_charset[random % charset_length];
    }
    password[index] = 0;
}

void wui_store_password(char *password, uint32_t length) {
    config_store().prusalink_password.set(password, length);
}

const char *wui_get_password() {
    return config_store().prusalink_password.get_c_str();
}

void netdev_set_active_id(uint32_t netdev_id) {
    assert(netdev_id <= NETDEV_COUNT);

    const auto target = static_cast<uint8_t>(netdev_id & 0xFF);
    if (config_store().active_netdev.get() != target) {
        config_store().active_netdev.set(target);
        notify_reconfigure();
    }
}

void netdev_set_static(uint32_t netdev_id) {
    modify_flag(netdev_id, [](uint8_t flag) -> uint8_t {
        CHANGE_FLAG_TO_STATIC(flag);
        TURN_FLAG_ON(flag);
        return flag;
    });
}

void netdev_set_dhcp(uint32_t netdev_id) {
    modify_flag(netdev_id, [](uint8_t flag) -> uint8_t {
        CHANGE_FLAG_TO_DHCP(flag);
        TURN_FLAG_ON(flag);
        return flag;
    });
}

void netdev_set_enabled(const uint32_t netdev_id, const bool enabled) {
    modify_flag(netdev_id, [enabled](uint8_t flag) -> uint8_t {
        if (enabled) {
            TURN_FLAG_ON(flag);
        } else {
            TURN_FLAG_OFF(flag);
        }
        return flag;
    });
}

bool netdev_is_enabled([[maybe_unused]] const uint32_t netdev_id) {
    const uint8_t flag = config_store().wifi_flag.get();
    return IS_LAN_ON(flag);
}

netdev_ip_obtained_t netdev_get_ip_obtained_type(uint32_t netdev_id) {
    if (netdev_id >= NETDEV_COUNT) {
        return NETDEV_DHCP;
    }

    uint8_t flag_value = 0;
    modify_flag(netdev_id, [&flag_value](uint8_t flag) {
        flag_value = flag;
        return flag;
    });
    return IS_LAN_DHCP(flag_value) ? NETDEV_DHCP : NETDEV_STATIC;
}
