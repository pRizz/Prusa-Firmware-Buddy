const FATAL_AUDIT_SURFACE_IDS: &[&str] = &[
    "panic-bsod-assert-boundary",
    "crash-dump-memory-boundary",
    "watchdog-boundary",
];

const THERMAL_SOURCE_PATHS: &[&str] = &[
    "lib/Marlin/",
    "src/common/marlin_server.cpp",
    "src/common/feature/safety_timer/",
    "src/common/safe_state.cpp",
];
const MOTION_SAFE_OUTPUT_SOURCE_PATHS: &[&str] = &[
    "lib/Marlin/",
    "src/common/marlin_server.cpp",
    "src/common/safe_state.cpp",
    "src/common/feature/emergency_stop/",
    "src/common/Pin.cpp",
];
const SELFTEST_SOURCE_PATHS: &[&str] = &["src/common/selftest/"];
const CALIBRATION_SOURCE_PATHS: &[&str] =
    &["src/common/selftest/", "src/common/probe_analysis.cpp"];
const CRASH_DETECTION_SOURCE_PATHS: &[&str] = &[
    "lib/Marlin/",
    "src/common/marlin_server.cpp",
    "src/common/power_panic.cpp",
];
const POWER_PANIC_SOURCE_PATHS: &[&str] = &[
    "src/common/power_panic.cpp",
    "src/common/marlin_server.cpp",
    "src/common/crash_dump/",
    "rust/crates/runtime-adapter/src/panic_boundary.rs",
];
const EMERGENCY_STOP_SOURCE_PATHS: &[&str] = &[
    "src/common/feature/emergency_stop/",
    "src/common/safe_state.cpp",
    "src/common/Pin.cpp",
];
const FATAL_BOUNDARY_SOURCE_PATHS: &[&str] = &[
    "src/common/safe_state.cpp",
    "src/common/crash_dump/",
    "src/common/Pin.cpp",
    "rust/crates/runtime-adapter/src/panic_boundary.rs",
];
const CRASH_DUMP_SOURCE_PATHS: &[&str] = &[
    "src/common/crash_dump/",
    "src/common/crash_dump/dump.cpp",
    "src/common/crash_dump/crash_dump_distribute.cpp",
    "rust/crates/runtime-adapter/src/panic_boundary.rs",
];
const WATCHDOG_SOURCE_PATHS: &[&str] = &[
    "src/common/crash_dump/dump.cpp",
    "src/common/wdt.cpp",
    "rust/crates/runtime-adapter/src/panic_boundary.rs",
];
const RECOVERY_SOURCE_PATHS: &[&str] = &[
    "src/common/marlin_server.cpp",
    "src/common/power_panic.cpp",
    "src/common/selftest/",
];
const PROBE_LOADCELL_SOURCE_PATHS: &[&str] = &[
    "src/common/probe_analysis.cpp",
    "src/common/selftest/",
    "src/common/random_hw.cpp",
    "ProjectOptions.cmake",
];

const FATAL_PATH_POLICY: FatalPathPolicy = FatalPathPolicy {
    allows_allocation: false,
    preserves_crash_evidence: true,
    audit_surface_ids: FATAL_AUDIT_SURFACE_IDS,
};

/// Evidence class for a Phase 6 safety policy claim.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum EvidenceClass {
    /// Manifest structure and source paths are checked locally.
    ManifestCheck,
    /// Source audit against retained firmware paths.
    SourceAudit,
    /// Static source audit against retained boundary paths.
    StaticSourceAudit,
    /// Host test evidence in the retained or mixed codebase.
    HostTest,
    /// Rust host test evidence for pure Rust classification only.
    RustHostTest,
    /// Simulator evidence is required for runtime flow behavior.
    SimulatorFlow,
    /// Hardware smoke evidence is required.
    HardwareSmoke,
    /// Manual hardware or failure-injection evidence is required.
    ManualHardwareRequired,
}

/// Named Phase 6 safety and recovery flow.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum SafetyFlow {
    /// Thermal safe-state and cooldown transitions.
    ThermalTransition,
    /// Motion and output safe-state handling.
    MotionSafeOutput,
    /// Selftest safety policy.
    Selftest,
    /// Calibration safety policy.
    Calibration,
    /// Crash-detection policy.
    CrashDetection,
    /// Power-panic stop, save, and resume policy.
    PowerPanic,
    /// Emergency-stop policy.
    EmergencyStop,
    /// Fatal redscreen/BSOD/assert boundary.
    FatalBoundary,
    /// Crash-dump boundary policy.
    CrashDump,
    /// Watchdog boundary policy.
    Watchdog,
    /// Recovery flow policy.
    Recovery,
    /// Probe/loadcell classifier policy.
    ProbeLoadcellClassification,
}

/// Pure Rust policy action for a retained safety flow.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum SafetyAction {
    /// Keep monitoring without changing retained firmware state.
    ContinueMonitoring,
    /// Hold motion while retained policy resolves the flow.
    HoldMotion,
    /// Disable heaters.
    DisableHeaters,
    /// Disable motors.
    DisableMotors,
    /// Disable motion and heat.
    DisableMotionAndHeat,
    /// Enter retained safe-output handling.
    EnterSafeOutput,
    /// Request retained recovery handling.
    RequestRecovery,
    /// Enter retained fatal-boundary handling.
    EnterFatalBoundary,
}

