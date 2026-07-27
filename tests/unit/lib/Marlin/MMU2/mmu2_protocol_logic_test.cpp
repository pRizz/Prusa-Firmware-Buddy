#include "catch2/catch.hpp"

#include "mmu2_supported_version.h"
#include "protocol_logic.h"
#include "stubs/stub_interfaces.h"

#include <deque>
#include <regex>
#include <string>

#define supportedMmuFWVersionMajor    3
#define supportedMmuFWVersionMinor    0
#define supportedMmuFWVersionRevision 3
#define supportedMmuFWVersionBuild    895

static_assert(MMU2::mmuVersionMajor == 3);
static_assert(MMU2::mmuVersionMinor == 0);
static_assert(MMU2::mmuVersionPatch == 3);

#define xstr(s) Str(s)
#define Str(s)  #s

static constexpr uint8_t MMU2_TOOL_CHANGE_LOAD_LENGTH = 30; // mm
static constexpr uint8_t PULLEY_SLOW_FEED_RATE = 20; // mm/s

using PST = MMU2::ProtocolLogic::State;
using PSC = MMU2::ProtocolLogic::Scope;

bool StepAndCheckState(MMU2::ProtocolLogic &pl, const std::string_view rxContent, PST plState, PSC plScope, MMU2::StepStatus stepStatus, const std::string_view txContent) {
    mmu2SerialSim.SetRxBuffCRC(rxContent);
    auto sr = pl.Step();
    CHECKED_ELSE(pl.state == plState) {
        return false;
    }
    CHECKED_ELSE(sr == stepStatus) {
        return false;
    }
    CHECKED_ELSE(pl.currentScope == plScope) {
        return false;
    }

    if (txContent.empty()) {
        CHECKED_ELSE(mmu2SerialSim.txbuffQ.empty()) {
            return false;
        }
    } else {
        CHECKED_ELSE(!mmu2SerialSim.txbuffQ.empty()) {
            return false;
        }
        CHECKED_ELSE(mmu2SerialSim.TxBuffMatchesCRC(txContent)) {
            return false;
        }
    }
    mmu2SerialSim.txbuffQ.clear();
    return true;
}

bool StepAndCheckState2(MMU2::ProtocolLogic &pl, const std::string_view rxContent, PST plState, MMU2::StepStatus stepStatus, const char *txContent0, const char *txContent1) {
    mmu2SerialSim.SetRxBuffCRC(rxContent);
    auto sr = pl.Step();
    CHECKED_ELSE(pl.state == plState) {
        return false;
    }
    CHECKED_ELSE(sr == stepStatus) {
        return false;
    }
    CHECKED_ELSE(mmu2SerialSim.txbuffQ.size() == 2) {
        return false;
    }
    CHECKED_ELSE(mmu2SerialSim.txbuffQ[0] == AppendCRC(txContent0)) {
        return false;
    }
    CHECKED_ELSE(mmu2SerialSim.txbuffQ[1] == AppendCRC(txContent1)) {
        return false;
    }

    mmu2SerialSim.txbuffQ.clear();
    return true;
}

void InitCommunication2(MMU2::ProtocolLogic &pl, std::string command);

void InitCommunication(MMU2::ProtocolLogic &pl) {
    using namespace MMU2;

    mmu2SerialSim.rxbuff.clear();
    mmu2SerialSim.txbuffQ.clear();

    // as it starts, the communication shall be disabled
    REQUIRE(pl.state == PST::Stopped);

    // stepping the state machine should keep it in Stopped state
    // and step result shall be ??? Processing?
    for (uint8_t i = 0; i < 10; ++i) {
        REQUIRE(StepAndCheckState(pl, "", PST::Stopped, PSC::Stopped, Processing, ""));
    }

    // enable the state machine
    pl.Start();
    REQUIRE(StepAndCheckState(pl, "", PST::InitSequence, PSC::StartSeq, Processing, "S0"));

    // step the machine a couple of times, waiting for response from the MMU
    for (uint8_t i = 0; i < 10; ++i) {
        REQUIRE(StepAndCheckState(pl, "", PST::InitSequence, PSC::StartSeq, Processing, ""));
        IncMillis(); // pretend one millisecond elapsed
    }

    InitCommunication2(pl, "X0");
}

