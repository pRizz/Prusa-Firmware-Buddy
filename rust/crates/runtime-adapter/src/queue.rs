use crate::EvidenceClass;

const QUEUE_SOURCE_EVIDENCE: &[&str] = &[
    "src/freertos/queue.cpp",
    "src/freertos/include/freertos/queue.hpp",
];
const QUEUE_EVIDENCE: &[EvidenceClass] = &[
    EvidenceClass::StaticSourceAudit,
    EvidenceClass::RustHostTest,
    EvidenceClass::SimulatorFlow,
    EvidenceClass::HardwareSmoke,
];

/// Error returned when static FreeRTOS queue storage cannot be represented safely.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StaticQueueStorageError {
    /// FreeRTOS queues copy fixed-size items; the copied item size cannot be zero.
    ZeroItemSize,
    /// The queue must hold at least one item.
    ZeroItemCapacity,
    /// Item size multiplied by capacity overflowed.
    StorageSizeOverflow,
}

/// Static FreeRTOS queue storage contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct StaticQueueStorage {
    item_size_bytes: usize,
    item_capacity: usize,
    item_storage_bytes: usize,
    audit_surface_id: &'static str,
    source_evidence_paths: &'static [&'static str],
    evidence_classes: &'static [EvidenceClass],
}

impl StaticQueueStorage {
    /// Creates a fixed-size item-copying queue storage contract.
    pub fn new(
        item_size_bytes: usize,
        item_capacity: usize,
    ) -> Result<Self, StaticQueueStorageError> {
        if item_size_bytes == 0 {
            return Err(StaticQueueStorageError::ZeroItemSize);
        }
        if item_capacity == 0 {
            return Err(StaticQueueStorageError::ZeroItemCapacity);
        }

        let Some(item_storage_bytes) = item_size_bytes.checked_mul(item_capacity) else {
            return Err(StaticQueueStorageError::StorageSizeOverflow);
        };

        Ok(Self {
            item_size_bytes,
            item_capacity,
            item_storage_bytes,
            audit_surface_id: "freertos-queue-contracts",
            source_evidence_paths: QUEUE_SOURCE_EVIDENCE,
            evidence_classes: QUEUE_EVIDENCE,
        })
    }

    /// Returns the size in bytes FreeRTOS copies per queue item.
    pub fn item_size_bytes(&self) -> usize {
        self.item_size_bytes
    }

    /// Returns the fixed queue capacity.
    pub fn item_capacity(&self) -> usize {
        self.item_capacity
    }

    /// Returns the total byte storage required for item copies.
    pub fn item_storage_bytes(&self) -> usize {
        self.item_storage_bytes
    }

    /// Returns true because retained FreeRTOS queues byte-copy fixed-size items.
    pub fn copies_fixed_size_items(&self) -> bool {
        true
    }

    /// Returns the Phase 5 unsafe-audit surface ID for this contract.
    pub fn audit_surface_id(&self) -> &'static str {
        self.audit_surface_id
    }

    /// Returns source paths proving retained queue wrapper behavior.
    pub fn source_evidence_paths(&self) -> &'static [&'static str] {
        self.source_evidence_paths
    }

    /// Returns evidence classes for queue storage and scheduler wakeups.
    pub fn evidence_classes(&self) -> &'static [EvidenceClass] {
        self.evidence_classes
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn static_queue_storage_rejects_zero_item_size() {
        // Arrange, Act
        let result = StaticQueueStorage::new(0, 4);

        // Assert
        assert_eq!(result, Err(StaticQueueStorageError::ZeroItemSize));
    }

    #[test]
    fn static_queue_storage_rejects_zero_capacity() {
        // Arrange, Act
        let result = StaticQueueStorage::new(8, 0);

        // Assert
        assert_eq!(result, Err(StaticQueueStorageError::ZeroItemCapacity));
    }
}
