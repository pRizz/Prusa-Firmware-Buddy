use crate::EvidenceClass;

const STATIC_ONLY_EVIDENCE_CLASSES: &[EvidenceClass] = &[
    EvidenceClass::ManifestCheck,
    EvidenceClass::StaticSourceAudit,
    EvidenceClass::RustHostTest,
    EvidenceClass::ManualHardwareRequired,
];
const HEAP_BACKED_EVIDENCE_CLASSES: &[EvidenceClass] = &[
    EvidenceClass::ManifestCheck,
    EvidenceClass::StaticSourceAudit,
    EvidenceClass::RustHostTest,
    EvidenceClass::SimulatorFlow,
    EvidenceClass::HardwareSmoke,
    EvidenceClass::ManualHardwareRequired,
];
const STATIC_ONLY_EVIDENCE_PATHS: &[&str] = &[
    "src/puppy/xbuddy_extension/config/FreeRTOSConfig.h",
    "configSUPPORT_DYNAMIC_ALLOCATION 0",
    "configSUPPORT_STATIC_ALLOCATION 1",
];
const HEAP_BACKED_EVIDENCE_PATHS: &[&str] = &[
    "include/stm32f4_hal/FreeRTOSConfig.h",
    "include/stm32g0_hal/FreeRTOSConfig.h",
    "configTOTAL_HEAP_SIZE",
    "._user_heap_stack",
];

/// Runtime allocation assumption exposed to later firmware adapters.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum AllocatorAssumption {
    /// Runtime contracts require retained static allocation only.
    StaticOnly,
    /// Runtime contracts allow a bounded retained heap.
    HeapBacked,
}

/// Error returned when allocator facts cannot become a typed boundary.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AllocatorBoundaryError {
    /// A heap-backed runtime with zero heap bytes cannot satisfy the contract.
    ZeroHeapSize,
}

/// Allocator and heap boundary contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct AllocatorBoundary {
    assumption: AllocatorAssumption,
    maybe_heap_size_bytes: Option<usize>,
    audit_surface_id: &'static str,
    linker_section_name: &'static str,
    evidence_paths: &'static [&'static str],
    evidence_classes: &'static [EvidenceClass],
}

impl AllocatorBoundary {
    /// Creates a static-only allocator contract without adding allocation behavior.
    pub fn static_only() -> Self {
        Self {
            assumption: AllocatorAssumption::StaticOnly,
            maybe_heap_size_bytes: None,
            audit_surface_id: "allocator-heap-contracts",
            linker_section_name: "._user_heap_stack",
            evidence_paths: STATIC_ONLY_EVIDENCE_PATHS,
            evidence_classes: STATIC_ONLY_EVIDENCE_CLASSES,
        }
    }

    /// Creates a heap-backed allocator contract only when the retained heap is non-zero.
    pub fn heap_backed(heap_size_bytes: usize) -> Result<Self, AllocatorBoundaryError> {
        if heap_size_bytes == 0 {
            return Err(AllocatorBoundaryError::ZeroHeapSize);
        }

        Ok(Self {
            assumption: AllocatorAssumption::HeapBacked,
            maybe_heap_size_bytes: Some(heap_size_bytes),
            audit_surface_id: "allocator-heap-contracts",
            linker_section_name: "._user_heap_stack",
            evidence_paths: HEAP_BACKED_EVIDENCE_PATHS,
            evidence_classes: HEAP_BACKED_EVIDENCE_CLASSES,
        })
    }

    /// Returns whether the runtime is static-only or heap-backed.
    pub fn assumption(&self) -> AllocatorAssumption {
        self.assumption
    }

    /// Returns heap size evidence for heap-backed contracts.
    pub fn maybe_heap_size_bytes(&self) -> Option<usize> {
        self.maybe_heap_size_bytes
    }

    /// Returns the unsafe-boundary audit row for allocator and heap assumptions.
    pub fn audit_surface_id(&self) -> &'static str {
        self.audit_surface_id
    }

    /// Returns the retained linker section that bounds heap/stack assumptions.
    pub fn linker_section_name(&self) -> &'static str {
        self.linker_section_name
    }

    /// Returns retained config/linker evidence paths or symbols.
    pub fn evidence_paths(&self) -> &'static [&'static str] {
        self.evidence_paths
    }

    /// Returns local and non-local evidence classes for this allocator contract.
    pub fn evidence_classes(&self) -> &'static [EvidenceClass] {
        self.evidence_classes
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn allocator_boundary_rejects_zero_heap_size() {
        // Arrange
        let heap_size_bytes = 0;

        // Act
        let result = AllocatorBoundary::heap_backed(heap_size_bytes);

        // Assert
        assert!(matches!(result, Err(AllocatorBoundaryError::ZeroHeapSize)));
    }

    #[test]
    fn allocator_boundary_distinguishes_static_only_from_heap_backed() {
        // Arrange
        let static_only = AllocatorBoundary::static_only();
        let heap_backed = AllocatorBoundary::heap_backed(40960)
            .expect("non-zero heap size should create a heap-backed boundary");

        // Act
        let static_assumption = static_only.assumption();
        let heap_assumption = heap_backed.assumption();

        // Assert
        assert_ne!(static_assumption, heap_assumption);
        assert_eq!(static_only.maybe_heap_size_bytes(), None);
        assert_eq!(heap_backed.maybe_heap_size_bytes(), Some(40960));
        assert!(
            heap_backed
                .evidence_classes()
                .contains(&EvidenceClass::SimulatorFlow)
        );
    }
}
