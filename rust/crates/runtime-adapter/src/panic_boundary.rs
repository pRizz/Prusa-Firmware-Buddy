use crate::EvidenceClass;

const PANIC_EVIDENCE_STRINGS: &[&str] = &[
    "configASSERT",
    "_bsod",
    "fatal_error",
    "hal_panic",
    "panic-bsod-assert-boundary",
    "include/stm32f4_hal/FreeRTOSConfig.h",
    "include/stm32g0_hal/FreeRTOSConfig.h",
    "src/puppy/xbuddy_extension/config/FreeRTOSConfig.h",
];
const WATCHDOG_EVIDENCE_STRINGS: &[&str] = &[
    "watchdog-boundary",
    "watchdog_init",
    "HAL_watchdog_refresh",
    "wdt_iwdg_init",
    "wdt_iwdg_refresh",
    "wdt_iwdg_warning_cb",
    "src/common/wdt.cpp",
];
const CRASH_DUMP_EVIDENCE_STRINGS: &[&str] = &[
    "crash-dump-memory-boundary",
    "CrashCatcher_GetMemoryRegions",
    "CrashCatcher_DumpMemory",
    "RAM_ADDR",
    "CCMRAM_ADDR",
    "SCB_ADDR",
    "w25x_dump_start_address",
    "src/common/crash_dump/dump.cpp",
];
const PANIC_EVIDENCE_CLASSES: &[EvidenceClass] = &[
    EvidenceClass::ManifestCheck,
    EvidenceClass::StaticSourceAudit,
    EvidenceClass::RustHostTest,
    EvidenceClass::ManualHardwareRequired,
];
const WATCHDOG_EVIDENCE_CLASSES: &[EvidenceClass] = &[
    EvidenceClass::ManifestCheck,
    EvidenceClass::StaticSourceAudit,
    EvidenceClass::RustHostTest,
    EvidenceClass::HardwareSmoke,
    EvidenceClass::ManualHardwareRequired,
];
const CRASH_DUMP_EVIDENCE_CLASSES: &[EvidenceClass] = &[
    EvidenceClass::ManifestCheck,
    EvidenceClass::StaticSourceAudit,
    EvidenceClass::RustHostTest,
    EvidenceClass::SimulatorFlow,
    EvidenceClass::ManualHardwareRequired,
];
const CRASH_DUMP_MEMORY_REGIONS: &[CrashDumpMemoryRegion] = &[
    CrashDumpMemoryRegion::new("SCB", "SCB_ADDR", "SCB_SIZE"),
    CrashDumpMemoryRegion::new("SRAM", "RAM_ADDR", "RAM_SIZE"),
    CrashDumpMemoryRegion::new("CCMRAM", "CCMRAM_ADDR", "CCMRAM_SIZE"),
    CrashDumpMemoryRegion::new(
        "build identification",
        "version::project_build_identification",
        "sizeof(version::project_build_identification)",
    ),
];

/// Raw memory region named by the retained crash-dump collector.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CrashDumpMemoryRegion {
    name: &'static str,
    start_symbol: &'static str,
    size_symbol: &'static str,
}

impl CrashDumpMemoryRegion {
    /// Creates a crash-dump memory-region contract.
    pub const fn new(
        name: &'static str,
        start_symbol: &'static str,
        size_symbol: &'static str,
    ) -> Self {
        Self {
            name,
            start_symbol,
            size_symbol,
        }
    }

    /// Returns the region label.
    pub fn name(&self) -> &'static str {
        self.name
    }

    /// Returns the retained start symbol or expression.
    pub fn start_symbol(&self) -> &'static str {
        self.start_symbol
    }

    /// Returns the retained size symbol or expression.
    pub fn size_symbol(&self) -> &'static str {
        self.size_symbol
    }
}

/// Panic/assert/BSOD/fatal runtime-boundary contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PanicBoundary {
    audit_surface_id: &'static str,
    evidence_strings: &'static [&'static str],
    evidence_classes: &'static [EvidenceClass],
    fatal_convergence: &'static str,
}

impl PanicBoundary {
    /// Creates the retained panic boundary contract.
    pub fn retained() -> Self {
        Self {
            audit_surface_id: "panic-bsod-assert-boundary",
            evidence_strings: PANIC_EVIDENCE_STRINGS,
            evidence_classes: PANIC_EVIDENCE_CLASSES,
            fatal_convergence: "retained configASSERT, _bsod, fatal_error, and hal_panic paths must converge on firmware-fatal behavior without becoming recoverable Rust control flow",
        }
    }

    /// Returns the unsafe-boundary audit row for panic/assert behavior.
    pub fn audit_surface_id(&self) -> &'static str {
        self.audit_surface_id
    }

    /// Returns retained symbols and paths that prove the panic/assert boundary shape.
    pub fn evidence_strings(&self) -> &'static [&'static str] {
        self.evidence_strings
    }

    /// Returns local and non-local evidence classes for this panic contract.
    pub fn evidence_classes(&self) -> &'static [EvidenceClass] {
        self.evidence_classes
    }

    /// Returns the fatal-path convergence rule.
    pub fn fatal_convergence(&self) -> &'static str {
        self.fatal_convergence
    }
}

