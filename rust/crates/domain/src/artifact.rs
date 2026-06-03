use crate::{InvariantError, ProductProfile};

/// Release artifact categories surfaced by the current firmware reference.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ArtifactKind {
    /// Raw firmware binary.
    Bin,
    /// Prusa firmware package.
    Bbf,
    /// DFU package.
    Dfu,
    /// Linker map output.
    Map,
    /// Resource image.
    ResourceImage,
    /// Resource package.
    ResourcePackage,
    /// Version and build provenance metadata.
    Provenance,
    /// Auxiliary-controller manifest.
    AuxiliaryManifest,
}

impl ArtifactKind {
    /// Required filename suffix for this artifact kind.
    pub fn expected_suffix(self) -> &'static str {
        match self {
            Self::Bin => ".bin",
            Self::Bbf => ".bbf",
            Self::Dfu => ".dfu",
            Self::Map => ".map",
            Self::ResourceImage => ".resource.img",
            Self::ResourcePackage => ".resource.pkg",
            Self::Provenance => ".provenance.json",
            Self::AuxiliaryManifest => ".manifest.json",
        }
    }
}

/// Plain release artifact file name with path syntax rejected.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct ArtifactFileName(String);

impl ArtifactFileName {
    /// Parses a raw file name into a safe artifact file name.
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if raw.is_empty() {
            return Err(InvariantError::EmptyArtifactName);
        }

        if raw.contains('/') || raw.contains('\\') || raw.split('.').any(|part| part == "..") {
            return Err(InvariantError::ArtifactNameContainsPath);
        }

        Ok(Self(raw))
    }

    /// Returns the artifact file name as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Validated request for producing a release artifact for a product profile.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ArtifactRequest {
    profile: ProductProfile,
    kind: ArtifactKind,
    name: ArtifactFileName,
}

impl ArtifactRequest {
    /// Creates an artifact request only when the file name suffix matches the
    /// declared kind.
    pub fn new(
        profile: ProductProfile,
        kind: ArtifactKind,
        name: ArtifactFileName,
    ) -> Result<Self, InvariantError> {
        let expected_suffix = kind.expected_suffix();
        if !name.as_str().ends_with(expected_suffix) {
            return Err(InvariantError::ArtifactSuffixMismatch {
                kind,
                expected_suffix,
            });
        }

        Ok(Self {
            profile,
            kind,
            name,
        })
    }

    /// Returns the profile that owns this artifact.
    pub fn profile(&self) -> &ProductProfile {
        &self.profile
    }

    /// Returns the artifact kind.
    pub fn kind(&self) -> ArtifactKind {
        self.kind
    }

    /// Returns the artifact file name.
    pub fn name(&self) -> &ArtifactFileName {
        &self.name
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{BoardKind, BootloaderMode, FeatureSet, McuKind, PrinterKind};

    fn mini_profile() -> ProductProfile {
        ProductProfile::new(
            PrinterKind::Mini,
            BoardKind::Buddy,
            McuKind::Stm32F407Vg,
            BootloaderMode::Boot,
            FeatureSet::empty(),
        )
        .expect("MINI/BUDDY/F407 boot profile is part of the supported reference matrix")
    }

    #[test]
    fn rejects_path_like_artifact_name() {
        // Arrange
        let raw_name = "../firmware.bin";

        // Act
        let result = ArtifactFileName::parse(raw_name);

        // Assert
        assert_eq!(result, Err(InvariantError::ArtifactNameContainsPath));
    }

    #[test]
    fn rejects_suffix_mismatch() {
        // Arrange
        let profile = mini_profile();
        let name = ArtifactFileName::parse("mini.dfu").expect("plain artifact name is valid");

        // Act
        let result = ArtifactRequest::new(profile, ArtifactKind::Bbf, name);

        // Assert
        assert!(matches!(
            result,
            Err(InvariantError::ArtifactSuffixMismatch {
                kind: ArtifactKind::Bbf,
                expected_suffix: ".bbf",
            })
        ));
    }

    #[test]
    fn accepts_matching_artifact_kind_and_suffix() {
        // Arrange
        let profile = mini_profile();
        let name = ArtifactFileName::parse("mini_boot.bbf").expect("plain artifact name is valid");

        // Act
        let result = ArtifactRequest::new(profile, ArtifactKind::Bbf, name);

        // Assert
        assert!(matches!(result, Ok(request) if request.kind() == ArtifactKind::Bbf));
    }
}
