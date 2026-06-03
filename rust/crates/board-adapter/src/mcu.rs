use buddy_domain::{BoardKind, McuKind, ProductProfile};

/// MCU runtime family used by retained board startup, HAL, and linker surfaces.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum McuFamily {
    /// STM32F4 master-board family selected from `src/device/stm32f4`.
    Stm32F4,
    /// STM32G0 auxiliary-controller family selected from `src/device/stm32g0`.
    Stm32G0,
    /// STM32H503 xBuddy Extension surface selected from `src/puppy/xbuddy_extension`.
    Stm32H503XbuddyExtension,
}

/// Board and MCU contract derived from a validated domain product profile.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct BoardRuntimeSurface {
    board: BoardKind,
    mcu: McuKind,
    mcu_family: McuFamily,
    retained_component_id: &'static str,
}

impl BoardRuntimeSurface {
    /// Creates a board runtime surface from a validated product profile.
    pub fn from_profile(profile: &ProductProfile) -> Self {
        let board = profile.board();
        let mcu = profile.mcu();
        let (mcu_family, retained_component_id) = runtime_surface_for(board, mcu);

        Self {
            board,
            mcu,
            mcu_family,
            retained_component_id,
        }
    }

    /// Returns the selected board.
    pub fn board(&self) -> BoardKind {
        self.board
    }

    /// Returns the selected MCU.
    pub fn mcu(&self) -> McuKind {
        self.mcu
    }

    /// Returns the retained runtime MCU family.
    pub fn mcu_family(&self) -> McuFamily {
        self.mcu_family
    }

    /// Returns the retained foreign-code inventory row that owns this surface.
    pub fn retained_component_id(&self) -> &'static str {
        self.retained_component_id
    }
}

fn runtime_surface_for(board: BoardKind, mcu: McuKind) -> (McuFamily, &'static str) {
    match (board, mcu) {
        (
            BoardKind::Buddy | BoardKind::XBuddy | BoardKind::XlBuddy | BoardKind::XlDevKitXlBuddy,
            McuKind::Stm32F407Vg | McuKind::Stm32F427Zi | McuKind::Stm32F429Vi,
        ) => (McuFamily::Stm32F4, "stm32f4-startup-linker"),
        (BoardKind::Dwarf | BoardKind::ModularBed, McuKind::Stm32G070RbT6) => {
            (McuFamily::Stm32G0, "stm32g0-startup-linker")
        }
        (BoardKind::XBuddyExtension, McuKind::Stm32H503CbU7) => (
            McuFamily::Stm32H503XbuddyExtension,
            "stm32h503-xbuddy-extension-startup-linker",
        ),
        (_, McuKind::Stm32F407Vg | McuKind::Stm32F427Zi | McuKind::Stm32F429Vi) => {
            (McuFamily::Stm32F4, "stm32f4-startup-linker")
        }
        (_, McuKind::Stm32G070RbT6) => (McuFamily::Stm32G0, "stm32g0-startup-linker"),
        (_, McuKind::Stm32H503CbU7) => (
            McuFamily::Stm32H503XbuddyExtension,
            "stm32h503-xbuddy-extension-startup-linker",
        ),
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
    fn maps_f4_and_g0_profiles_to_distinct_mcu_families() {
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
        let f4_surface = BoardRuntimeSurface::from_profile(&f4_profile);
        let g0_surface = BoardRuntimeSurface::from_profile(&g0_profile);

        // Assert
        assert_eq!(f4_surface.mcu_family(), McuFamily::Stm32F4);
        assert_eq!(g0_surface.mcu_family(), McuFamily::Stm32G0);
    }

    #[test]
    fn maps_h503_xbuddy_extension_profile_to_specific_surface() {
        // Arrange
        let profile = profile(
            PrinterKind::CoreOne,
            BoardKind::XBuddyExtension,
            McuKind::Stm32H503CbU7,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::XBuddyExtension]),
        );

        // Act
        let surface = BoardRuntimeSurface::from_profile(&profile);

        // Assert
        assert_eq!(surface.board(), BoardKind::XBuddyExtension);
        assert_eq!(surface.mcu(), McuKind::Stm32H503CbU7);
        assert_eq!(surface.mcu_family(), McuFamily::Stm32H503XbuddyExtension);
    }
}
