use crate::{Feature, FeatureSet, InvariantError};

/// Supported reference printer selected by the current firmware matrix.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum PrinterKind {
    /// Original Prusa CORE One.
    CoreOne,
    /// Original Prusa MINI.
    Mini,
    /// Original Prusa MK4.
    Mk4,
    /// Original Prusa MK3.5.
    Mk35,
    /// Original Prusa XL.
    Xl,
    /// Original Prusa iX.
    Ix,
    /// Original Prusa XL development kit.
    XlDevKit,
}

/// Supported board or auxiliary-controller firmware personality.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum BoardKind {
    /// Buddy board.
    Buddy,
    /// xBuddy board.
    XBuddy,
    /// XL Buddy board.
    XlBuddy,
    /// Dwarf auxiliary controller.
    Dwarf,
    /// Modular Bed auxiliary controller.
    ModularBed,
    /// XL development-kit XL board.
    XlDevKitXlBuddy,
    /// xBuddy Extension auxiliary controller.
    XBuddyExtension,
}

/// Supported MCU selected by board configuration.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum McuKind {
    /// STM32F407VG MCU.
    Stm32F407Vg,
    /// STM32F427ZI MCU.
    Stm32F427Zi,
    /// STM32F429VI MCU.
    Stm32F429Vi,
    /// STM32G070RBT6 MCU.
    Stm32G070RbT6,
    /// STM32H503CBU7 MCU.
    Stm32H503CbU7,
}

/// Firmware bootloader packaging mode.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum BootloaderMode {
    /// Firmware package includes bootloader-managed update behavior.
    Boot,
    /// Firmware package omits bootloader output.
    NoBoot,
    /// Auxiliary-controller firmware package.
    Auxiliary,
}

/// Validated product profile for the Rust firmware build graph.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProductProfile {
    printer: PrinterKind,
    board: BoardKind,
    mcu: McuKind,
    bootloader_mode: BootloaderMode,
    features: FeatureSet,
}

impl ProductProfile {
    /// Creates a profile only when the hardware and features match the current
    /// supported reference matrix.
    pub fn new(
        printer: PrinterKind,
        board: BoardKind,
        mcu: McuKind,
        bootloader_mode: BootloaderMode,
        features: FeatureSet,
    ) -> Result<Self, InvariantError> {
        if !is_supported_hardware(printer, board, mcu, bootloader_mode) {
            return Err(InvariantError::UnsupportedHardwareCombination {
                printer,
                board,
                mcu,
                bootloader_mode,
            });
        }

        for feature in features.iter() {
            if !is_supported_feature(printer, board, feature) {
                return Err(InvariantError::UnsupportedFeature {
                    printer,
                    board,
                    feature,
                });
            }
        }

        Ok(Self {
            printer,
            board,
            mcu,
            bootloader_mode,
            features,
        })
    }

    /// Returns the selected printer.
    pub fn printer(&self) -> PrinterKind {
        self.printer
    }

    /// Returns the selected board.
    pub fn board(&self) -> BoardKind {
        self.board
    }

    /// Returns the selected MCU.
    pub fn mcu(&self) -> McuKind {
        self.mcu
    }

    /// Returns the selected bootloader mode.
    pub fn bootloader_mode(&self) -> BootloaderMode {
        self.bootloader_mode
    }

    /// Returns the validated feature set.
    pub fn features(&self) -> &FeatureSet {
        &self.features
    }

    /// Returns true when the board is an auxiliary controller rather than a
    /// master-board firmware image.
    pub fn is_auxiliary(&self) -> bool {
        matches!(
            self.board,
            BoardKind::Dwarf | BoardKind::ModularBed | BoardKind::XBuddyExtension
        )
    }
}

fn is_supported_hardware(
    printer: PrinterKind,
    board: BoardKind,
    mcu: McuKind,
    bootloader_mode: BootloaderMode,
) -> bool {
    let board_and_mcu_match = matches!(
        (printer, board, mcu),
        (PrinterKind::Mini, BoardKind::Buddy, McuKind::Stm32F407Vg)
            | (
                PrinterKind::CoreOne | PrinterKind::Mk4 | PrinterKind::Mk35 | PrinterKind::Ix,
                BoardKind::XBuddy,
                McuKind::Stm32F427Zi,
            )
            | (PrinterKind::Xl, BoardKind::XlBuddy, McuKind::Stm32F427Zi)
            | (
                PrinterKind::XlDevKit,
                BoardKind::XlDevKitXlBuddy,
                McuKind::Stm32F427Zi
            )
            | (
                PrinterKind::Xl | PrinterKind::XlDevKit,
                BoardKind::Dwarf,
                McuKind::Stm32G070RbT6,
            )
            | (
                PrinterKind::Xl | PrinterKind::Ix,
                BoardKind::ModularBed,
                McuKind::Stm32G070RbT6,
            )
            | (
                PrinterKind::CoreOne,
                BoardKind::XBuddyExtension,
                McuKind::Stm32H503CbU7,
            )
    );

    if !board_and_mcu_match {
        return false;
    }

    matches!(
        (board, bootloader_mode),
        (
            BoardKind::Buddy | BoardKind::XBuddy | BoardKind::XlBuddy | BoardKind::XlDevKitXlBuddy,
            BootloaderMode::Boot | BootloaderMode::NoBoot
        ) | (
            BoardKind::Dwarf | BoardKind::ModularBed | BoardKind::XBuddyExtension,
            BootloaderMode::Auxiliary
        )
    )
}

