const SYNCHRONIZATION_SOURCE_EVIDENCE: &[&str] = &[
    "include/tasks.hpp",
    "src/common/tasks.cpp",
    "src/freertos/mutex.cpp",
    "src/freertos/include/freertos/mutex.hpp",
    "src/freertos/binary_semaphore.cpp",
    "src/freertos/include/freertos/binary_semaphore.hpp",
    "src/freertos/counting_semaphore.cpp",
    "src/freertos/include/freertos/counting_semaphore.hpp",
    "src/freertos/wait_condition.cpp",
    "src/freertos/include/freertos/wait_condition.hpp",
    "include/common/freertos_shared_mutex.hpp",
    "src/common/rw_mutex.cpp",
];
const TASK_DEPS_EVENT_GROUP_API_EVIDENCE: &[&str] = &[
    "components_ready",
    "xEventGroupWaitBits",
    "xEventGroupSetBits",
];
const NON_LOCAL_SCHEDULER_EVIDENCE: &[SynchronizationEvidence] = &[
    SynchronizationEvidence::ManualHardwareRequired,
    SynchronizationEvidence::SimulatorFlow,
    SynchronizationEvidence::HardwareSmoke,
];
const SYNCHRONIZATION_EVIDENCE: &[SynchronizationEvidence] = &[
    SynchronizationEvidence::RustHostTest,
    SynchronizationEvidence::SimulatorFlow,
    SynchronizationEvidence::HardwareSmoke,
    SynchronizationEvidence::ManualHardwareRequired,
];

/// Evidence classes specific to FreeRTOS synchronization timing and wakeups.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum SynchronizationEvidence {
    /// Host tests can validate contract construction and invariant names.
    RustHostTest,
    /// Simulator flow evidence is needed for scheduler ordering.
    SimulatorFlow,
    /// Hardware smoke evidence is needed for interrupt and wakeup behavior.
    HardwareSmoke,
    /// Manual hardware validation is still required before parity claims.
    ManualHardwareRequired,
}

impl SynchronizationEvidence {
    /// Returns the Phase 5 audit spelling for this evidence class.
    pub fn audit_value(self) -> &'static str {
        match self {
            Self::RustHostTest => "rust-host-test",
            Self::SimulatorFlow => "simulator-flow",
            Self::HardwareSmoke => "hardware-smoke",
            Self::ManualHardwareRequired => "manual-hardware-required",
        }
    }

    /// Returns non-local evidence required for scheduler timing and wakeup ordering.
    pub fn non_local_scheduler_evidence() -> &'static [Self] {
        NON_LOCAL_SCHEDULER_EVIDENCE
    }

    /// Returns true when host tests cannot prove the behavior represented by this evidence.
    pub fn requires_non_local_scheduler_evidence(self) -> bool {
        matches!(
            self,
            Self::SimulatorFlow | Self::HardwareSmoke | Self::ManualHardwareRequired
        )
    }
}

/// Error returned when a synchronization contract cannot represent retained storage safely.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SynchronizationContractError {
    /// The erased FreeRTOS wrapper storage cannot be zero bytes.
    ZeroStorageSize,
    /// The wrapper storage alignment cannot be zero.
    ZeroAlignment,
    /// Counting semaphores need a nonzero maximum token count.
    ZeroMaxCount,
    /// Initial tokens cannot exceed the maximum token count.
    InitialCountExceedsMax,
}

/// Mutex storage and ownership contract for `freertos::Mutex`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MutexContract {
    storage_size_bytes: usize,
    storage_alignment: usize,
    audit_surface_id: &'static str,
    locking_invariant: &'static str,
    isr_boundary: &'static str,
    source_evidence_paths: &'static [&'static str],
    evidence_classes: &'static [SynchronizationEvidence],
}

