use crate::InvariantError;

fn is_path_free_printable_ascii(raw: &str) -> bool {
    raw != "."
        && raw != ".."
        && !raw.contains("..")
        && !raw.contains('/')
        && !raw.contains('\\')
        && raw.bytes().all(|byte| byte.is_ascii_graphic())
}

fn is_valid_row_id(raw: &str) -> bool {
    !raw.is_empty() && raw.len() <= 96 && is_path_free_printable_ascii(raw)
}

fn is_non_empty_printable_text(raw: &str) -> bool {
    !raw.trim().is_empty() && raw.len() <= 240 && raw.bytes().all(|byte| !byte.is_ascii_control())
}

/// Phase 11 cutover evidence row identity parsed before verifier or adapter code uses it.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct CutoverEvidenceRowId(String);

impl CutoverEvidenceRowId {
    /// Parses a path-free printable ASCII row ID at most 96 bytes long.
    pub fn try_new(raw: &str) -> Result<Self, InvariantError> {
        if raw.is_empty() {
            return Err(InvariantError::EmptyCutoverEvidenceRowId);
        }

        if !is_valid_row_id(raw) {
            return Err(InvariantError::InvalidCutoverEvidenceRowId);
        }

        Ok(Self(raw.to_owned()))
    }

    /// Returns the validated row ID as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Locality and acceptance scope for Phase 11 evidence.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ProofScope {
    /// Locally provable by deterministic static, unit, or contract checks.
    Local,
    /// Requires CI evidence outside a local deterministic check.
    Ci,
    /// Requires simulator-flow evidence.
    Simulator,
    /// Requires hardware smoke evidence.
    HardwareSmoke,
    /// Requires manual hardware or failure-injection evidence.
    ManualHardwareRequired,
    /// Requires retained-code boundary and justification review.
    RetainedCodeJustification,
}

impl ProofScope {
    /// Returns the manifest string for this proof scope.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Local => "local",
            Self::Ci => "ci",
            Self::Simulator => "simulator",
            Self::HardwareSmoke => "hardware-smoke",
            Self::ManualHardwareRequired => "manual-hardware-required",
            Self::RetainedCodeJustification => "retained-code-justification",
        }
    }
}

/// Evidence class for a Phase 11 parity or cutover claim.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum EvidenceClass {
    /// Pure Rust unit test evidence.
    RustUnitTest,
    /// Adapter or domain contract test evidence.
    AdapterContractTest,
    /// Generated-output drift check evidence.
    GeneratedDriftCheck,
    /// Reference fixture comparison evidence.
    ReferenceFixtureComparison,
    /// Simulator flow evidence.
    SimulatorFlow,
    /// Network/TLS/API check evidence.
    NetworkTlsApiCheck,
    /// Release artifact check evidence.
    ReleaseArtifactCheck,
    /// Hardware smoke evidence.
    HardwareSmoke,
    /// Manual hardware evidence.
    ManualHardwareRequired,
    /// Retained-code justification evidence.
    RetainedCodeJustification,
    /// Source audit evidence.
    SourceAudit,
    /// Static verifier evidence.
    StaticVerifier,
}

impl EvidenceClass {
    /// Returns whether this evidence class can support a local proof scope.
    pub fn is_local_proof(self) -> bool {
        matches!(
            self,
            Self::RustUnitTest
                | Self::AdapterContractTest
                | Self::GeneratedDriftCheck
                | Self::ReferenceFixtureComparison
                | Self::SourceAudit
                | Self::StaticVerifier
        )
    }

    /// Returns the manifest string for this evidence class.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::RustUnitTest => "rust-unit-test",
            Self::AdapterContractTest => "adapter-contract-test",
            Self::GeneratedDriftCheck => "generated-drift-check",
            Self::ReferenceFixtureComparison => "reference-fixture-comparison",
            Self::SimulatorFlow => "simulator-flow",
            Self::NetworkTlsApiCheck => "network-tls-api-check",
            Self::ReleaseArtifactCheck => "release-artifact-check",
            Self::HardwareSmoke => "hardware-smoke",
            Self::ManualHardwareRequired => "manual-hardware-required",
            Self::RetainedCodeJustification => "retained-code-justification",
            Self::SourceAudit => "source-audit",
            Self::StaticVerifier => "static-verifier",
        }
    }
}

/// Cutover status vocabulary used by Phase 11 evidence contracts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum CutoverStatus {
    /// Local deterministic verification passed.
    PassedLocal,
    /// CI evidence is pending.
    PendingCi,
    /// Simulator evidence is pending.
    PendingSimulator,
    /// Hardware smoke evidence is pending.
    PendingHardwareSmoke,
    /// Manual hardware evidence is required.
    ManualHardwareRequired,
    /// Retained code has accepted source-backed justification.
    AcceptedRetainedCode,
    /// Cutover status is blocked.
    Blocked,
    /// Cutover is not ready.
    NotCutoverReady,
}