/// Fatal-path constraints inherited from the Phase 5 runtime-boundary audit.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct FatalPathPolicy {
    /// Whether allocation is allowed while handling this fatal path.
    pub allows_allocation: bool,
    /// Whether crash evidence must be preserved.
    pub preserves_crash_evidence: bool,
    /// Phase 5 audit surfaces that constrain the fatal path.
    pub audit_surface_ids: &'static [&'static str],
}

/// Pure policy surface for one retained safety flow.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct SafetyPolicySurface {
    /// Safety flow being classified.
    pub flow: SafetyFlow,
    /// Pure policy action label for the retained flow.
    pub action: SafetyAction,
    /// Highest required evidence class for the Phase 6 claim.
    pub evidence_class: EvidenceClass,
    /// Retained source paths backing this policy row.
    pub source_paths: &'static [&'static str],
    /// Known concern linked to this policy, when applicable.
    pub maybe_concern_id: Option<&'static str>,
    /// Fatal-path constraints, when this flow enters the retained fatal boundary.
    pub maybe_fatal_path_policy: Option<FatalPathPolicy>,
}

/// Classifies a safety flow into pure policy metadata.
pub const fn classify_safety_flow(flow: SafetyFlow) -> SafetyPolicySurface {
    match flow {
        SafetyFlow::ThermalTransition => SafetyPolicySurface {
            flow,
            action: SafetyAction::DisableHeaters,
            evidence_class: EvidenceClass::SourceAudit,
            source_paths: THERMAL_SOURCE_PATHS,
            maybe_concern_id: None,
            maybe_fatal_path_policy: None,
        },
        SafetyFlow::MotionSafeOutput => SafetyPolicySurface {
            flow,
            action: SafetyAction::EnterSafeOutput,
            evidence_class: EvidenceClass::HardwareSmoke,
            source_paths: MOTION_SAFE_OUTPUT_SOURCE_PATHS,
            maybe_concern_id: None,
            maybe_fatal_path_policy: None,
        },
        SafetyFlow::Selftest => SafetyPolicySurface {
            flow,
            action: SafetyAction::ContinueMonitoring,
            evidence_class: EvidenceClass::SourceAudit,
            source_paths: SELFTEST_SOURCE_PATHS,
            maybe_concern_id: None,
            maybe_fatal_path_policy: None,
        },
        SafetyFlow::Calibration => SafetyPolicySurface {
            flow,
            action: SafetyAction::HoldMotion,
            evidence_class: EvidenceClass::SourceAudit,
            source_paths: CALIBRATION_SOURCE_PATHS,
            maybe_concern_id: None,
            maybe_fatal_path_policy: None,
        },
        SafetyFlow::CrashDetection => SafetyPolicySurface {
            flow,
            action: SafetyAction::RequestRecovery,
            evidence_class: EvidenceClass::SourceAudit,
            source_paths: CRASH_DETECTION_SOURCE_PATHS,
            maybe_concern_id: None,
            maybe_fatal_path_policy: None,
        },
        SafetyFlow::PowerPanic => SafetyPolicySurface {
            flow,
            action: SafetyAction::RequestRecovery,
            evidence_class: EvidenceClass::ManualHardwareRequired,
            source_paths: POWER_PANIC_SOURCE_PATHS,
            maybe_concern_id: None,
            maybe_fatal_path_policy: None,
        },
        SafetyFlow::EmergencyStop => SafetyPolicySurface {
            flow,
            action: SafetyAction::DisableMotionAndHeat,
            evidence_class: EvidenceClass::HardwareSmoke,
            source_paths: EMERGENCY_STOP_SOURCE_PATHS,
            maybe_concern_id: None,
            maybe_fatal_path_policy: None,
        },
        SafetyFlow::FatalBoundary => SafetyPolicySurface {
            flow,
            action: SafetyAction::EnterFatalBoundary,
            evidence_class: EvidenceClass::StaticSourceAudit,
            source_paths: FATAL_BOUNDARY_SOURCE_PATHS,
            maybe_concern_id: None,
            maybe_fatal_path_policy: Some(FATAL_PATH_POLICY),
        },
        SafetyFlow::CrashDump => SafetyPolicySurface {
            flow,
            action: SafetyAction::EnterFatalBoundary,
            evidence_class: EvidenceClass::ManualHardwareRequired,
            source_paths: CRASH_DUMP_SOURCE_PATHS,
            maybe_concern_id: Some("CL-011"),
            maybe_fatal_path_policy: Some(FATAL_PATH_POLICY),
        },
        SafetyFlow::Watchdog => SafetyPolicySurface {
            flow,
            action: SafetyAction::EnterFatalBoundary,
            evidence_class: EvidenceClass::ManualHardwareRequired,
            source_paths: WATCHDOG_SOURCE_PATHS,
            maybe_concern_id: None,
            maybe_fatal_path_policy: Some(FATAL_PATH_POLICY),
        },
        SafetyFlow::Recovery => SafetyPolicySurface {
            flow,
            action: SafetyAction::RequestRecovery,
            evidence_class: EvidenceClass::SimulatorFlow,
            source_paths: RECOVERY_SOURCE_PATHS,
            maybe_concern_id: None,
            maybe_fatal_path_policy: None,
        },
        SafetyFlow::ProbeLoadcellClassification => SafetyPolicySurface {
            flow,
            action: SafetyAction::ContinueMonitoring,
            evidence_class: EvidenceClass::SourceAudit,
            source_paths: PROBE_LOADCELL_SOURCE_PATHS,
            maybe_concern_id: Some("CL-007"),
            maybe_fatal_path_policy: None,
        },
    }
}

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