template <typename T>
std::string RegisterReq(const MMU2::ProtocolLogic &pl, const T *arrayOfIndices, uint8_t i) {
    std::ostringstream s;
    s << "R" << std::hex << static_cast<uint32_t>(*(arrayOfIndices + i));
    std::string sx = s.str();
    return sx; // .str();
}

std::string RegisterReq8(const MMU2::ProtocolLogic &pl, uint8_t i) {
    return RegisterReq(pl, pl.regs8Addrs, i);
}

std::string RegisterReq16(const MMU2::ProtocolLogic &pl, uint8_t i) {
    return RegisterReq(pl, pl.regs16Addrs, i);
}

void QueryRegisters(MMU2::ProtocolLogic &pl, PSC scope = PSC::Idle, PSC terminalScope = PSC::Idle, MMU2::StepStatus terminalStatus = MMU2::Finished, const char *terminalMsg = "") {
    using namespace MMU2;
    // 8bit
    for (uint8_t i = 1; i < pl.regs8Count; ++i) {
        StepAndCheckState(pl, RegisterReq8(pl, i - 1) + " A0", PST::Running, scope, Processing, RegisterReq8(pl, i));
    }

    // transition between 8bit and 16bit regs
    StepAndCheckState(pl, RegisterReq8(pl, pl.regs8Count - 1) + " A0", PST::Running, scope, Processing, RegisterReq16(pl, 0));

    // 16 bit
    for (uint8_t i = 1; i < pl.regs16Count; ++i) {
        StepAndCheckState(pl, RegisterReq16(pl, i - 1) + " A0", PST::Running, scope, Processing, RegisterReq16(pl, i));
    }

    // finished
    StepAndCheckState(pl, RegisterReq16(pl, pl.regs16Count - 1) + " A0", PST::Running, terminalScope, terminalStatus, terminalMsg);
}

std::string SetRegister8(const MMU2::ProtocolLogic &pl, uint8_t i, uint8_t value) {
    std::ostringstream s;
    s << "W" << std::hex << (uint32_t)pl.initRegs8Addrs[i] << " " << std::hex << (uint32_t)value;
    return s.str();
}

std::string SetRegister8Ack(const MMU2::ProtocolLogic &pl, uint8_t i) {
    std::ostringstream s;
    s << "W" << std::hex << (uint32_t)pl.initRegs8Addrs[i] << " A";
    return s.str();
}

void InitialSetupRegisters(MMU2::ProtocolLogic &pl) {
    using namespace MMU2;
    // when adding a new init register it is necessary to add a StepAndCheckState line + set the register's correct value
    StepAndCheckState(pl, SetRegister8Ack(pl, 0), PST::InitSequence, PSC::StartSeq, Processing, SetRegister8(pl, 1, PULLEY_SLOW_FEED_RATE));
    // transition to fsensor
    StepAndCheckState(pl, SetRegister8Ack(pl, 1), PST::InitSequence, PSC::StartSeq, Processing, "f0");
}

void InitCommunication2(MMU2::ProtocolLogic &pl, std::string command) {
    using namespace MMU2;
    // perform the init sequence
    StepAndCheckState(pl, "S0 A" xstr(supportedMmuFWVersionMajor), PST::InitSequence, PSC::StartSeq, Processing, "S1");
    IncMillis();
    StepAndCheckState(pl, "S1 A" xstr(supportedMmuFWVersionMinor), PST::InitSequence, PSC::StartSeq, Processing, "S2");
    IncMillis();
    StepAndCheckState(pl, "S2 A" xstr(supportedMmuFWVersionRevision), PST::InitSequence, PSC::StartSeq, Processing, "S3");
    IncMillis();
    StepAndCheckState(pl, "S3 A" xstr(supportedMmuFWVersionBuild), PST::InitSequence, PSC::StartSeq, Processing, SetRegister8(pl, 0, MMU2_TOOL_CHANGE_LOAD_LENGTH));

    InitialSetupRegisters(pl);

    IncMillis();
    StepAndCheckState(pl, "f0 A0", PST::Running, PSC::Idle, Processing, "Q0");
    IncMillis();
    StepAndCheckState(pl, command + " F0", PST::Running, PSC::Idle, Processing, RegisterReq8(pl, 0));
    QueryRegisters(pl);
    // we have successfully completed the init sequence
}

