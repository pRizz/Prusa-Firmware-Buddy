#[cfg(test)]
mod tests {
    use super::*;
    use crate::InvariantError;

    #[test]
    fn rejects_invalid_cutover_evidence_row_ids() {
        // Arrange
        let valid_id = "ref-product-artifacts";
        let oversized_id = "a".repeat(97);
        let invalid_ids = ["", ".", "..", "../ref", "ref\\artifact", "ref artifact", "ref\nartifact"];

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
