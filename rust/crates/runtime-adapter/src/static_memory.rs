use crate::EvidenceClass;
use buddy_domain::{McuKind, ProductProfile};

const STATIC_TASK_MEMORY_SOURCES: &[&str] = &[
    "src/freertos/system_tasks.cpp",
    "src/buddy/main.cpp",
    "src/puppies/puppy_task.cpp",
    "src/puppy/dwarf/main.cpp",
    "src/puppy/modularbed/main.cpp",
    "src/puppy/xbuddy_extension/main.cpp",
];
const STATIC_TASK_MEMORY_EVIDENCE: &[EvidenceClass] = &[
    EvidenceClass::StaticSourceAudit,
    EvidenceClass::RustHostTest,
    EvidenceClass::SimulatorFlow,
    EvidenceClass::HardwareSmoke,
    EvidenceClass::ManualHardwareRequired,
];
const F4_G0_CONFIG_MINIMAL_STACK_WORDS: usize = 128;
const H503_CONFIG_MINIMAL_STACK_WORDS: usize = 32;

/// Error returned when static FreeRTOS task memory cannot represent a valid contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StaticTaskMemoryError {
    /// FreeRTOS stack depth is represented in `StackType_t` words and must not be zero.
    ZeroStackWords,
}

/// Static FreeRTOS task storage contract.
///
/// This type models retained static storage such as `StaticTask_t` and
/// `StackType_t[]` buffers. `stack_words` deliberately stores the FreeRTOS
/// stack depth in words, not bytes, matching `osThread*Def` and
/// `xTaskCreateStatic` call sites.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct StaticTaskMemory {
    task_name: &'static str,
    stack_words: usize,
    control_block_section: &'static str,
    stack_section: &'static str,
    storage_owner: &'static str,
    source_evidence_paths: &'static [&'static str],
    audit_surface_id: &'static str,
    evidence_classes: &'static [EvidenceClass],
}

impl StaticTaskMemory {
    /// Creates a static task memory contract using stack depth in FreeRTOS words.
    pub fn new(
        task_name: &'static str,
        stack_words: usize,
        control_block_section: &'static str,
        stack_section: &'static str,
        storage_owner: &'static str,
    ) -> Result<Self, StaticTaskMemoryError> {
        if stack_words == 0 {
            return Err(StaticTaskMemoryError::ZeroStackWords);
        }

        Ok(Self {
            task_name,
            stack_words,
            control_block_section,
            stack_section,
            storage_owner,
            source_evidence_paths: STATIC_TASK_MEMORY_SOURCES,
            audit_surface_id: "static-task-memory-contracts",
            evidence_classes: STATIC_TASK_MEMORY_EVIDENCE,
        })
    }

    /// Returns the retained FreeRTOS task name or callback owner.
    pub fn task_name(&self) -> &'static str {
        self.task_name
    }

    /// Returns stack depth in `StackType_t` words, not bytes.
    pub fn stack_words(&self) -> usize {
        self.stack_words
    }

    /// Returns the unit used by `stack_words`.
    pub fn stack_unit(&self) -> &'static str {
        "StackType_t words"
    }

    /// Returns the retained section used for the task control block.
    pub fn control_block_section(&self) -> &'static str {
        self.control_block_section
    }

    /// Returns the retained section used for the task stack.
    pub fn stack_section(&self) -> &'static str {
        self.stack_section
    }

    /// Returns the owner responsible for keeping this static storage alive.
    pub fn storage_owner(&self) -> &'static str {
        self.storage_owner
    }

    /// Returns source paths that prove the retained memory owner.
    pub fn source_evidence_paths(&self) -> &'static [&'static str] {
        self.source_evidence_paths
    }

    /// Returns the Phase 5 unsafe-audit surface ID for this contract.
    pub fn audit_surface_id(&self) -> &'static str {
        self.audit_surface_id
    }

    /// Returns evidence classes for static-memory and scheduler behavior.
    pub fn evidence_classes(&self) -> &'static [EvidenceClass] {
        self.evidence_classes
    }

    /// Contract for retained idle task callback storage in `configMINIMAL_STACK_SIZE` words.
    pub fn idle_task_callback(profile: &ProductProfile) -> Self {
        Self::new(
            "idle_task",
            config_minimal_stack_words(profile),
            ".ccmram",
            "default RAM",
            "src/freertos/system_tasks.cpp owns persistent idle task storage for the scheduler lifetime",
        )
        .expect("retained configMINIMAL_STACK_SIZE constants are nonzero")
    }

    /// Returns representative retained static task-memory contracts.
    pub fn known_contracts() -> &'static [Self] {
        KNOWN_STATIC_TASK_MEMORY
    }
}

