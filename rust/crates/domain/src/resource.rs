use crate::InvariantError;

const STANDARD_IMAGE_RUNTIME_PATHS: &[&str] = &["qoi.data", "resources/revision_standard.hpp"];
const BOOTLOADER_IMAGE_RUNTIME_PATHS: &[&str] = &["/bootloader.bin"];
const ESP32_BLOB_RUNTIME_PATHS: &[&str] = &[
    "/esp/uart_wifi.bin",
    "/esp/bootloader.bin",
    "/esp/partition-table.bin",
];
const ESP8266_BLOB_RUNTIME_PATHS: &[&str] = &[
    "/esp/uart_wifi.bin",
    "/esp/bootloader.bin",
    "/esp/partition-table.bin",
];
const WUI_STATIC_ASSET_RUNTIME_PATHS: &[&str] = &["/web/index.html", "/web/favicon.ico"];
const QOI_DATA_RUNTIME_PATHS: &[&str] = &["qoi.data"];
const LANGUAGE_PACK_RUNTIME_PATHS: &[&str] = &["/lang/*.mo"];
const FONT_ASSET_RUNTIME_PATHS: &[&str] = &[
    "src/gui/res/cc/font_regular_11x18_full.hpp",
    "src/gui/res/cc/*.hpp",
];
const MMU_FIRMWARE_RUNTIME_PATHS: &[&str] = &["/mmu/fw.bin"];
const HASH_AND_REVISION_RUNTIME_PATHS: &[&str] = &["resources/revision_standard.hpp"];
const RUNTIME_BOOTSTRAP_PATHS: &[&str] = &["src/resources/bootstrap.cpp"];

/// Resource or generated header path visible to runtime/resource packaging.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct ResourceRuntimePath(String);

impl ResourceRuntimePath {
    /// Parses a resource path while rejecting traversal and non-portable syntax.
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if raw.is_empty() {
            return Err(InvariantError::EmptyResourcePath);
        }

        if raw.split('/').any(|segment| segment == "..") {
            return Err(InvariantError::ResourcePathContainsTraversal);
        }

        if raw.len() > 160 || raw.contains('\\') || raw.bytes().any(|byte| byte.is_ascii_control())
        {
            return Err(InvariantError::InvalidResourcePath);
        }

        Ok(Self(raw))
    }

    /// Returns the resource runtime path as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Phase 7 resource or generated-output compatibility surface.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ResourceSurface {
    /// Standard firmware resource image.
    StandardImage,
    /// Bootloader resource image.
    BootloaderImage,
    /// ESP32 firmware blobs packaged as resources.
    Esp32Blobs,
    /// ESP8266 firmware blobs packaged as resources.
    Esp8266Blobs,
    /// WUI static assets packaged under `/web`.
    WuiStaticAssets,
    /// QOI image data resource.
    QoiData,
    /// Translation language packs.
    LanguagePacks,
    /// Font assets generated from translation/font tooling.
    FontAssets,
    /// MMU firmware resource.
    MmuFirmware,
    /// Resource hash and revision generated headers.
    HashAndRevision,
    /// Runtime resource bootstrap surface.
    RuntimeBootstrap,
}

impl ResourceSurface {
    /// Returns fixed runtime paths associated with this resource surface.
    pub fn required_runtime_paths(self) -> &'static [&'static str] {
        match self {
            Self::StandardImage => STANDARD_IMAGE_RUNTIME_PATHS,
            Self::BootloaderImage => BOOTLOADER_IMAGE_RUNTIME_PATHS,
            Self::Esp32Blobs => ESP32_BLOB_RUNTIME_PATHS,
            Self::Esp8266Blobs => ESP8266_BLOB_RUNTIME_PATHS,
            Self::WuiStaticAssets => WUI_STATIC_ASSET_RUNTIME_PATHS,
            Self::QoiData => QOI_DATA_RUNTIME_PATHS,
            Self::LanguagePacks => LANGUAGE_PACK_RUNTIME_PATHS,
            Self::FontAssets => FONT_ASSET_RUNTIME_PATHS,
            Self::MmuFirmware => MMU_FIRMWARE_RUNTIME_PATHS,
            Self::HashAndRevision => HASH_AND_REVISION_RUNTIME_PATHS,
            Self::RuntimeBootstrap => RUNTIME_BOOTSTRAP_PATHS,
        }
    }
}

/// Ownership class for generated outputs under Phase 7.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum GeneratedOutputOwnership {
    /// The generated output is tracked and reviewed as source.
    TrackedReviewedSource,
    /// The output is produced during the build from declared inputs.
    GeneratedAtBuild,
}

impl GeneratedOutputOwnership {
    /// Parses a generated-output ownership value.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "tracked-reviewed-source" => Ok(Self::TrackedReviewedSource),
            "generated-at-build" => Ok(Self::GeneratedAtBuild),
            _ => Err(InvariantError::InvalidGeneratedOutputOwnership),
        }
    }

    /// Returns the manifest string for this ownership value.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::TrackedReviewedSource => "tracked-reviewed-source",
            Self::GeneratedAtBuild => "generated-at-build",
        }
    }
}

/// Bazel label naming a generated-output check or update target.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct BazelLabel(String);

impl BazelLabel {
    /// Parses a Bazel label in `//package/path:target` form.
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if !raw.starts_with("//") {
            return Err(InvariantError::InvalidBazelLabel);
        }

        let Some(separator_index) = raw.find(':') else {
            return Err(InvariantError::InvalidBazelLabel);
        };

        if separator_index <= 2 || separator_index + 1 == raw.len() {
            return Err(InvariantError::InvalidBazelLabel);
        }