impl MutexContract {
    fn new(
        storage_size_bytes: usize,
        storage_alignment: usize,
    ) -> Result<Self, SynchronizationContractError> {
        validate_storage(storage_size_bytes, storage_alignment)?;

        Ok(Self {
            storage_size_bytes,
            storage_alignment,
            audit_surface_id: "freertos-mutex-contracts",
            locking_invariant: "exclusive non-recursive ownership; lock and unlock must be paired by the owning task",
            isr_boundary: "mutex lock/unlock is task-context only; ISR-safe release is modeled by semaphore contracts",
            source_evidence_paths: SYNCHRONIZATION_SOURCE_EVIDENCE,
            evidence_classes: SYNCHRONIZATION_EVIDENCE,
        })
    }

    /// Returns erased FreeRTOS static semaphore storage size in bytes.
    pub fn storage_size_bytes(&self) -> usize {
        self.storage_size_bytes
    }

    /// Returns erased FreeRTOS static semaphore storage alignment.
    pub fn storage_alignment(&self) -> usize {
        self.storage_alignment
    }

    /// Returns the Phase 5 unsafe-audit surface ID for this mutex contract.
    pub fn audit_surface_id(&self) -> &'static str {
        self.audit_surface_id
    }

    /// Returns the retained mutex ownership invariant.
    pub fn locking_invariant(&self) -> &'static str {
        self.locking_invariant
    }

    /// Returns the ISR boundary for this retained wrapper.
    pub fn isr_boundary(&self) -> &'static str {
        self.isr_boundary
    }

    /// Returns source paths proving retained mutex behavior.
    pub fn source_evidence_paths(&self) -> &'static [&'static str] {
        self.source_evidence_paths
    }

    /// Returns local and non-local evidence classes for this contract.
    pub fn evidence_classes(&self) -> &'static [SynchronizationEvidence] {
        self.evidence_classes
    }
}

/// Retained semaphore storage kind.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SemaphoreKind {
    Binary,
    Counting,
}

/// Binary or counting semaphore contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct SemaphoreContract {
    kind: SemaphoreKind,
    storage_size_bytes: usize,
    storage_alignment: usize,
    max_count: usize,
    initial_count: usize,
    audit_surface_id: &'static str,
    ownership_invariant: &'static str,
    isr_boundary: &'static str,
    source_evidence_paths: &'static [&'static str],
    evidence_classes: &'static [SynchronizationEvidence],
}

impl SemaphoreContract {
    fn binary(
        storage_size_bytes: usize,
        storage_alignment: usize,
    ) -> Result<Self, SynchronizationContractError> {
        validate_storage(storage_size_bytes, storage_alignment)?;

        Ok(Self {
            kind: SemaphoreKind::Binary,
            storage_size_bytes,
            storage_alignment,
            max_count: 1,
            initial_count: 0,
            audit_surface_id: "freertos-binary-semaphore-contracts",
            ownership_invariant: "binary semaphore stores at most one token; release_from_isr is the ISR-safe release boundary",
            isr_boundary: "release_from_isr may yield from ISR through portYIELD_FROM_ISR; acquire remains task-context",
            source_evidence_paths: SYNCHRONIZATION_SOURCE_EVIDENCE,
            evidence_classes: SYNCHRONIZATION_EVIDENCE,
        })
    }

    fn counting(
        storage_size_bytes: usize,
        storage_alignment: usize,
        max_count: usize,
        initial_count: usize,
    ) -> Result<Self, SynchronizationContractError> {
        validate_storage(storage_size_bytes, storage_alignment)?;
        if max_count == 0 {
            return Err(SynchronizationContractError::ZeroMaxCount);
        }
        if initial_count > max_count {
            return Err(SynchronizationContractError::InitialCountExceedsMax);
        }

        Ok(Self {
            kind: SemaphoreKind::Counting,
            storage_size_bytes,
            storage_alignment,
            max_count,
            initial_count,
            audit_surface_id: "freertos-counting-semaphore-contracts",
            ownership_invariant: "counting semaphore capacity cannot overflow and timeout behavior follows retained xSemaphoreTake",
            isr_boundary: "retained counting wrapper exposes task-context release/acquire only in Phase 5 contracts",
            source_evidence_paths: SYNCHRONIZATION_SOURCE_EVIDENCE,
            evidence_classes: SYNCHRONIZATION_EVIDENCE,
        })
    }