/// Watchdog runtime-boundary contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct WatchdogBoundary {
    audit_surface_id: &'static str,
    evidence_strings: &'static [&'static str],
    evidence_classes: &'static [EvidenceClass],
}

impl WatchdogBoundary {
    /// Creates the retained watchdog boundary contract.
    pub fn retained() -> Self {
        Self {
            audit_surface_id: "watchdog-boundary",
            evidence_strings: WATCHDOG_EVIDENCE_STRINGS,
            evidence_classes: WATCHDOG_EVIDENCE_CLASSES,
        }
    }

    /// Returns the unsafe-boundary audit row for watchdog behavior.
    pub fn audit_surface_id(&self) -> &'static str {
        self.audit_surface_id
    }

    /// Returns retained watchdog symbols and source paths.
    pub fn evidence_strings(&self) -> &'static [&'static str] {
        self.evidence_strings
    }

    /// Returns local and non-local evidence classes for this watchdog contract.
    pub fn evidence_classes(&self) -> &'static [EvidenceClass] {
        self.evidence_classes
    }
}

/// Crash-dump raw-memory runtime-boundary contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CrashDumpBoundary {
    audit_surface_id: &'static str,
    evidence_strings: &'static [&'static str],
    memory_regions: &'static [CrashDumpMemoryRegion],
    evidence_classes: &'static [EvidenceClass],
}

impl CrashDumpBoundary {
    /// Creates the retained crash-dump memory boundary contract.
    pub fn retained() -> Self {
        Self {
            audit_surface_id: "crash-dump-memory-boundary",
            evidence_strings: CRASH_DUMP_EVIDENCE_STRINGS,
            memory_regions: CRASH_DUMP_MEMORY_REGIONS,
            evidence_classes: CRASH_DUMP_EVIDENCE_CLASSES,
        }
    }

    /// Returns the unsafe-boundary audit row for crash-dump raw memory behavior.
    pub fn audit_surface_id(&self) -> &'static str {
        self.audit_surface_id
    }

    /// Returns retained crash-dump symbols and source paths.
    pub fn evidence_strings(&self) -> &'static [&'static str] {
        self.evidence_strings
    }

    /// Returns raw memory regions named by retained crash dump collection.
    pub fn memory_regions(&self) -> &'static [CrashDumpMemoryRegion] {
        self.memory_regions
    }

    /// Returns local and non-local evidence classes for this crash-dump contract.
    pub fn evidence_classes(&self) -> &'static [EvidenceClass] {
        self.evidence_classes
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn panic_boundary_names_retained_assert_and_fatal_paths() {
        // Arrange
        let boundary = PanicBoundary::retained();

        // Act
        let evidence = boundary.evidence_strings();

        // Assert
        assert!(evidence.contains(&"configASSERT"));
        assert!(evidence.contains(&"_bsod"));
        assert!(evidence.contains(&"fatal_error"));
        assert!(evidence.contains(&"hal_panic"));
    }

    #[test]
    fn watchdog_and_crash_dump_boundaries_name_audit_surfaces() {
        // Arrange
        let watchdog = WatchdogBoundary::retained();
        let crash_dump = CrashDumpBoundary::retained();

        // Act
        let watchdog_surface = watchdog.audit_surface_id();
        let crash_dump_surface = crash_dump.audit_surface_id();

        // Assert
        assert_eq!(watchdog_surface, "watchdog-boundary");
        assert_eq!(crash_dump_surface, "crash-dump-memory-boundary");
    }

    #[test]
    fn panic_watchdog_and_crash_dump_keep_non_local_evidence() {
        // Arrange
        let panic = PanicBoundary::retained();
        let watchdog = WatchdogBoundary::retained();
        let crash_dump = CrashDumpBoundary::retained();

        // Act
        let panic_evidence = panic.evidence_classes();
        let watchdog_evidence = watchdog.evidence_classes();
        let crash_dump_evidence = crash_dump.evidence_classes();

        // Assert
        assert!(panic_evidence.contains(&EvidenceClass::ManualHardwareRequired));
        assert!(watchdog_evidence.contains(&EvidenceClass::HardwareSmoke));
        assert!(crash_dump_evidence.contains(&EvidenceClass::SimulatorFlow));
    }

    #[test]
    fn crash_dump_boundary_names_raw_memory_regions() {
        // Arrange
        let crash_dump = CrashDumpBoundary::retained();

        // Act
        let regions = crash_dump.memory_regions();

        // Assert
        assert!(regions.iter().any(
            |region| region.start_symbol() == "RAM_ADDR" && region.size_symbol() == "RAM_SIZE"
        ));
        assert!(
            regions
                .iter()
                .any(|region| region.start_symbol() == "CCMRAM_ADDR"
                    && region.size_symbol() == "CCMRAM_SIZE")
        );
    }
}
