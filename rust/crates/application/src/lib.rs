#![forbid(unsafe_code)]

//! Pure application policies built on the firmware domain model.

use buddy_domain::{ArtifactKind, ProductProfile};

/// Returns the artifact kinds expected for a validated product profile.
pub fn release_artifact_kinds(profile: &ProductProfile) -> &'static [ArtifactKind] {
    if profile.is_auxiliary() {
        return &[ArtifactKind::Bin, ArtifactKind::AuxiliaryManifest];
    }

    &[
        ArtifactKind::Bin,
        ArtifactKind::Map,
        ArtifactKind::Bbf,
        ArtifactKind::Dfu,
        ArtifactKind::Provenance,
    ]
}

#[cfg(test)]
mod tests {
    use super::*;
    use buddy_domain::{BoardKind, BootloaderMode, Feature, FeatureSet, McuKind, PrinterKind};

    #[test]
    fn includes_release_packages_for_master_board_profiles() {
        // Arrange
        let profile = ProductProfile::new(
            PrinterKind::Mini,
            BoardKind::Buddy,
            McuKind::Stm32F407Vg,
            BootloaderMode::Boot,
            FeatureSet::empty(),
        )
        .expect("MINI/BUDDY/F407 boot profile is part of the supported reference matrix");

        // Act
        let kinds = release_artifact_kinds(&profile);

        // Assert
        assert!(kinds.contains(&ArtifactKind::Bbf));
        assert!(kinds.contains(&ArtifactKind::Dfu));
    }

    #[test]
    fn keeps_auxiliary_controller_artifacts_narrow() {
        // Arrange
        let profile = ProductProfile::new(
            PrinterKind::Xl,
            BoardKind::Dwarf,
            McuKind::Stm32G070RbT6,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::Dwarf]),
        )
        .expect("XL/DWARF/G070 auxiliary profile is part of the supported reference matrix");

        // Act
        let kinds = release_artifact_kinds(&profile);

        // Assert
        assert_eq!(kinds, &[ArtifactKind::Bin, ArtifactKind::AuxiliaryManifest]);
    }
}
