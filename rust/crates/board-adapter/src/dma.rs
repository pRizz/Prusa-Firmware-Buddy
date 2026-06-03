use crate::{MemoryRegion, MemoryRegionKind};

/// Error returned when a memory region cannot be shared with DMA.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DmaBufferError {
    /// The region is not explicitly classified as DMA-accessible RAM.
    NotDmaAccessible,
}

/// DMA-visible memory range contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct DmaBufferRegion {
    region: MemoryRegion,
}

impl DmaBufferRegion {
    /// Creates a DMA buffer region only from memory classified as DMA-accessible.
    pub fn new(region: MemoryRegion) -> Result<Self, DmaBufferError> {
        if region.kind() != MemoryRegionKind::DmaAccessibleRam {
            return Err(DmaBufferError::NotDmaAccessible);
        }

        Ok(Self { region })
    }

    /// Returns the checked memory region behind this DMA contract.
    pub fn region(&self) -> MemoryRegion {
        self.region
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dma_buffer_rejects_core_coupled_ram() {
        // Arrange
        let region = MemoryRegion::new(MemoryRegionKind::CoreCoupledRam, 0x1000_0000, 1024)
            .expect("nonzero memory region should be valid");

        // Act
        let result = DmaBufferRegion::new(region);

        // Assert
        assert!(matches!(result, Err(DmaBufferError::NotDmaAccessible)));
    }

    #[test]
    fn dma_buffer_accepts_dma_accessible_ram() {
        // Arrange
        let region = MemoryRegion::new(MemoryRegionKind::DmaAccessibleRam, 0x2000_0000, 1024)
            .expect("nonzero memory region should be valid");

        // Act
        let result = DmaBufferRegion::new(region);

        // Assert
        assert!(
            matches!(result, Ok(buffer) if buffer.region().kind() == MemoryRegionKind::DmaAccessibleRam)
        );
    }
}