    /// Returns whether this is a binary or counting semaphore contract.
    pub fn kind(&self) -> SemaphoreKind {
        self.kind
    }

    /// Returns erased FreeRTOS static semaphore storage size in bytes.
    pub fn storage_size_bytes(&self) -> usize {
        self.storage_size_bytes
    }

    /// Returns erased FreeRTOS static semaphore storage alignment.
    pub fn storage_alignment(&self) -> usize {
        self.storage_alignment
    }

    /// Returns maximum token count.
    pub fn max_count(&self) -> usize {
        self.max_count
    }

    /// Returns initial token count.
    pub fn initial_count(&self) -> usize {
        self.initial_count
    }

    /// Returns the Phase 5 unsafe-audit surface ID for this semaphore.
    pub fn audit_surface_id(&self) -> &'static str {
        self.audit_surface_id
    }

    /// Returns the retained semaphore ownership invariant.
    pub fn ownership_invariant(&self) -> &'static str {
        self.ownership_invariant
    }

    /// Returns ISR-safety boundary evidence for this semaphore.
    pub fn isr_boundary(&self) -> &'static str {
        self.isr_boundary
    }

    /// Returns source paths proving retained semaphore behavior.
    pub fn source_evidence_paths(&self) -> &'static [&'static str] {
        self.source_evidence_paths
    }

    /// Returns local and non-local evidence classes for this contract.
    pub fn evidence_classes(&self) -> &'static [SynchronizationEvidence] {
        self.evidence_classes
    }
}

/// Event-group contract for TaskDeps readiness bits.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct EventGroupContract {
    event_group_symbol: &'static str,
    api_evidence: &'static [&'static str],
    readiness_semantics: &'static str,
    audit_surface_id: &'static str,
    source_evidence_paths: &'static [&'static str],
    evidence_classes: &'static [SynchronizationEvidence],
}

impl EventGroupContract {
    /// Returns the retained TaskDeps event-group contract.
    pub fn task_deps() -> Self {
        Self {
            event_group_symbol: "components_ready",
            api_evidence: TASK_DEPS_EVENT_GROUP_API_EVIDENCE,
            readiness_semantics: "TaskDeps::wait waits for all requested bits without clearing them; TaskDeps::provide publishes one readiness bit through xEventGroupSetBits",
            audit_surface_id: "freertos-event-group-contracts",
            source_evidence_paths: SYNCHRONIZATION_SOURCE_EVIDENCE,
            evidence_classes: SYNCHRONIZATION_EVIDENCE,
        }
    }

    /// Returns the retained event-group symbol.
    pub fn event_group_symbol(&self) -> &'static str {
        self.event_group_symbol
    }

    /// Returns retained FreeRTOS APIs that prove wait/set behavior.
    pub fn api_evidence(&self) -> &'static [&'static str] {
        self.api_evidence
    }

    /// Returns readiness semantics for event bits.
    pub fn readiness_semantics(&self) -> &'static str {
        self.readiness_semantics
    }

    /// Returns the Phase 5 unsafe-audit surface ID for this event group.
    pub fn audit_surface_id(&self) -> &'static str {
        self.audit_surface_id
    }

    /// Returns source paths proving retained event-group behavior.
    pub fn source_evidence_paths(&self) -> &'static [&'static str] {
        self.source_evidence_paths
    }

    /// Returns local and non-local evidence classes for this contract.
    pub fn evidence_classes(&self) -> &'static [SynchronizationEvidence] {
        self.evidence_classes
    }
}

/// Wait-condition contract for retained `freertos::WaitCondition`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct WaitConditionContract {
    audit_surface_id: &'static str,
    locking_invariant: &'static str,
    binary_semaphore_surface_id: &'static str,
    notification_invariant: &'static str,
    source_evidence_paths: &'static [&'static str],
    evidence_classes: &'static [SynchronizationEvidence],
}