fn is_supported_feature(printer: PrinterKind, board: BoardKind, feature: Feature) -> bool {
    if matches!(
        board,
        BoardKind::Dwarf | BoardKind::ModularBed | BoardKind::XBuddyExtension
    ) {
        return matches!(
            (board, feature),
            (BoardKind::Dwarf, Feature::Dwarf)
                | (BoardKind::ModularBed, Feature::ModularBed)
                | (BoardKind::XBuddyExtension, Feature::XBuddyExtension)
        );
    }

    match feature {
        Feature::WebUi | Feature::Connect | Feature::UsbDevice => true,
        Feature::Resources => !matches!(printer, PrinterKind::XlDevKit),
        Feature::Translations => !matches!(printer, PrinterKind::Ix | PrinterKind::XlDevKit),
        Feature::Touch => matches!(
            printer,
            PrinterKind::CoreOne | PrinterKind::Mk4 | PrinterKind::Xl
        ),
        Feature::Mmu2 => matches!(
            printer,
            PrinterKind::CoreOne | PrinterKind::Mk4 | PrinterKind::Mk35
        ),
        Feature::Puppies => matches!(
            printer,
            PrinterKind::CoreOne | PrinterKind::Xl | PrinterKind::Ix | PrinterKind::XlDevKit
        ),
        Feature::Dwarf => matches!(printer, PrinterKind::Xl | PrinterKind::XlDevKit),
        Feature::ModularBed => matches!(printer, PrinterKind::Xl | PrinterKind::Ix),
        Feature::XBuddyExtension | Feature::Nfc => matches!(printer, PrinterKind::CoreOne),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn accepts_supported_master_board_profile() {
        // Arrange
        let features = FeatureSet::from_features([
            Feature::WebUi,
            Feature::Connect,
            Feature::Resources,
            Feature::Translations,
        ]);

        // Act
        let result = ProductProfile::new(
            PrinterKind::Mini,
            BoardKind::Buddy,
            McuKind::Stm32F407Vg,
            BootloaderMode::Boot,
            features,
        );

        // Assert
        assert!(result.is_ok());
    }

    #[test]
    fn rejects_invalid_board_mcu_pair() {
        // Arrange
        let features = FeatureSet::empty();

        // Act
        let result = ProductProfile::new(
            PrinterKind::Mini,
            BoardKind::XBuddy,
            McuKind::Stm32F427Zi,
            BootloaderMode::Boot,
            features,
        );

        // Assert
        assert!(matches!(
            result,
            Err(InvariantError::UnsupportedHardwareCombination { .. })
        ));
    }

    #[test]
    fn rejects_master_bootloader_mode_for_auxiliary_board() {
        // Arrange
        let features = FeatureSet::from_features([Feature::Dwarf]);

        // Act
        let result = ProductProfile::new(
            PrinterKind::Xl,
            BoardKind::Dwarf,
            McuKind::Stm32G070RbT6,
            BootloaderMode::Boot,
            features,
        );

        // Assert
        assert!(matches!(
            result,
            Err(InvariantError::UnsupportedHardwareCombination { .. })
        ));
    }

    #[test]
    fn rejects_feature_for_wrong_product_family() {
        // Arrange
        let features = FeatureSet::from_features([Feature::Mmu2]);

        // Act
        let result = ProductProfile::new(
            PrinterKind::Mini,
            BoardKind::Buddy,
            McuKind::Stm32F407Vg,
            BootloaderMode::Boot,
            features,
        );

        // Assert
        assert!(matches!(
            result,
            Err(InvariantError::UnsupportedFeature {
                feature: Feature::Mmu2,
                ..
            })
        ));
    }

    #[test]
    fn accepts_auxiliary_controller_profile() {
        // Arrange
        let features = FeatureSet::from_features([Feature::XBuddyExtension]);

        // Act
        let result = ProductProfile::new(
            PrinterKind::CoreOne,
            BoardKind::XBuddyExtension,
            McuKind::Stm32H503CbU7,
            BootloaderMode::Auxiliary,
            features,
        );

        // Assert
        assert!(matches!(result, Ok(profile) if profile.is_auxiliary()));
    }
}
