#include <cassert>

#include <freertos/mutex.hpp>
#include <puppies/Dwarf.hpp>

#include "adc.hpp"

namespace buddy::puppies {

using Lock = std::unique_lock<freertos::Mutex>;

float Dwarf::get_hotend_temp() {
    // Called from interrupts, so use the cached register value without locking.
    return static_cast<int16_t>(RegisterGeneralStatus.value.HotendMeasuredTemperature);
}

CommunicationStatus Dwarf::set_hotend_target_temp(float target) {
    Lock guard(*mutex);

    GeneralWrite.value.HotendRequestedTemperature = static_cast<uint16_t>(target);
    GeneralWrite.dirty = true;
    return CommunicationStatus::OK;
}

int Dwarf::get_heater_pwm() {
    // Called from interrupts, so use the cached register value without locking.
    return static_cast<float>(RegisterGeneralStatus.value.HotendPWMState);
}

bool Dwarf::is_picked() const {
    Lock guard(*mutex);
    return DiscreteGeneralStatus.value.is_picked;
}

bool Dwarf::is_parked() const {
    Lock guard(*mutex);
    return DiscreteGeneralStatus.value.is_parked;
}

bool Dwarf::is_button_up_pressed() const {
    Lock guard(*mutex);
    return DiscreteGeneralStatus.value.is_button_up_pressed;
}

bool Dwarf::is_button_down_pressed() const {
    Lock guard(*mutex);
    return DiscreteGeneralStatus.value.is_button_down_pressed;
}

bool Dwarf::is_selected() const {
    Lock guard(*mutex);
    return selected;
}

IFSensor::value_type Dwarf::get_tool_filament_sensor() {
    static_assert(static_cast<IFSensor::value_type>(AdcGet::undefined_value) == AdcGet::undefined_value);

    IFSensor::value_type value = tool_filament_sensor.load();
    if (value == AdcGet::undefined_value) {
        value = IFSensor::undefined_value;
    }
    return value;
}

int16_t Dwarf::get_mcu_temperature() {
    // Called from interrupts, so use the cached register value without locking.
    return static_cast<int16_t>(RegisterGeneralStatus.value.MCUTemperature);
}

int16_t Dwarf::get_board_temperature() {
    // Called from interrupts, so use the cached register value without locking.
    return static_cast<int16_t>(RegisterGeneralStatus.value.BoardTemperature);
}

float Dwarf::get_24V() {
    // Called from interrupts, so use the cached register value without locking.
    return RegisterGeneralStatus.value.system_24V_mV / 1000.0;
}

float Dwarf::get_heater_current() {
    // Called from interrupts, so use the cached register value without locking.
    return RegisterGeneralStatus.value.heater_current_mA / 1000.0;
}

void Dwarf::set_heatbreak_target_temp(int16_t target) {
    Lock guard(*mutex);

    GeneralWrite.value.HeatbreakRequestedTemperature = target;
    GeneralWrite.dirty = true;
}

void Dwarf::set_fan(uint8_t fan, uint16_t target) {
    assert(fan < NUM_FANS);
    // Some callers run in an interrupt; the refresh path applies this cached value under its lock.
    fan_pwm_desired[fan].store(target);
}

void Dwarf::set_cheese_led(uint8_t pwr_selected, uint8_t pwr_not_selected) {
    Lock guard(*mutex);

    GeneralWrite.value.led_pwm.selected = pwr_selected;
    GeneralWrite.value.led_pwm.not_selected = pwr_not_selected;
    GeneralWrite.dirty = true;
}

void Dwarf::set_status_led(dwarf_shared::StatusLed::Mode mode, uint8_t r, uint8_t g, uint8_t b) {
    Lock guard(*mutex);

    dwarf_shared::StatusLed status_led(mode, r, g, b);
    GeneralWrite.value.status_led[0] = status_led.get_reg_value(0);
    GeneralWrite.value.status_led[1] = status_led.get_reg_value(1);
    GeneralWrite.dirty = true;
}

void Dwarf::set_pid(float p, float i, float d) {
    Lock guard(*mutex);

    GeneralWrite.value.pid.p = p;
    GeneralWrite.value.pid.i = i;
    GeneralWrite.value.pid.d = d;
    GeneralWrite.dirty = true;
}

float Dwarf::get_heatbreak_temp() {
    // Called from interrupts, so use the cached register value without locking.
    return static_cast<int16_t>(RegisterGeneralStatus.value.HeatBreakMeasuredTemperature);
}

uint16_t Dwarf::get_heatbreak_fan_pwr() {
    // Called from interrupts, so use the cached register value without locking.
    return RegisterGeneralStatus.value.fan[1].pwm;
}

uint16_t Dwarf::get_fan_pwm(uint8_t fan_nr) const {
    // Called from interrupts, so use the cached register value without locking.
    return RegisterGeneralStatus.value.fan[fan_nr].pwm;
}

uint16_t Dwarf::get_fan_rpm(uint8_t fan_nr) const {
    // Called from interrupts, so use the cached register value without locking.
    return RegisterGeneralStatus.value.fan[fan_nr].rpm;
}

bool Dwarf::get_fan_rpm_ok(uint8_t fan_nr) const {
    // Called from interrupts, so use the cached register value without locking.
    return RegisterGeneralStatus.value.fan[fan_nr].is_rpm_ok;
}

uint16_t Dwarf::get_fan_state(uint8_t fan_nr) const {
    // Called from interrupts, so use the cached register value without locking.
    return RegisterGeneralStatus.value.fan[fan_nr].state;
}

} // namespace buddy::puppies