impl WaitConditionContract {
    /// Returns the retained wait-condition wrapper contract.
    pub fn retained_wrapper() -> Self {
        Self {
            audit_surface_id: "freertos-wait-condition-contracts",
            locking_invariant: "caller must hold the mutex; wait must unlock before semaphore acquire and reacquire the mutex after notification",
            binary_semaphore_surface_id: "freertos-binary-semaphore-contracts",
            notification_invariant: "notify_one and notify_all account for waiter_count and release the binary semaphore without claiming host tests prove wakeup timing",
            source_evidence_paths: SYNCHRONIZATION_SOURCE_EVIDENCE,
            evidence_classes: SYNCHRONIZATION_EVIDENCE,
        }
    }

    /// Returns the Phase 5 unsafe-audit surface ID for this wait condition.
    pub fn audit_surface_id(&self) -> &'static str {
        self.audit_surface_id
    }

    /// Returns mutex release/reacquire invariant.
    pub fn locking_invariant(&self) -> &'static str {
        self.locking_invariant
    }

    /// Returns the binary semaphore dependency used for wakeups.
    pub fn binary_semaphore_surface_id(&self) -> &'static str {
        self.binary_semaphore_surface_id
    }

    /// Returns notification/waiter-count invariant.
    pub fn notification_invariant(&self) -> &'static str {
        self.notification_invariant
    }

    /// Returns source paths proving retained wait-condition behavior.
    pub fn source_evidence_paths(&self) -> &'static [&'static str] {
        self.source_evidence_paths
    }

    /// Returns local and non-local evidence classes for this contract.
    pub fn evidence_classes(&self) -> &'static [SynchronizationEvidence] {
        self.evidence_classes
    }
}

/// Top-level synchronization primitive contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SynchronizationPrimitive {
    Mutex(MutexContract),
    BinarySemaphore(SemaphoreContract),
    CountingSemaphore(SemaphoreContract),
    EventGroup(EventGroupContract),
    WaitCondition(WaitConditionContract),
}

impl SynchronizationPrimitive {
    /// Creates a retained mutex contract.
    pub fn mutex(
        storage_size_bytes: usize,
        storage_alignment: usize,
    ) -> Result<Self, SynchronizationContractError> {
        MutexContract::new(storage_size_bytes, storage_alignment).map(Self::Mutex)
    }

    /// Creates a retained binary semaphore contract.
    pub fn binary_semaphore(
        storage_size_bytes: usize,
        storage_alignment: usize,
    ) -> Result<Self, SynchronizationContractError> {
        SemaphoreContract::binary(storage_size_bytes, storage_alignment).map(Self::BinarySemaphore)
    }

    /// Creates a retained counting semaphore contract.
    pub fn counting_semaphore(
        storage_size_bytes: usize,
        storage_alignment: usize,
        max_count: usize,
        initial_count: usize,
    ) -> Result<Self, SynchronizationContractError> {
        SemaphoreContract::counting(
            storage_size_bytes,
            storage_alignment,
            max_count,
            initial_count,
        )
        .map(Self::CountingSemaphore)
    }

    /// Creates the retained TaskDeps event-group contract.
    pub fn task_deps_event_group() -> Self {
        Self::EventGroup(EventGroupContract::task_deps())
    }

    /// Creates the retained wait-condition contract.
    pub fn wait_condition() -> Self {
        Self::WaitCondition(WaitConditionContract::retained_wrapper())
    }

