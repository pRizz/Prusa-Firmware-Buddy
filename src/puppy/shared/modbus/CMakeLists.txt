target_sources(
  firmware
  PRIVATE ModbusBuffer.cpp
          ModbusProtocol.cpp
          ModbusRegisterDictionary.cpp
          ModbusTask.cpp
          modbus_state.cpp
  )
