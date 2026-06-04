#[cfg(test)]
mod tests {
    use super::*;

    fn all_safety_flows() -> [SafetyFlow; 12] {
        [
            SafetyFlow::ThermalTransition,
            SafetyFlow::MotionSafeOutput,
            SafetyFlow::Selftest,
            SafetyFlow::Calibration,
            SafetyFlow::CrashDetection,
            SafetyFlow::PowerPanic,
            SafetyFlow::EmergencyStop,
            SafetyFlow::FatalBoundary,
            SafetyFlow::CrashDump,
            SafetyFlow::Watchdog,
            SafetyFlow::Recovery,
            SafetyFlow::ProbeLoadcellClassification,
        ]
    }

    #[test]
    fn every_safety_flow_names_retained_source_paths() {
        // Arrange
        let flows = all_safety_flows();

        // Act
        let surfaces = flows.map(classify_safety_flow);

        // Assert
        assert!(
            surfaces
                .iter()
                .all(|surface| !surface.source_paths.is_empty())
        );
    }

    #[test]
    fn fatal_boundary_disallows_allocation_and_names_phase5_audit_surfaces() {
        // Arrange
        let flow = SafetyFlow::FatalBoundary;

        // Act
        let surface = classify_safety_flow(flow);
        let maybe_policy = surface.maybe_fatal_path_policy;

        // Assert
        assert_eq!(surface.action, SafetyAction::EnterFatalBoundary);
        assert_eq!(
            maybe_policy,
            Some(FatalPathPolicy {
                allows_allocation: false,
                preserves_crash_evidence: true,
                audit_surface_ids: &[
                    "panic-bsod-assert-boundary",
                    "crash-dump-memory-boundary",
                    "watchdog-boundary",
                ],
            })
        );
    }

    #[test]
    fn crash_dump_and_watchdog_keep_non_local_evidence_classification() {
        // Arrange
        let flows = [SafetyFlow::CrashDump, SafetyFlow::Watchdog];

        // Act
        let surfaces = flows.map(classify_safety_flow);

        // Assert
        for surface in surfaces {
            assert_ne!(surface.evidence_class, EvidenceClass::RustHostTest);
            assert!(matches!(
                surface.evidence_class,
                EvidenceClass::SimulatorFlow
                    | EvidenceClass::HardwareSmoke
                    | EvidenceClass::ManualHardwareRequired
            ));
        }
    }

    #[test]
    fn probe_loadcell_classification_preserves_cl007_reference_behavior() {
        // Arrange
        let flow = SafetyFlow::ProbeLoadcellClassification;

        // Act
        let surface = classify_safety_flow(flow);

        // Assert
        assert_eq!(surface.maybe_concern_id, Some("CL-007"));
        assert!(
            surface
                .source_paths
                .contains(&"src/common/probe_analysis.cpp")
        );
    }

    #[test]
    fn emergency_stop_maps_to_safe_output_action_and_source_paths() {
        // Arrange
        let flow = SafetyFlow::EmergencyStop;

        // Act
        let surface = classify_safety_flow(flow);

        // Assert
        assert!(matches!(
            surface.action,
            SafetyAction::EnterSafeOutput | SafetyAction::DisableMotionAndHeat
        ));
        assert!(
            surface
                .source_paths
                .contains(&"src/common/feature/emergency_stop/")
        );
    }
}
