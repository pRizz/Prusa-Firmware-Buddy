#![forbid(unsafe_code)]

//! Thin board adapter boundary for validated product profiles.
//!
//! Phase 5 owns actual HAL, MMIO, FFI, interrupt, and retained-code wiring.
//! This crate exists now so the architecture has an inspectable adapter layer
//! that cannot accept unchecked printer, board, or MCU primitives.

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