        if raw[separator_index + 1..].contains(':')
            || raw.contains('\\')
            || raw
                .bytes()
                .any(|byte| byte.is_ascii_control() || byte.is_ascii_whitespace())
        {
            return Err(InvariantError::InvalidBazelLabel);
        }

        Ok(Self(raw))
    }

    /// Returns the label as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }

    fn ends_with(&self, suffix: &str) -> bool {
        self.0.ends_with(suffix)
    }
}

/// Generated-output surface paired with check and update labels.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GeneratedSurface {
    id: String,
    ownership: GeneratedOutputOwnership,
    check_label: BazelLabel,
    update_label: BazelLabel,
}

impl GeneratedSurface {
    /// Creates a generated surface only when labels carry explicit check/update
    /// suffixes.
    pub fn new(
        id: impl Into<String>,
        ownership: GeneratedOutputOwnership,
        check_label: BazelLabel,
        update_label: BazelLabel,
    ) -> Result<Self, InvariantError> {
        if !check_label.ends_with("_check") {
            return Err(InvariantError::GeneratedCheckLabelMismatch);
        }

        if !update_label.ends_with("_update") {
            return Err(InvariantError::GeneratedUpdateLabelMismatch);
        }

        Ok(Self {
            id: id.into(),
            ownership,
            check_label,
            update_label,
        })
    }

    /// Returns the generated surface identifier.
    pub fn id(&self) -> &str {
        &self.id
    }

    /// Returns the generated-output ownership.
    pub fn ownership(&self) -> GeneratedOutputOwnership {
        self.ownership
    }

    /// Returns the generated-output check label.
    pub fn check_label(&self) -> &BazelLabel {
        &self.check_label
    }

    /// Returns the generated-output update label.
    pub fn update_label(&self) -> &BazelLabel {
        &self.update_label
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn accepts_known_resource_runtime_paths() {
        // Arrange
        let raw_paths = [
            "/web/index.html",
            "/esp/uart_wifi.bin",
            "qoi.data",
            "resources/revision_standard.hpp",
        ];

        // Act
        let results = raw_paths.map(ResourceRuntimePath::parse);

        // Assert
        assert!(results.iter().all(Result::is_ok));
    }

    #[test]
    fn rejects_resource_path_with_traversal() {
        // Arrange
        let raw_path = "../web/index.html";

        // Act
        let result = ResourceRuntimePath::parse(raw_path);

        // Assert
        assert_eq!(result, Err(InvariantError::ResourcePathContainsTraversal));
    }

    #[test]
    fn rejects_empty_resource_path() {
        // Arrange
        let raw_path = "";

        // Act
        let result = ResourceRuntimePath::parse(raw_path);

        // Assert
        assert_eq!(result, Err(InvariantError::EmptyResourcePath));
    }

    #[test]
    fn rejects_resource_path_with_backslash() {
        // Arrange
        let raw_path = "web\\index.html";

        // Act
        let result = ResourceRuntimePath::parse(raw_path);

        // Assert
        assert_eq!(result, Err(InvariantError::InvalidResourcePath));
    }

    #[test]
    fn parses_generated_output_ownership_values() {
        // Arrange
        let tracked = "tracked-reviewed-source";
        let generated = "generated-at-build";
        let invalid = "tracked-but-unreviewed";

        // Act
        let tracked_result = GeneratedOutputOwnership::parse(tracked);
        let generated_result = GeneratedOutputOwnership::parse(generated);
        let invalid_result = GeneratedOutputOwnership::parse(invalid);

        // Assert
        assert!(matches!(
            tracked_result,
            Ok(GeneratedOutputOwnership::TrackedReviewedSource)
        ));
        assert!(matches!(
            generated_result,
            Ok(GeneratedOutputOwnership::GeneratedAtBuild)
        ));
        assert_eq!(
            invalid_result,
            Err(InvariantError::InvalidGeneratedOutputOwnership)
        );
    }

    #[test]
    fn parses_bazel_label_shape() {
        // Arrange
        let valid_label = "//tools/bazel:generated_resources_check";
        let invalid_label = "tools/bazel:generated_resources_check";

        // Act
        let valid_result = BazelLabel::parse(valid_label);
        let invalid_result = BazelLabel::parse(invalid_label);

        // Assert
        assert!(valid_result.is_ok());
        assert_eq!(invalid_result, Err(InvariantError::InvalidBazelLabel));
    }

    #[test]
    fn standard_image_runtime_paths_include_qoi_and_revision_header() {
        // Arrange
        let surface = ResourceSurface::StandardImage;

        // Act
        let runtime_paths = surface.required_runtime_paths();

        // Assert
        assert!(runtime_paths.contains(&"qoi.data"));
        assert!(runtime_paths.contains(&"resources/revision_standard.hpp"));
    }

    #[test]
    fn generated_surface_rejects_mismatched_check_and_update_labels() {
        // Arrange
        let id = "resources";
        let ownership = GeneratedOutputOwnership::TrackedReviewedSource;
        let valid_check = BazelLabel::parse("//tools/bazel:generated_resources_check")
            .expect("valid check label shape");
        let valid_update = BazelLabel::parse("//tools/bazel:generated_resources_update")
            .expect("valid update label shape");
        let invalid_check = BazelLabel::parse("//tools/bazel:generated_resources_smoke")
            .expect("valid label shape");
        let invalid_update = BazelLabel::parse("//tools/bazel:generated_resources_write")
            .expect("valid label shape");

        // Act
        let check_result =
            GeneratedSurface::new(id, ownership, invalid_check, valid_update.clone());
        let update_result = GeneratedSurface::new(id, ownership, valid_check, invalid_update);

        // Assert
        assert_eq!(
            check_result,
            Err(InvariantError::GeneratedCheckLabelMismatch)
        );
        assert_eq!(
            update_result,
            Err(InvariantError::GeneratedUpdateLabelMismatch)
        );
    }
}
