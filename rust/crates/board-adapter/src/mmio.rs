use crate::{MemoryRegion, MemoryRegionError, MemoryRegionKind};

/// Register width used to validate MMIO address alignment.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum RegisterWidth {
    /// 8-bit register access.
    U8,
    /// 16-bit register access.
    U16,
    /// 32-bit register access.
    U32,
}

impl RegisterWidth {
    fn bytes(self) -> usize {
        match self {
            Self::U8 => 1,
            Self::U16 => 2,
            Self::U32 => 4,
        }
    }
}

/// Error returned when a raw address cannot become a register contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RegisterAddressError {
    /// Zero is not a valid peripheral register address.
    ZeroAddress,
    /// The address is not aligned for the requested register width.
    UnalignedAddress,
    /// The backing memory range failed validation.
    InvalidRegion(MemoryRegionError),
    /// The address width is not valid for a 32-bit register facade.
    NotU32,
}

/// Typed peripheral register address tied to a memory-mapped-register region.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RegisterAddress {
    region: MemoryRegion,
    width: RegisterWidth,
}

impl RegisterAddress {
    /// Creates a typed register address after nonzero and alignment checks.
    pub fn new(address: usize, width: RegisterWidth) -> Result<Self, RegisterAddressError> {
        if address == 0 {
            return Err(RegisterAddressError::ZeroAddress);
        }

        let width_bytes = width.bytes();
        if address % width_bytes != 0 {
            return Err(RegisterAddressError::UnalignedAddress);
        }

        let region =
            MemoryRegion::new(MemoryRegionKind::MemoryMappedRegister, address, width_bytes)
                .map_err(RegisterAddressError::InvalidRegion)?;

        Ok(Self { region, width })
    }

    /// Returns the raw address value.
    pub fn address(&self) -> usize {
        self.region.start()
    }

    /// Returns the requested access width.
    pub fn width(&self) -> RegisterWidth {
        self.width
    }

    fn as_const_ptr<T>(&self) -> *const T {
        self.address() as *const T
    }

    fn as_mut_ptr<T>(&self) -> *mut T {
        self.address() as *mut T
    }
}

/// Narrow 32-bit MMIO register facade.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Register32 {
    address: RegisterAddress,
}

impl Register32 {
    /// Creates a 32-bit register facade from a typed register address.
    pub fn new(address: RegisterAddress) -> Result<Self, RegisterAddressError> {
        if address.width() != RegisterWidth::U32 {
            return Err(RegisterAddressError::NotU32);
        }

        Ok(Self { address })
    }

    /// Returns the typed register address.
    pub fn address(&self) -> RegisterAddress {
        self.address
    }

    /// Reads the register through a volatile MMIO load.
    ///
    /// Volatile access is not synchronization; callers must still preserve the
    /// retained HAL sequencing contract for the selected board.
    pub fn read(&self) -> u32 {
        let pointer = self.address.as_const_ptr::<u32>();

        // SAFETY: mmio-register-contracts - RegisterAddress::new rejects zero
        // and unaligned addresses, and this facade centralizes volatile MMIO
        // access for retained HAL/CMSIS-owned peripheral registers.
        unsafe { core::ptr::read_volatile(pointer) }
    }

    /// Writes the register through a volatile MMIO store.
    ///
    /// Volatile access is not synchronization; callers must still preserve the
    /// retained HAL sequencing contract for the selected board.
    pub fn write(&self, value: u32) {
        let pointer = self.address.as_mut_ptr::<u32>();

        // SAFETY: mmio-register-contracts - RegisterAddress::new rejects zero
        // and unaligned addresses, and this facade centralizes volatile MMIO
        // access for retained HAL/CMSIS-owned peripheral registers.
        unsafe { core::ptr::write_volatile(pointer, value) };
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn register_address_rejects_zero_address() {
        // Arrange
        let address = 0;

        // Act
        let result = RegisterAddress::new(address, RegisterWidth::U32);

        // Assert
        assert!(matches!(result, Err(RegisterAddressError::ZeroAddress)));
    }

    #[test]
    fn register_address_rejects_unaligned_width() {
        // Arrange
        let address = 0x4000_0001;

        // Act
        let result = RegisterAddress::new(address, RegisterWidth::U32);

        // Assert
        assert!(matches!(
            result,
            Err(RegisterAddressError::UnalignedAddress)
        ));
    }
}