void IdleOperation(MMU2::ProtocolLogic &pl) {
    using namespace MMU2;
    // check for repeated queries while idle (protocol heartbeat)

    // FINDA query + response follows immediately
    IncMillis(heartBeatPeriod);
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Idle, Processing, "Q0"));
    REQUIRE(StepAndCheckState(pl, "X0 F0", PST::Running, PSC::Idle, Processing, RegisterReq8(pl, 0)));
    QueryRegisters(pl);

    IncMillis(heartBeatPeriod);

    // try several times more with longer timing
    for (int i = 0; i < 10; ++i) {
        REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Idle, Processing, "Q0"));

        // receive a response after 100ms - should reset the uart timeout
        IncMillis(MMU2::heartBeatPeriod / 3);
        // FINDA query + response follows immediately
        REQUIRE(StepAndCheckState(pl, "X0 F0", PST::Running, PSC::Idle, Processing, RegisterReq8(pl, 0)));
        QueryRegisters(pl);

        // waiting + not sending anything
        IncMillis(MMU2::heartBeatPeriod / 3);
        REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Idle, Finished, ""));

        // waiting + not sending anything
        IncMillis(MMU2::heartBeatPeriod / 3);
        REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Idle, Finished, ""));

        IncMillis(MMU2::heartBeatPeriod / 3 + 3); // avoid rounding errors
    }
}

void CommandOperation(MMU2::ProtocolLogic &pl, std::string cmdRq) {
    using namespace MMU2;

    REQUIRE_FALSE(mmu2SerialSim.txbuffQ.empty());
    REQUIRE(mmu2SerialSim.TxBuffMatchesCRC(cmdRq));
    mmu2SerialSim.txbuffQ.clear();
    IncMillis();

    // receive a response
    REQUIRE(StepAndCheckState(pl, cmdRq + " A", PST::Running, PSC::Command, Processing, ""));

    IncMillis(MMU2::heartBeatPeriod);

    // query command state
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Command, Processing, "Q0"));
    IncMillis();

    // receive a response and report fsensor state immediately
    REQUIRE(StepAndCheckState(pl, cmdRq + " P1", PST::Running, PSC::Command, Processing, "f0"));

    // receive a response and ask for register status immediately
    REQUIRE(StepAndCheckState(pl, "f0 A", PST::Running, PSC::Command, Processing, RegisterReq8(pl, 0)));
    // receive stats
    QueryRegisters(pl, PSC::Command, PSC::Command, Processing);

    IncMillis(MMU2::heartBeatPeriod);

    // query state
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Command, Processing, "Q0"));

    IncMillis();

    // receive a finish response
    REQUIRE(StepAndCheckState(pl, cmdRq + " F0", PST::Running, PSC::Idle, Finished, ""));
}

/// Verify the protocol_logic layer - sitting idle
TEST_CASE("Marlin::MMU2::ProtocolLogic Idle", "[Marlin][MMU2]") {
    using namespace MMU2;
    InitEnvironment(MMU2::FilamentState::NOT_PRESENT);
    ProtocolLogic pl(&mmu2Serial, MMU2_TOOL_CHANGE_LOAD_LENGTH, PULLEY_SLOW_FEED_RATE);

    InitCommunication(pl);
    IdleOperation(pl);
}

/// Verify the protocol_logic layer - command
TEST_CASE("Marlin::MMU2::ProtocolLogic Command", "[Marlin][MMU2]") {
    using namespace MMU2;
    InitEnvironment(MMU2::FilamentState::NOT_PRESENT);
    ProtocolLogic pl(&mmu2Serial, MMU2_TOOL_CHANGE_LOAD_LENGTH, PULLEY_SLOW_FEED_RATE);

    InitCommunication(pl);

    // cycle through all slots to simulate regular behavior
    for (uint8_t slot = 0; slot < 5; ++slot) {
        // send a command
        pl.ToolChange(slot);
        char expectedMsgPrefix[3] = "T_";
        expectedMsgPrefix[1] = slot + '0';
        CommandOperation(pl, expectedMsgPrefix);
        // continue with an Idle state
        IdleOperation(pl);
    }
}

