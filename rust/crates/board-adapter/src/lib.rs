#![deny(unsafe_op_in_unsafe_fn)]

//! Thin board adapter boundary for validated product profiles.
//!
//! Phase 5 owns actual HAL, MMIO, FFI, interrupt, and retained-code wiring.
//! This crate exists now so the architecture has an inspectable adapter layer
//! that cannot accept unchecked printer, board, or MCU primitives.

pub mod clock;
pub mod dma;
pub mod ffi;
pub mod interrupt;
pub mod mcu;
pub mod memory_region;
pub mod mmio;

pub use clock::{BoardClockTree, ClockSource, CoreClockHz};
pub use dma::DmaBufferRegion;
pub use ffi::{ForeignComponentId, ForeignSymbol};
pub use interrupt::{InterruptLine, InterruptPriority};
pub use mcu::{BoardRuntimeSurface, McuFamily};
pub use memory_region::{MemoryRegion, MemoryRegionError, MemoryRegionKind};
pub use mmio::{Register32, RegisterAddress};

use buddy_domain::{BoardKind, McuKind, ProductProfile};

/// Board adapter boundary derived from a validated product profile.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BoardAdapterBoundary {
    profile: ProductProfile,
}

impl BoardAdapterBoundary {
    /// Creates a board adapter boundary from a validated profile.
    pub fn new(profile: ProductProfile) -> Self {
        Self { profile }
    }

    /// Returns the selected board.
    pub fn board(&self) -> BoardKind {
        self.profile.board()
    }

    /// Returns the selected MCU.
    pub fn mcu(&self) -> McuKind {
        self.profile.mcu()
    }

    /// Returns true because board code remains a retained-code/unsafe boundary
    /// until Phase 5 narrows it with explicit facade contracts.
    pub fn requires_foreign_runtime(&self) -> bool {
        true
    }
}
