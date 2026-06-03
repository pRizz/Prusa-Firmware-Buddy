/// Memory range category used by board-side unsafe boundary contracts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum MemoryRegionKind {
    /// STM32F4 CCMRAM, which retained code documents as inaccessible to DMA.
    CoreCoupledRam,
    /// SRAM or retained buffers visible to DMA-capable peripherals.
    DmaAccessibleRam,
    /// Peripheral register address range.
    MemoryMappedRegister,
    /// Linker-controlled firmware section.
    LinkerSection,
}

/// Error returned when a raw memory range cannot become a typed region.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MemoryRegionError {
    /// The region length was zero.
    ZeroLength,
    /// `start + length` overflowed the address space.
    AddressOverflow,
}

/// Checked memory range contract for linker, MMIO, and DMA facades.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MemoryRegion {
    kind: MemoryRegionKind,
    start: usize,
    length: usize,
    end_exclusive: usize,
}

impl MemoryRegion {
    /// Creates a typed memory region after range validation.
    pub fn new(
        kind: MemoryRegionKind,
        start: usize,
        length: usize,
    ) -> Result<Self, MemoryRegionError> {
        if length == 0 {
            return Err(MemoryRegionError::ZeroLength);
        }

        let Some(end_exclusive) = start.checked_add(length) else {
            return Err(MemoryRegionError::AddressOverflow);
        };

        Ok(Self {
            kind,
            start,
            length,
            end_exclusive,
        })
    }

    /// Returns the memory-region kind.
    pub fn kind(&self) -> MemoryRegionKind {
        self.kind
    }

    /// Returns the first address in the region.
    pub fn start(&self) -> usize {
        self.start
    }

    /// Returns the region length in bytes.
    pub fn length(&self) -> usize {
        self.length
    }

    /// Returns the exclusive end address.
    pub fn end_exclusive(&self) -> usize {
        self.end_exclusive
    }

    /// Returns true when `address` is inside this checked range.
    pub fn contains_address(&self, address: usize) -> bool {
        address >= self.start && address < self.end_exclusive
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn memory_region_rejects_zero_length() {
        // Arrange
        let start = 0x2000_0000;

        // Act
        let result = MemoryRegion::new(MemoryRegionKind::DmaAccessibleRam, start, 0);

        // Assert
        assert!(matches!(result, Err(MemoryRegionError::ZeroLength)));
    }

    #[test]
    fn memory_region_rejects_checked_add_overflow() {
        // Arrange
        let start = usize::MAX;
        let length = 2;

        // Act
        let result = MemoryRegion::new(MemoryRegionKind::DmaAccessibleRam, start, length);

        // Assert
        assert!(matches!(result, Err(MemoryRegionError::AddressOverflow)));
    }
}