    /// Returns the Phase 5 unsafe-audit surface ID for this primitive.
    pub fn audit_surface_id(&self) -> &'static str {
        match self {
            Self::Mutex(contract) => contract.audit_surface_id(),
            Self::BinarySemaphore(contract) | Self::CountingSemaphore(contract) => {
                contract.audit_surface_id()
            }
            Self::EventGroup(contract) => contract.audit_surface_id(),
            Self::WaitCondition(contract) => contract.audit_surface_id(),
        }
    }

    /// Returns semaphore kind for semaphore primitives.
    pub fn semaphore_kind(&self) -> Option<SemaphoreKind> {
        match self {
            Self::BinarySemaphore(contract) | Self::CountingSemaphore(contract) => {
                Some(contract.kind())
            }
            Self::Mutex(_) | Self::EventGroup(_) | Self::WaitCondition(_) => None,
        }
    }

    /// Returns local and non-local evidence classes for this primitive.
    pub fn evidence_classes(&self) -> &'static [SynchronizationEvidence] {
        match self {
            Self::Mutex(contract) => contract.evidence_classes(),
            Self::BinarySemaphore(contract) | Self::CountingSemaphore(contract) => {
                contract.evidence_classes()
            }
            Self::EventGroup(contract) => contract.evidence_classes(),
            Self::WaitCondition(contract) => contract.evidence_classes(),
        }
    }
}

fn validate_storage(
    storage_size_bytes: usize,
    storage_alignment: usize,
) -> Result<(), SynchronizationContractError> {
    if storage_size_bytes == 0 {
        return Err(SynchronizationContractError::ZeroStorageSize);
    }
    if storage_alignment == 0 {
        return Err(SynchronizationContractError::ZeroAlignment);
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn mutex_rejects_zero_storage_or_alignment() {
        // Arrange, Act
        let zero_storage = SynchronizationPrimitive::mutex(0, 4);
        let zero_alignment = SynchronizationPrimitive::mutex(4, 0);
        let valid = SynchronizationPrimitive::mutex(4, 4)
            .expect("nonzero storage and alignment should create a mutex contract");

        // Assert
        assert_eq!(
            zero_storage,
            Err(SynchronizationContractError::ZeroStorageSize)
        );
        assert_eq!(
            zero_alignment,
            Err(SynchronizationContractError::ZeroAlignment)
        );
        assert_eq!(valid.audit_surface_id(), "freertos-mutex-contracts");
    }

    #[test]
    fn semaphore_contracts_distinguish_binary_and_counting_storage() {
        // Arrange
        let binary = SynchronizationPrimitive::binary_semaphore(4, 4)
            .expect("binary semaphore storage should be valid");
        let counting = SynchronizationPrimitive::counting_semaphore(4, 4, 8, 0)
            .expect("counting semaphore storage should be valid");

        // Act, Assert
        assert_eq!(
            binary.audit_surface_id(),
            "freertos-binary-semaphore-contracts"
        );
        assert_eq!(
            counting.audit_surface_id(),
            "freertos-counting-semaphore-contracts"
        );
        assert_ne!(binary.semaphore_kind(), counting.semaphore_kind());
    }

    #[test]
    fn task_deps_event_group_names_wait_and_set_evidence() {
        // Arrange, Act
        let contract = EventGroupContract::task_deps();

        // Assert
        assert_eq!(
            contract.audit_surface_id(),
            "freertos-event-group-contracts"
        );
        assert_eq!(contract.event_group_symbol(), "components_ready");
        assert!(contract.api_evidence().contains(&"xEventGroupWaitBits"));
        assert!(contract.api_evidence().contains(&"xEventGroupSetBits"));
    }

    #[test]
    fn wait_condition_names_unlock_relock_and_binary_semaphore_dependency() {
        // Arrange, Act
        let contract = WaitConditionContract::retained_wrapper();

        // Assert
        assert_eq!(
            contract.audit_surface_id(),
            "freertos-wait-condition-contracts"
        );
        assert!(
            contract
                .locking_invariant()
                .contains("unlock before semaphore acquire")
        );
        assert_eq!(
            contract.binary_semaphore_surface_id(),
            "freertos-binary-semaphore-contracts"
        );
    }

    #[test]
    fn synchronization_keeps_non_local_scheduler_evidence() {
        // Arrange, Act
        let evidence = SynchronizationEvidence::non_local_scheduler_evidence();

        // Assert
        assert!(evidence.contains(&SynchronizationEvidence::ManualHardwareRequired));
        assert!(evidence.contains(&SynchronizationEvidence::SimulatorFlow));
        assert!(evidence.contains(&SynchronizationEvidence::HardwareSmoke));
    }
}