TEST_CASE("Marlin::MMU2::ProtocolLogic AsyncCommandRqQuery", "[Marlin][MMU2]") {
    using namespace MMU2;
    InitEnvironment(MMU2::FilamentState::NOT_PRESENT);
    ProtocolLogic pl(&mmu2Serial, MMU2_TOOL_CHANGE_LOAD_LENGTH, PULLEY_SLOW_FEED_RATE);
    InitCommunication(pl);

    IncMillis(MMU2::heartBeatPeriod);
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Idle, Processing, "Q0"));

    // now shoot an async command
    pl.ToolChange(1);
    // the state machine must not change, just record a new request
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Idle, Processing, ""));

    // add a response
    IncMillis();

    // it should process the response and after finishing the message sequence,
    // transfer into a Command state + send the command
    REQUIRE(StepAndCheckState(pl, "X0 F0", PST::Running, PSC::Idle, Processing, RegisterReq8(pl, 0)));
    QueryRegisters(pl, PSC::Idle, PSC::Command, Processing, "T1");
    REQUIRE(StepAndCheckState(pl, "T1 A", PST::Running, PSC::Command, Processing, ""));
}

/// Verify the protocol_logic layer - correctly handle an incoming command while waiting for a response from the MMU in Command state
TEST_CASE("Marlin::MMU2::ProtocolLogic AsyncCommandRqCommand", "[Marlin][MMU2]") {
    using namespace MMU2;
    InitEnvironment(MMU2::FilamentState::NOT_PRESENT);
    ProtocolLogic pl(&mmu2Serial, MMU2_TOOL_CHANGE_LOAD_LENGTH, PULLEY_SLOW_FEED_RATE);
    InitCommunication(pl);

    // start doing a command
    pl.ToolChange(1);

    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Command, Processing, "T1"));
    IncMillis();

    // receive a response
    REQUIRE(StepAndCheckState(pl, "T1 A", PST::Running, PSC::Command, Processing, ""));

    IncMillis(MMU2::heartBeatPeriod);
    // query command state
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Command, Processing, "Q0"));

    IncMillis();
    // simulate an error
    REQUIRE(StepAndCheckState(pl, "T1 E32771", PST::Running, PSC::Command, CommandError, "f0"));
    REQUIRE(StepAndCheckState(pl, "f0 A", PST::Running, PSC::Command, Processing, RegisterReq8(pl, 0)));
    QueryRegisters(pl, PSC::Command, PSC::Command, Processing);

    IncMillis(MMU2::heartBeatPeriod);
    // query command state and meanwhile push a button
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Command, Processing, "Q0"));

    pl.Button(2);

    IncMillis();
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Command, Processing, ""));

    REQUIRE(StepAndCheckState(pl, "T1 E32771", PST::Running, PSC::Command, CommandError, "f0"));
    REQUIRE(StepAndCheckState(pl, "f0 A", PST::Running, PSC::Command, Processing, RegisterReq8(pl, 0)));
    QueryRegisters(pl, PSC::Command, PSC::Command, Processing);
    // the next step shall be our async request
    // @@TODO this is not nice, ideally the B2 request shall be emitted immediately...
    // but it is nothing serious, 1ms delay poses no problem.
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Command, Processing, "B2"));
    IncMillis();
    REQUIRE(StepAndCheckState(pl, "B2 A", PST::Running, PSC::Command, Processing, "f0"));
}

TEST_CASE("Marlin::MMU2::ProtocolLogic AsyncCommandRqCommandReset", "[Marlin][MMU2]") {
    using namespace MMU2;
    InitEnvironment(MMU2::FilamentState::NOT_PRESENT);
    ProtocolLogic pl(&mmu2Serial, MMU2_TOOL_CHANGE_LOAD_LENGTH, PULLEY_SLOW_FEED_RATE);
    InitCommunication(pl);

    IncMillis(MMU2::heartBeatPeriod);
    // query command state and meanwhile push a button
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Idle, Processing, "Q0"));
    // simulate MMU reset
    REQUIRE(StepAndCheckState(pl, "X0 E8087", PST::Running, PSC::Idle, CommandError, RegisterReq8(pl, 0)));
    // we should be getting an auto-retry button
    pl.Button(1);

    // Finish running the Query (Q0)
    // The firmware will then activate the planned button request (B1)
    // StepStatus must remain in 'Processing' at this point since we are expecting a response later (B1 A)
    QueryRegisters(pl, PSC::Idle, PSC::Idle, Processing, "B1");
    IncMillis();

    // Here was the error - upon reception of B1 A we sent P0 but transferred into Finished.
    // We must remain in Processing...
    REQUIRE(StepAndCheckState(pl, "B1 A", PST::Running, PSC::Idle, Processing, RegisterReq8(pl, 0)));
    QueryRegisters(pl);
}

