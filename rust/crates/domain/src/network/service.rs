use super::identity::{
    NetworkEvidenceClass, NetworkParityRowId, NetworkProofScope, SecretHandling,
};
use crate::{Feature, FeatureSet, InvariantError};

/// Product-gated Phase 9 network service surface.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum NetworkServiceSurface {
    /// Prusa Connect client surface.
    PrusaConnect,
    /// PrusaLink/WUI local service surface.
    PrusaLinkWui,
    /// SNTP service surface.
    Sntp,
    /// mDNS service surface.
    Mdns,
    /// DNS resolver service surface.
    Dns,
    /// Metrics UDP service surface.
    Metrics,
    /// Syslog UDP service surface.
    Syslog,
}

impl NetworkServiceSurface {
    /// Parses a network service surface string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "prusa-connect" => Ok(Self::PrusaConnect),
            "prusa-link-wui" => Ok(Self::PrusaLinkWui),
            "sntp" => Ok(Self::Sntp),
            "mdns" => Ok(Self::Mdns),
            "dns" => Ok(Self::Dns),
            "metrics" => Ok(Self::Metrics),
            "syslog" => Ok(Self::Syslog),
            _ => Err(InvariantError::InvalidNetworkServiceSurface),
        }
    }

    /// Returns the manifest string for this surface.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::PrusaConnect => "prusa-connect",
            Self::PrusaLinkWui => "prusa-link-wui",
            Self::Sntp => "sntp",
            Self::Mdns => "mdns",
            Self::Dns => "dns",
            Self::Metrics => "metrics",
            Self::Syslog => "syslog",
        }
    }
}

/// Raw inputs for creating a [`NetworkServiceContract`].
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NetworkServiceContractInput {
    /// Network service surface.
    pub surface: NetworkServiceSurface,
    /// Product feature set available for this service contract.
    pub features: FeatureSet,
}

/// Product-feature-gated network service contract.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NetworkServiceContract {
    surface: NetworkServiceSurface,
    features: FeatureSet,
}

impl NetworkServiceContract {
    /// Creates a service contract when the required feature is enabled.
    pub fn new(
        surface: NetworkServiceSurface,
        features: FeatureSet,
    ) -> Result<Self, InvariantError> {
        Self::from_input(NetworkServiceContractInput { surface, features })
    }

    /// Creates a service contract from raw validated input.
    pub fn from_input(input: NetworkServiceContractInput) -> Result<Self, InvariantError> {
        let NetworkServiceContractInput { surface, features } = input;
        let required_features: &[Feature] = match surface {
            NetworkServiceSurface::PrusaConnect => &[Feature::Connect, Feature::WebUi],
            NetworkServiceSurface::PrusaLinkWui
            | NetworkServiceSurface::Sntp
            | NetworkServiceSurface::Mdns
            | NetworkServiceSurface::Dns
            | NetworkServiceSurface::Metrics
            | NetworkServiceSurface::Syslog => &[Feature::WebUi],
        };

        if required_features
            .iter()
            .any(|feature| !features.contains(*feature))
        {
            return Err(InvariantError::UnsupportedNetworkService);
        }

        Ok(Self { surface, features })
    }

    /// Returns the service surface.
    pub fn surface(&self) -> NetworkServiceSurface {
        self.surface
    }

    /// Returns the feature set used to validate the service.
    pub fn features(&self) -> &FeatureSet {
        &self.features
    }
}

/// Raw inputs for creating a [`NetworkParityContract`].
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NetworkParityContractInput {
    /// Phase 9 row identity.
    pub row_id: NetworkParityRowId,
    /// Evidence class.
    pub evidence_class: NetworkEvidenceClass,
    /// Proof scope.
    pub proof_scope: NetworkProofScope,
    /// Secret handling policy.
    pub secret_handling: SecretHandling,
}

/// Validated Phase 9 network parity row contract.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NetworkParityContract {
    row_id: NetworkParityRowId,
    evidence_class: NetworkEvidenceClass,
    proof_scope: NetworkProofScope,
    secret_handling: SecretHandling,
}

impl NetworkParityContract {
    /// Creates a parity contract when evidence/proof compatibility is valid.
    pub fn new(input: NetworkParityContractInput) -> Result<Self, InvariantError> {
        let NetworkParityContractInput {
            row_id,
            evidence_class,
            proof_scope,
            secret_handling,
        } = input;

        if matches!(proof_scope, NetworkProofScope::Local) && !evidence_class.is_local_proof() {
            return Err(InvariantError::InvalidNetworkProofScope);
        }

        Ok(Self {
            row_id,
            evidence_class,
            proof_scope,
            secret_handling,
        })
    }

    /// Returns the row ID.
    pub fn row_id(&self) -> &NetworkParityRowId {
        &self.row_id
    }

    /// Returns the evidence class.
    pub fn evidence_class(&self) -> NetworkEvidenceClass {
        self.evidence_class
    }

    /// Returns the proof scope.
    pub fn proof_scope(&self) -> NetworkProofScope {
        self.proof_scope
    }

    /// Returns the secret-handling policy.
    pub fn secret_handling(&self) -> SecretHandling {
        self.secret_handling
    }

    /// Returns whether this contract permits credential value material.
    pub fn allows_value_material(&self) -> bool {
        self.secret_handling.allows_value_material()
    }
}
