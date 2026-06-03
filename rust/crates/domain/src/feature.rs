use std::collections::BTreeSet;

/// Firmware feature flags that affect product-specific behavior.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Feature {
    /// Local PrusaLink/WUI server.
    WebUi,
    /// Prusa Connect client.
    Connect,
    /// External resource package support.
    Resources,
    /// Compiled translation assets.
    Translations,
    /// Touch UI feature surface.
    Touch,
    /// MMU2 runtime integration.
    Mmu2,
    /// XL/iX/CORE One auxiliary-controller ecosystem.
    Puppies,
    /// Dwarf toolhead auxiliary firmware.
    Dwarf,
    /// Modular bed auxiliary firmware.
    ModularBed,
    /// CORE One xBuddy Extension firmware.
    XBuddyExtension,
    /// USB device support.
    UsbDevice,
    /// NFC feature surface.
    Nfc,
}

/// De-duplicated feature set for a firmware profile.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct FeatureSet {
    features: BTreeSet<Feature>,
}

impl FeatureSet {
    /// Creates an empty feature set.
    pub fn empty() -> Self {
        Self::default()
    }

    /// Creates a de-duplicated feature set from raw feature flags.
    pub fn from_features(features: impl IntoIterator<Item = Feature>) -> Self {
        Self {
            features: features.into_iter().collect(),
        }
    }

    /// Returns true when the feature is present.
    pub fn contains(&self, feature: Feature) -> bool {
        self.features.contains(&feature)
    }

    /// Iterates over features in deterministic order.
    pub fn iter(&self) -> impl Iterator<Item = Feature> + '_ {
        self.features.iter().copied()
    }
}