/// Reference comparison strategy.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ReferenceComparisonKind {
    /// Normalized semantic comparison without byte identity claims.
    NormalizedSemantic,
    /// Byte identity comparison allowed only with explicit fixture and normalization rule.
    ByteIdentityWithFixture,
}

/// Validated reference comparison contract for Phase 11 cutover evidence.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReferenceComparisonContract {
    row_id: CutoverEvidenceRowId,
    proof_scope: ProofScope,
    evidence_class: EvidenceClass,
    comparison_kind: ReferenceComparisonKind,
    maybe_fixture_id: Option<String>,
    maybe_normalization_rule: Option<String>,
    byte_identity_claim: bool,
}

impl ReferenceComparisonContract {
    /// Creates a reference comparison contract only when proof scope and
    /// comparison claims are internally consistent.
    pub fn new(
        row_id: CutoverEvidenceRowId,
        proof_scope: ProofScope,
        evidence_class: EvidenceClass,
        comparison_kind: ReferenceComparisonKind,
        maybe_fixture_id: Option<&str>,
        maybe_normalization_rule: Option<&str>,
        byte_identity_claim: bool,
    ) -> Result<Self, InvariantError> {
        if matches!(proof_scope, ProofScope::Local) && !evidence_class.is_local_proof() {
            return Err(InvariantError::InvalidCutoverProofScope);
        }

        let maybe_fixture_id = maybe_fixture_id.map(str::to_owned);
        let maybe_normalization_rule = maybe_normalization_rule.map(str::to_owned);
        let has_fixture = maybe_fixture_id.as_deref().is_some_and(is_valid_row_id);
        let has_normalization_rule = maybe_normalization_rule
            .as_deref()
            .is_some_and(is_non_empty_printable_text);

        if maybe_fixture_id
            .as_deref()
            .is_some_and(|raw| !is_valid_row_id(raw))
            || maybe_normalization_rule
                .as_deref()
                .is_some_and(|raw| !is_non_empty_printable_text(raw))
        {
            return Err(InvariantError::InvalidReferenceComparisonContract);
        }

        match comparison_kind {
            ReferenceComparisonKind::NormalizedSemantic => {
                if byte_identity_claim {
                    return Err(InvariantError::InvalidReferenceComparisonContract);
                }
            }
            ReferenceComparisonKind::ByteIdentityWithFixture => {
                if !byte_identity_claim || !has_fixture || !has_normalization_rule {
                    return Err(InvariantError::InvalidReferenceComparisonContract);
                }
            }
        }

        Ok(Self {
            row_id,
            proof_scope,
            evidence_class,
            comparison_kind,
            maybe_fixture_id,
            maybe_normalization_rule,
            byte_identity_claim,
        })
    }

    /// Returns the row ID.
    pub fn row_id(&self) -> &CutoverEvidenceRowId {
        &self.row_id
    }

    /// Returns the proof scope.
    pub fn proof_scope(&self) -> ProofScope {
        self.proof_scope
    }

    /// Returns the evidence class.
    pub fn evidence_class(&self) -> EvidenceClass {
        self.evidence_class
    }

    /// Returns the comparison kind.
    pub fn comparison_kind(&self) -> ReferenceComparisonKind {
        self.comparison_kind
    }

    /// Returns the optional fixture identity.
    pub fn maybe_fixture_id(&self) -> Option<&str> {
        self.maybe_fixture_id.as_deref()
    }

    /// Returns the optional normalization rule.
    pub fn maybe_normalization_rule(&self) -> Option<&str> {
        self.maybe_normalization_rule.as_deref()
    }

    /// Returns whether this contract claims byte identity.
    pub fn byte_identity_claim(&self) -> bool {
        self.byte_identity_claim
    }
}

/// Minimum cutover criteria that must be represented before demotion can be considered.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum CutoverCriterion {
    /// Every v1 requirement maps to evidence.
    AllV1RequirementsMapped,
    /// Local verifier passed.
    LocalVerifierPassed,
    /// Non-local gates are identified.
    NonLocalGatesIdentified,
    /// Retained-code justifications are accepted.
    RetainedCodeJustificationsAccepted,
    /// Intentional deltas are documented.
    IntentionalDeltasDocumented,
    /// Overclaim scan is clean.
    OverclaimScanClean,
    /// Reference demotion remains blocked until evidence is complete.
    ReferenceDemotionBlocked,
}

