#include "ModbusProtocol.hpp"

namespace modbus::ModbusProtocol {

extern const uint16_t crc_table[];

uint16_t CalculateChecksum(ModbusBuffer *pBuffer, uint32_t dataSize) {
    uint16_t crc = 0xFFFF;
    for (uint32_t i = 0; i < dataSize; i++) {
        uint8_t tmp = static_cast<uint8_t>((*pBuffer)[i] ^ crc);
        crc >>= 8;
        crc ^= crc_table[tmp];
    }

    return crc;
}

} // namespace modbus::ModbusProtocol