const KNOWN_STATIC_TASK_MEMORY: &[StaticTaskMemory] = &[
    StaticTaskMemory {
        task_name: "displayTask",
        stack_words: 1_536,
        control_block_section: ".ccmram",
        stack_section: ".ccmram",
        storage_owner: "src/buddy/main.cpp owns displayTask_buffer and displayTask_control for the scheduler lifetime",
        source_evidence_paths: STATIC_TASK_MEMORY_SOURCES,
        audit_surface_id: "static-task-memory-contracts",
        evidence_classes: STATIC_TASK_MEMORY_EVIDENCE,
    },
    StaticTaskMemory {
        task_name: "defaultTask",
        stack_words: 1_200,
        control_block_section: ".ccmram",
        stack_section: ".ccmram",
        storage_owner: "src/buddy/main.cpp owns the default task CCM thread definition until scheduler teardown",
        source_evidence_paths: STATIC_TASK_MEMORY_SOURCES,
        audit_surface_id: "static-task-memory-contracts",
        evidence_classes: STATIC_TASK_MEMORY_EVIDENCE,
    },
    StaticTaskMemory {
        task_name: "puppies",
        stack_words: 896,
        control_block_section: ".ccmram",
        stack_section: ".ccmram",
        storage_owner: "src/puppies/puppy_task.cpp owns puppy task CCM storage for the scheduler lifetime",
        source_evidence_paths: STATIC_TASK_MEMORY_SOURCES,
        audit_surface_id: "static-task-memory-contracts",
        evidence_classes: STATIC_TASK_MEMORY_EVIDENCE,
    },
    StaticTaskMemory {
        task_name: "xbuddy_extension_main_task",
        stack_words: 200,
        control_block_section: "non_shared_data",
        stack_section: "non_shared_data",
        storage_owner: "src/puppy/xbuddy_extension/main.cpp owns MPU-visible main task storage before scheduler start",
        source_evidence_paths: STATIC_TASK_MEMORY_SOURCES,
        audit_surface_id: "static-task-memory-contracts",
        evidence_classes: STATIC_TASK_MEMORY_EVIDENCE,
    },
    StaticTaskMemory {
        task_name: "xbuddy_extension_hal_task",
        stack_words: 100,
        control_block_section: "non_shared_data",
        stack_section: "non_shared_data",
        storage_owner: "src/puppy/xbuddy_extension/main.cpp owns MPU-visible HAL task storage before scheduler start",
        source_evidence_paths: STATIC_TASK_MEMORY_SOURCES,
        audit_surface_id: "static-task-memory-contracts",
        evidence_classes: STATIC_TASK_MEMORY_EVIDENCE,
    },
];

fn config_minimal_stack_words(profile: &ProductProfile) -> usize {
    match profile.mcu() {
        McuKind::Stm32H503CbU7 => H503_CONFIG_MINIMAL_STACK_WORDS,
        McuKind::Stm32F407Vg
        | McuKind::Stm32F427Zi
        | McuKind::Stm32F429Vi
        | McuKind::Stm32G070RbT6 => F4_G0_CONFIG_MINIMAL_STACK_WORDS,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use buddy_domain::{
        BoardKind, BootloaderMode, Feature, FeatureSet, McuKind, PrinterKind, ProductProfile,
    };

    fn profile(
        printer: PrinterKind,
        board: BoardKind,
        mcu: McuKind,
        bootloader_mode: BootloaderMode,
        features: FeatureSet,
    ) -> ProductProfile {
        ProductProfile::new(printer, board, mcu, bootloader_mode, features)
            .expect("test profile must match the supported product matrix")
    }

    #[test]
    fn static_task_memory_rejects_zero_stack_words() {
        // Arrange, Act
        let result = StaticTaskMemory::new(
            "default_task",
            0,
            ".ccmram",
            ".ccmram",
            "retained FreeRTOS task storage",
        );

        // Assert
        assert_eq!(result, Err(StaticTaskMemoryError::ZeroStackWords));
    }

    #[test]
    fn static_task_memory_keeps_stack_depth_in_words() {
        // Arrange
        let memory = StaticTaskMemory::new(
            "default_task",
            1_200,
            ".ccmram",
            ".ccmram",
            "retained FreeRTOS task storage",
        )
        .expect("nonzero stack words should create a contract");

        // Act
        let stack_words = memory.stack_words();

        // Assert
        assert_eq!(stack_words, 1_200);
        assert_eq!(memory.stack_unit(), "StackType_t words");
        assert!(memory.storage_owner().contains("retained FreeRTOS task"));
    }

    #[test]
    fn idle_task_callback_uses_f4_and_g0_minimal_stack_size() {
        // Arrange
        let f4_profile = profile(
            PrinterKind::Mini,
            BoardKind::Buddy,
            McuKind::Stm32F407Vg,
            BootloaderMode::Boot,
            FeatureSet::empty(),
        );
        let g0_profile = profile(
            PrinterKind::Xl,
            BoardKind::Dwarf,
            McuKind::Stm32G070RbT6,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::Dwarf]),
        );

        // Act
        let f4_memory = StaticTaskMemory::idle_task_callback(&f4_profile);
        let g0_memory = StaticTaskMemory::idle_task_callback(&g0_profile);

        // Assert
        assert_eq!(f4_memory.stack_words(), F4_G0_CONFIG_MINIMAL_STACK_WORDS);
        assert_eq!(g0_memory.stack_words(), F4_G0_CONFIG_MINIMAL_STACK_WORDS);
    }

    #[test]
    fn idle_task_callback_uses_h503_minimal_stack_size() {
        // Arrange
        let profile = profile(
            PrinterKind::CoreOne,
            BoardKind::XBuddyExtension,
            McuKind::Stm32H503CbU7,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::XBuddyExtension]),
        );

        // Act
        let memory = StaticTaskMemory::idle_task_callback(&profile);

        // Assert
        assert_eq!(memory.stack_words(), H503_CONFIG_MINIMAL_STACK_WORDS);
    }
}
