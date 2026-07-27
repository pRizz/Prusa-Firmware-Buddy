#include "backend.hpp"
#include <crc32.h>

namespace journal {
std::optional<Backend::CRCType> Backend::get_crc(const std::span<const uint8_t> data) {
    if (data.size() < CRC_SIZE) {
        return std::nullopt;
    }
    CRCType crc;
    memcpy(&crc, data.data(), CRC_SIZE);
    return crc;
}

std::optional<Backend::BankHeader> Backend::validate_bank_header(const std::span<const uint8_t> &data) {
    BankHeader header { 0, 0 };
    memcpy(&header, data.data(), BANK_HEADER_SIZE);
    auto crc_read = get_crc(data.subspan(BANK_HEADER_SIZE));
    if (!crc_read.has_value()) {
        return std::nullopt;
    }
    CRCType crc_computed = crc32_calc(reinterpret_cast<const uint8_t *>(&header), BANK_HEADER_SIZE);
    if (crc_read != crc_computed) {
        return std::nullopt;
    }
    return header;
}

Backend::CRCType Backend::calculate_crc(const Backend::ItemHeader &header, const std::span<const uint8_t> &data, CRCType crc) {
    crc = crc32_calc_ex(crc, reinterpret_cast<const uint8_t *>(&header), ITEM_HEADER_SIZE);
    crc = crc32_calc_ex(crc, data.data(), data.size());
    return crc;
}

bool Backend::fits_in_current_bank(uint16_t size) const {
    return get_free_space_in_current_bank() >= size;
}

uint16_t Backend::get_free_space_in_bank(Address address_in_bank) const {
    uint16_t used_space = current_address - get_bank_start_address(address_in_bank);
    return bank_size - used_space - 1; // 1 to prevent current_address going into next bank when you fit the item size just right
}

uint16_t Backend::get_bank_start_address(Address address_in_bank) const {
    return start_address + (address_in_bank < start_address + bank_size ? 0 : bank_size);
}

Backend::Address Backend::get_next_bank_start_address() const {
    if (current_address > start_address && current_address < start_address + bank_size) {
        return start_address + bank_size;
    } else {
        return start_address;
    }
}

Backend::BankSelector Backend::get_next_bank() {
    if (current_address > start_address && current_address < start_address + bank_size) {
        return BankSelector::Second;
    } else {
        return BankSelector::First;
    }
}

Backend::Address Backend::get_bank_start_address(const Backend::BankSelector selector) {
    return selector == BankSelector::First ? start_address : start_address + bank_size;
}

Backend::Transaction::Transaction(Transaction::Type type, Backend &backend)
    : backend(backend)
    , type(type)
    , last_item_address(type == Type::version_migration ? backend.current_next_address : backend.current_address) {
}

void Backend::Transaction::calculate_crc(Backend::Id id, const std::span<const uint8_t> &data) {
    const auto prev_crc = crc;

    ItemHeader header { .last_item = false, .id = id, .len = static_cast<uint16_t>(data.size()) };
    crc = Backend::calculate_crc(header, data, prev_crc);

    // If this item ends up being the last item, we need to calculate a different CRC for that
    header.last_item = true;
    last_item_crc = Backend::calculate_crc(header, data, prev_crc);
}
} // namespace journal