/// Verify the protocol_logic layer - recovery of a running command after a communication dropout
TEST_CASE("Marlin::MMU2::ProtocolLogic Recover Command", "[Marlin][MMU2]") {
    using namespace MMU2;
    InitEnvironment(MMU2::FilamentState::NOT_PRESENT);
    // @@TODO
}

TEST_CASE("Marlin::MMU2::ProtocolLogic repeated comm link attempts", "[Marlin][MMU2]") {
    using namespace MMU2;
    InitEnvironment(MMU2::FilamentState::NOT_PRESENT);
    ProtocolLogic pl(&mmu2Serial, MMU2_TOOL_CHANGE_LOAD_LENGTH, PULLEY_SLOW_FEED_RATE);

    mmu2SerialSim.rxbuff.clear();
    mmu2SerialSim.txbuffQ.clear();

    pl.Start();
    REQUIRE(mmu2SerialSim.TxBuffMatchesCRC("S0"));
    pl.Step();

    for (uint8_t i = 0; i < 10; ++i) {
        mmu2SerialSim.txbuffQ.clear(); // pretend we sent the data
        IncMillis(MMU2::linkLayerTimeout);
        pl.Step();
        REQUIRE(mmu2SerialSim.TxBuffMatchesCRC("S0"));
    }
}

TEST_CASE("Marlin::MMU2::ProtocolLogic Previous command finished while a new one issued", "[Marlin][MMU2]") {
    using namespace MMU2;
    InitEnvironment(MMU2::FilamentState::NOT_PRESENT);
    ProtocolLogic pl(&mmu2Serial, MMU2_TOOL_CHANGE_LOAD_LENGTH, PULLEY_SLOW_FEED_RATE);
    InitCommunication(pl);

    // start doing a command
    pl.ToolChange(1);

    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Command, Processing, "T1"));
    IncMillis();

    // receive a response
    REQUIRE(StepAndCheckState(pl, "T1 A", PST::Running, PSC::Command, Processing, ""));
    IncMillis(MMU2::heartBeatPeriod);
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Command, Processing, "Q0"));
    IncMillis();
    // T1 finished
    REQUIRE(StepAndCheckState(pl, "T1 F", PST::Running, PSC::Idle, Finished, ""));
    IncMillis(MMU2::heartBeatPeriod);
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Idle, Processing, "Q0"));
    REQUIRE(StepAndCheckState(pl, "T1 F", PST::Running, PSC::Idle, Processing, RegisterReq8(pl, 0)));
    QueryRegisters(pl);
    IncMillis(MMU2::heartBeatPeriod);
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Idle, Processing, "Q0"));

    pl.ToolChange(0); // now issue another command

    // do a couple of steps just as if the response to Q0 still hasn't arrived
    for (uint8_t i = 0; i < 10; ++i) {
        IncMillis();
        REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Idle, Processing, ""));
    }

    // MMU finally responded
    REQUIRE(StepAndCheckState(pl, "T1 F", PST::Running, PSC::Idle, Processing, RegisterReq8(pl, 0)));
    IncMillis();
    // Previously, this has caused the caller to think we have finished the planned command!
    // Now fixed and the transition from Idle to Command is seamless and we remain in the Processing state
    // It should post the T0 command right away.
    QueryRegisters(pl, PSC::Idle, PSC::Command, Processing, "T0");
    // continues as a normal command
    REQUIRE(StepAndCheckState(pl, "T0 A", PST::Running, PSC::Command, Processing, ""));
}

TEST_CASE("Marlin::MMU2::ProtocolLogic ReadRegister", "[Marlin][MMU2]") {
    // At this moment ReadRegister can only occur in Idle mode.
    // It is not a limitation of the protocol but a safety precaution of the higher level of G-codes processing.
    using namespace MMU2;
    InitEnvironment(MMU2::FilamentState::NOT_PRESENT);
    ProtocolLogic pl(&mmu2Serial, MMU2_TOOL_CHANGE_LOAD_LENGTH, PULLEY_SLOW_FEED_RATE);
    InitCommunication(pl);
    IdleOperation(pl);

    // it should plan a generic request and serve it accordingly
    pl.ReadRegister(0);
    REQUIRE(!mmu2SerialSim.txbuffQ.empty());
    REQUIRE(mmu2SerialSim.TxBuffMatchesCRC("R0"));
    mmu2SerialSim.txbuffQ.clear();
    // step again and receive some response
    REQUIRE(StepAndCheckState(pl, "R0 A2", PST::Running, PSC::Idle, Finished, ""));

    IdleOperation(pl);
}