/// Retained-code disposition in final cutover evidence.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum RetainedCodeDisposition {
    /// Retained surface is accepted with source-backed justification.
    Accepted,
    /// Retained surface blocks cutover.
    Blocked,
    /// Retained surface is deferred beyond the current cutover gate.
    Deferred,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::InvariantError;

    #[test]
    fn rejects_invalid_cutover_evidence_row_ids() {
        // Arrange
        let valid_id = "ref-product-artifacts";
        let oversized_id = "a".repeat(97);
        let invalid_ids = [
            "",
            ".",
            "..",
            "../ref",
            "ref\\artifact",
            "ref artifact",
            "ref..artifact",
            "ref\nartifact",
        ];

        // Act
        let valid_result = CutoverEvidenceRowId::try_new(valid_id);
        let oversized_result = CutoverEvidenceRowId::try_new(&oversized_id);
        let invalid_results = invalid_ids.map(CutoverEvidenceRowId::try_new);

        // Assert
        assert!(matches!(
            valid_result,
            Ok(row_id) if row_id.as_str() == valid_id
        ));
        assert_eq!(
            invalid_results[0],
            Err(InvariantError::EmptyCutoverEvidenceRowId)
        );
        assert!(invalid_results[1..].iter().all(Result::is_err));
        assert_eq!(
            oversized_result,
            Err(InvariantError::InvalidCutoverEvidenceRowId)
        );
    }

    #[test]
    fn rejects_non_local_evidence_as_local_cutover_proof() {
        // Arrange
        let row_id =
            CutoverEvidenceRowId::try_new("ref-network-tls-api-behavior").expect("row ID is valid");
        let non_local_evidence_classes = [
            EvidenceClass::SimulatorFlow,
            EvidenceClass::HardwareSmoke,
            EvidenceClass::ManualHardwareRequired,
            EvidenceClass::RetainedCodeJustification,
        ];

        // Act
        let results = non_local_evidence_classes.map(|evidence_class| {
            ReferenceComparisonContract::new(
                row_id.clone(),
                ProofScope::Local,
                evidence_class,
                ReferenceComparisonKind::NormalizedSemantic,
                None,
                Some("compare normalized fixture identities"),
                false,
            )
        });

        // Assert
        assert!(
            results
                .iter()
                .all(|result| *result == Err(InvariantError::InvalidCutoverProofScope))
        );
    }

    #[test]
    fn accepts_normalized_semantic_reference_comparison_without_fixture() {
        // Arrange
        let row_id =
            CutoverEvidenceRowId::try_new("ref-generated-resources").expect("row ID is valid");

        // Act
        let result = ReferenceComparisonContract::new(
            row_id,
            ProofScope::Ci,
            EvidenceClass::ReferenceFixtureComparison,
            ReferenceComparisonKind::NormalizedSemantic,
            None,
            Some("compare generator identity and tracked output names"),
            false,
        );

        // Assert
        assert!(matches!(
            result,
            Ok(contract)
                if contract.comparison_kind() == ReferenceComparisonKind::NormalizedSemantic
                    && contract.maybe_fixture_id().is_none()
                    && !contract.byte_identity_claim()
        ));
    }

    #[test]
    fn requires_fixture_and_normalization_for_byte_identity_claim() {
        // Arrange
        let row_id =
            CutoverEvidenceRowId::try_new("ref-release-metadata").expect("row ID is valid");

        // Act
        let missing_fixture_result = ReferenceComparisonContract::new(
            row_id.clone(),
            ProofScope::Ci,
            EvidenceClass::ReferenceFixtureComparison,
            ReferenceComparisonKind::ByteIdentityWithFixture,
            None,
            Some("normalize release metadata"),
            true,
        );
        let missing_normalization_result = ReferenceComparisonContract::new(
            row_id.clone(),
            ProofScope::Ci,
            EvidenceClass::ReferenceFixtureComparison,
            ReferenceComparisonKind::ByteIdentityWithFixture,
            Some("release-candidate-metadata"),
            None,
            true,
        );
        let valid_result = ReferenceComparisonContract::new(
            row_id,
            ProofScope::Ci,
            EvidenceClass::ReferenceFixtureComparison,
            ReferenceComparisonKind::ByteIdentityWithFixture,
            Some("release-candidate-metadata"),
            Some("normalize paths and timestamps before byte comparison"),
            true,
        );

        // Assert
        assert_eq!(
            missing_fixture_result,
            Err(InvariantError::InvalidReferenceComparisonContract)
        );
        assert_eq!(
            missing_normalization_result,
            Err(InvariantError::InvalidReferenceComparisonContract)
        );
        assert!(valid_result.is_ok());
    }
}
