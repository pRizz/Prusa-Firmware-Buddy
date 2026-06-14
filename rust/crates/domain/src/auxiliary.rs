#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        BoardKind, BootloaderMode, Feature, FeatureSet, InvariantError, McuKind, PrinterKind,
        ProductProfile,
    };

    fn valid_row_id() -> AuxiliaryParityRowId {
        AuxiliaryParityRowId::parse("mmu2-availability-reporting-stub")
            .expect("test row ID is valid")
    }

    fn auxiliary_parity_input(
        evidence_class: BusEvidenceClass,
        proof_scope: AuxiliaryProofScope,
    ) -> AuxiliaryParityContractInput {
        AuxiliaryParityContractInput {
            row_id: valid_row_id(),
            evidence_class,
            proof_scope,
        }
    }

    fn profile(
        printer: PrinterKind,
        board: BoardKind,
        mcu: McuKind,
        bootloader_mode: BootloaderMode,
        features: FeatureSet,
    ) -> ProductProfile {
        ProductProfile::new(printer, board, mcu, bootloader_mode, features)
            .expect("test profile is part of the supported reference matrix")
    }

    #[test]
    fn parses_auxiliary_parity_row_ids() {
        // Arrange
        let valid_id = "mmu2-availability-reporting-stub";
        let oversized_id = "a".repeat(97);
        let invalid_ids = [
            "",
            ".",
            "..",
            "../mmu2",
            "mmu2\\availability",
            "mmu2 availability",
            "mmu2\navailability",
        ];

        // Act
        let valid_result = AuxiliaryParityRowId::parse(valid_id);
        let oversized_result = AuxiliaryParityRowId::parse(oversized_id);
        let invalid_results = invalid_ids.map(AuxiliaryParityRowId::parse);

        // Assert
        assert!(matches!(
            valid_result,
            Ok(row_id) if row_id.as_str() == valid_id
        ));
        assert_eq!(
            invalid_results[0],
            Err(InvariantError::EmptyAuxiliaryParityRowId)
        );
        assert!(invalid_results[1..].iter().all(Result::is_err));
        assert_eq!(
            oversized_result,
            Err(InvariantError::InvalidAuxiliaryParityRowId)
        );
    }

    #[test]
    fn classifies_bus_evidence_locality() {
        // Arrange
        let local_evidence = "manifest-check";
        let hardware_evidence = "hardware-smoke";
        let manual_evidence = "manual-hardware-required";

        // Act
        let local_result = BusEvidenceClass::parse(local_evidence);
        let hardware_result = BusEvidenceClass::parse(hardware_evidence);
        let manual_result = BusEvidenceClass::parse(manual_evidence);

        // Assert
        assert!(matches!(
            local_result,
            Ok(evidence_class)
                if evidence_class.as_str() == local_evidence && evidence_class.is_local_proof()
        ));
        assert!(matches!(
            hardware_result,
            Ok(evidence_class)
                if evidence_class.as_str() == hardware_evidence
                    && !evidence_class.is_local_proof()
        ));
        assert!(matches!(
            manual_result,
            Ok(evidence_class)
                if evidence_class.as_str() == manual_evidence && !evidence_class.is_local_proof()
        ));
    }

    #[test]
    fn rejects_non_local_bus_evidence_as_local_proof() {
        // Arrange
        let non_local_evidence_classes = [
            BusEvidenceClass::SimulatorFlow,
            BusEvidenceClass::HardwareSmoke,
            BusEvidenceClass::ManualHardwareRequired,
        ];

        // Act
        let results = non_local_evidence_classes.map(|evidence_class| {
            AuxiliaryParityContract::new(auxiliary_parity_input(
                evidence_class,
                AuxiliaryProofScope::Local,
            ))
        });

        // Assert
        assert!(
            results
                .iter()
                .all(|result| *result == Err(InvariantError::InvalidAuxiliaryParityContract))
        );
    }

    #[test]
    fn parses_all_auxiliary_runtime_states() {
        // Arrange
        let raw_states = [
            "bootloader",
            "unavailable",
            "active",
            "stopped",
            "updating",
            "update-failed",
            "communication-fault",
            "unknown-reference-deferred",
        ];

        // Act
        let results = raw_states.map(AuxiliaryRuntimeState::parse);

        // Assert
        assert!(results.iter().all(Result::is_ok));
    }

    #[test]
    fn keeps_firmware_image_sources_named_only() {
        // Arrange
        let raw_sources = [
            "DWARF_BINARY_PATH",
            "MODULARBED_BINARY_PATH",
            "XBUDDY_EXTENSION_BINARY_PATH",
            "/puppies/fw-dwarf.bin",
            "/puppies/fw-modularbed.bin",
            "/puppies/fw-xbuddy-extension.bin",
            "/mmu/fw.bin",
        ];

        // Act
        let results = raw_sources.map(FirmwareImageSource::parse);

        // Assert
        for (raw_source, result) in raw_sources.into_iter().zip(results) {
            assert!(matches!(result, Ok(source) if source.as_str() == raw_source));
        }
    }

    #[test]
    fn validates_modbus_unit_identity_bounds() {
        // Arrange
        let xbuddy_extension_mmu_bridge_unit = 220;

        // Act
        let valid_result = ModbusUnitIdentity::new(xbuddy_extension_mmu_bridge_unit);
        let zero_result = ModbusUnitIdentity::new(0);
        let broadcast_overflow_result = ModbusUnitIdentity::new(248);

        // Assert
        assert!(matches!(
            valid_result,
            Ok(identity) if identity.as_u8() == xbuddy_extension_mmu_bridge_unit
        ));
        assert_eq!(zero_result, Err(InvariantError::InvalidModbusUnitIdentity));
        assert_eq!(
            broadcast_overflow_result,
            Err(InvariantError::InvalidModbusUnitIdentity)
        );
    }

    #[test]
    fn parses_dock_identities() {
        // Arrange
        let raw_docks = ["DWARF_1", "DWARF_6", "MODULAR_BED", "XBUDDY_EXTENSION"];

        // Act
        let results = raw_docks.map(DockIdentity::parse);
        let unknown_result = DockIdentity::parse("UNKNOWN_DOCK");

        // Assert
        assert_eq!(
            results,
            [
                Ok(DockIdentity::Dwarf1),
                Ok(DockIdentity::Dwarf6),
                Ok(DockIdentity::ModularBed),
                Ok(DockIdentity::XBuddyExtension),
            ]
        );
        assert_eq!(unknown_result, Err(InvariantError::InvalidDockIdentity));
    }

    #[test]
    fn validates_tool_offset_identity_range() {
        // Arrange
        let first_tool = 1;
        let last_tool = 6;

        // Act
        let first_result = ToolOffsetIdentity::new(first_tool, ToolOffsetAxis::X);
        let last_result = ToolOffsetIdentity::new(last_tool, ToolOffsetAxis::Z);
        let zero_result = ToolOffsetIdentity::new(0, ToolOffsetAxis::Y);
        let overflow_result = ToolOffsetIdentity::new(7, ToolOffsetAxis::Y);

        // Assert
        assert!(matches!(
            first_result,
            Ok(identity)
                if identity.tool_number() == first_tool && identity.axis() == ToolOffsetAxis::X
        ));
        assert!(matches!(
            last_result,
            Ok(identity)
                if identity.tool_number() == last_tool && identity.axis() == ToolOffsetAxis::Z
        ));
        assert_eq!(zero_result, Err(InvariantError::InvalidToolOffsetIdentity));
        assert_eq!(
            overflow_result,
            Err(InvariantError::InvalidToolOffsetIdentity)
        );
    }

    #[test]
    fn parses_mmu_transport_states() {
        // Arrange
        let raw_states = [
            "puppy-modbus-bridge",
            "direct-uart",
            "bootloader",
            "updating",
            "update-failed",
            "communication-fault",
        ];

        // Act
        let results = raw_states.map(MmuTransportState::parse);

        // Assert
        assert!(results.iter().all(Result::is_ok));
    }

    #[test]
    fn parses_update_modes_and_modbus_request_kinds() {
        // Arrange
        let update_modes = [
            "startup-flash",
            "skip-flash",
            "prebuilt-path",
            "firmware-descriptor",
            "crash-dump-download",
            "mmu-bootloader-update",
        ];
        let request_kinds = [
            "read-input",
            "read-holding",
            "write-holding",
            "write-coil",
            "read-fifo",
            "query",
            "command",
        ];

        // Act
        let update_results = update_modes.map(AuxiliaryUpdateMode::parse);
        let request_results = request_kinds.map(ModbusRequestKind::parse);

        // Assert
        assert!(update_results.iter().all(Result::is_ok));
        assert!(request_results.iter().all(Result::is_ok));
    }

    #[test]
    fn gates_auxiliary_controller_by_product_profile() {
        // Arrange
        let dwarf_profile = profile(
            PrinterKind::Xl,
            BoardKind::Dwarf,
            McuKind::Stm32G070RbT6,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::Dwarf]),
        );
        let dwarf_input = AuxiliaryControllerContractInput {
            profile: dwarf_profile.clone(),
            controller_kind: AuxiliaryControllerKind::Dwarf,
        };
        let xbuddy_extension_input = AuxiliaryControllerContractInput {
            profile: dwarf_profile,
            controller_kind: AuxiliaryControllerKind::XBuddyExtension,
        };

        // Act
        let dwarf_result = AuxiliaryControllerContract::new(dwarf_input);
        let mismatch_result = AuxiliaryControllerContract::new(xbuddy_extension_input);

        // Assert
        assert!(matches!(
            dwarf_result,
            Ok(contract) if contract.controller_kind() == AuxiliaryControllerKind::Dwarf
        ));
        assert_eq!(
            mismatch_result,
            Err(InvariantError::UnsupportedAuxiliaryController)
        );
    }

    #[test]
    fn parses_controller_fault_classes() {
        // Arrange
        let raw_faults = [
            "fingerprint-mismatch",
            "modbus-communication",
            "dwarf-tmc",
            "modular-bed-panic",
            "xbuddy-extension-mmu-bridge",
        ];

        // Act
        let results = raw_faults.map(ControllerFaultClass::parse);

        // Assert
        assert_eq!(
            results,
            [
                Ok(ControllerFaultClass::FingerprintMismatch),
                Ok(ControllerFaultClass::ModbusCommunication),
                Ok(ControllerFaultClass::DwarfTmc),
                Ok(ControllerFaultClass::ModularBedPanic),
                Ok(ControllerFaultClass::XBuddyExtensionMmuBridge),
            ]
        );
    }
}