TEST_CASE("Marlin::MMU2::ProtocolLogic WriteRegister", "[Marlin][MMU2]") {
    using namespace MMU2;
    ProtocolLogic pl(&mmu2Serial, MMU2_TOOL_CHANGE_LOAD_LENGTH, PULLEY_SLOW_FEED_RATE);
    InitCommunication(pl);
    IdleOperation(pl);

    // it should plan a generic request and serve it accordingly
    pl.WriteRegister(9, 10);
    REQUIRE(!mmu2SerialSim.txbuffQ.empty());
    REQUIRE(mmu2SerialSim.txbuffQ[0] == AppendCRCWrite("W9 a"));
    mmu2SerialSim.txbuffQ.clear();
    // step again and receive some response
    REQUIRE(StepAndCheckState(pl, "W9 A", PST::Running, PSC::Idle, Finished, ""));

    IdleOperation(pl);
}

TEST_CASE("Marlin::MMU2::ProtocolLogic Interrupted", "[Marlin][MMU2]") {
    using namespace MMU2;
    InitEnvironment(MMU2::FilamentState::NOT_PRESENT);
    ProtocolLogic pl(&mmu2Serial, MMU2_TOOL_CHANGE_LOAD_LENGTH, PULLEY_SLOW_FEED_RATE);
    InitCommunication(pl);
    IdleOperation(pl);

    pl.ToolChange(0);
    std::string cmdRq("T0");

    REQUIRE_FALSE(mmu2SerialSim.txbuffQ.empty());
    REQUIRE(mmu2SerialSim.TxBuffMatchesCRC(cmdRq));
    mmu2SerialSim.txbuffQ.clear();
    IncMillis();
    REQUIRE(StepAndCheckState(pl, cmdRq + " A", PST::Running, PSC::Command, Processing, ""));
    IncMillis(MMU2::heartBeatPeriod);
    REQUIRE(StepAndCheckState(pl, "", PST::Running, PSC::Command, Processing, "Q0"));
    IncMillis();
    REQUIRE(StepAndCheckState(pl, cmdRq + " P1", PST::Running, PSC::Command, Processing, "f0"));
    REQUIRE(StepAndCheckState(pl, "f0 A", PST::Running, PSC::Command, Processing, RegisterReq8(pl, 0)));
    QueryRegisters(pl, PSC::Command, PSC::Command, Processing);
    IncMillis(MMU2::heartBeatPeriod);
    StepAndCheckState(pl, "", PST::Running, PSC::Command, Processing, "Q0");

    // cause a timeout
    IncMillis(MMU2::dataLayerTimeout * 2);
    REQUIRE(StepAndCheckState(pl, "", PST::InitSequence, PSC::StartSeq, Processing, "S0"));
    StepAndCheckState(pl, "S0 A" xstr(supportedMmuFWVersionMajor), PST::InitSequence, PSC::StartSeq, Processing, "S1");
    IncMillis();
    StepAndCheckState(pl, "S1 A" xstr(supportedMmuFWVersionMinor), PST::InitSequence, PSC::StartSeq, Processing, "S2");
    IncMillis();
    StepAndCheckState(pl, "S2 A" xstr(supportedMmuFWVersionRevision), PST::InitSequence, PSC::StartSeq, Processing, "S3");
    IncMillis();
    StepAndCheckState(pl, "S3 A" xstr(supportedMmuFWVersionBuild), PST::InitSequence, PSC::StartSeq, Processing, SetRegister8(pl, 0, MMU2_TOOL_CHANGE_LOAD_LENGTH));
    InitialSetupRegisters(pl);
    IncMillis();
    StepAndCheckState(pl, "f0 A0", PST::Running, PSC::Idle, Processing, "Q0");
    IncMillis();
    StepAndCheckState(pl, "X0 F0", PST::Running, PSC::Idle, Interrupted, "");

    // even though "interrupted" the state machine should continue querying the MMU like usually
    IncMillis(MMU2::heartBeatPeriod);
    StepAndCheckState(pl, "", PST::Running, PSC::Idle, Processing, "Q0");
}
