use super::*;
use crate::{Feature, FeatureSet, InvariantError};

fn valid_row_id() -> NetworkParityRowId {
    NetworkParityRowId::parse("connect-registration-token-fingerprint")
        .expect("test row ID is valid")
}

fn network_parity_input(
    evidence_class: NetworkEvidenceClass,
    proof_scope: NetworkProofScope,
) -> NetworkParityContractInput {
    NetworkParityContractInput {
        row_id: valid_row_id(),
        evidence_class,
        proof_scope,
        secret_handling: SecretHandling::None,
    }
}

#[test]
fn parses_network_evidence_classes() {
    // Arrange
    let local_evidence = "manifest-check";
    let unit_test_evidence = "unit-test-backed";
    let non_local_evidence = "simulator-flow";

    // Act
    let local_result = NetworkEvidenceClass::parse(local_evidence);
    let unit_test_result = NetworkEvidenceClass::parse(unit_test_evidence);
    let non_local_result = NetworkEvidenceClass::parse(non_local_evidence);

    // Assert
    assert!(matches!(
        local_result,
        Ok(evidence_class)
            if evidence_class.as_str() == local_evidence && evidence_class.is_local_proof()
    ));
    assert!(matches!(
        unit_test_result,
        Ok(evidence_class)
            if evidence_class.as_str() == unit_test_evidence
                && evidence_class.is_local_proof()
    ));
    assert!(matches!(
        non_local_result,
        Ok(evidence_class)
            if evidence_class.as_str() == non_local_evidence
                && !evidence_class.is_local_proof()
    ));
}

#[test]
fn rejects_non_local_network_evidence_as_local_proof() {
    // Arrange
    let non_local_evidence_classes = [
        NetworkEvidenceClass::SimulatorFlow,
        NetworkEvidenceClass::HardwareSmoke,
        NetworkEvidenceClass::ManualHardwareRequired,
    ];

    // Act
    let results = non_local_evidence_classes.map(|evidence_class| {
        NetworkParityContract::new(network_parity_input(
            evidence_class,
            NetworkProofScope::Local,
        ))
    });

    // Assert
    assert!(
        results
            .iter()
            .all(|result| *result == Err(InvariantError::InvalidNetworkProofScope))
    );
}

#[test]
fn rejects_invalid_network_parity_row_ids() {
    // Arrange
    let valid_id = "connect-registration-token-fingerprint";
    let oversized_id = "a".repeat(97);
    let invalid_ids = [
        "",
        "../connect",
        "connect\\token",
        "connect token",
        "connect\nid",
    ];

    // Act
    let valid_result = NetworkParityRowId::parse(valid_id);
    let oversized_result = NetworkParityRowId::parse(oversized_id);
    let invalid_results = invalid_ids.map(NetworkParityRowId::parse);

    // Assert
    assert!(matches!(
        valid_result,
        Ok(row_id) if row_id.as_str() == valid_id
    ));
    assert_eq!(
        invalid_results[0],
        Err(InvariantError::EmptyNetworkParityRowId)
    );
    assert!(invalid_results[1..].iter().all(Result::is_err));
    assert_eq!(
        oversized_result,
        Err(InvariantError::InvalidNetworkParityRowId)
    );
}

#[test]
fn keeps_secret_handling_named_only() {
    // Arrange
    let raw_no_secret_handling = "none";
    let raw_secret_handling = "named-only-redacted";

    // Act
    let no_secret_result = SecretHandling::parse(raw_no_secret_handling);
    let result = SecretHandling::parse(raw_secret_handling);

    // Assert
    assert!(matches!(
        no_secret_result,
        Ok(secret_handling)
            if secret_handling.as_str() == raw_no_secret_handling
                && !secret_handling.allows_value_material()
    ));
    assert!(matches!(
        result,
        Ok(secret_handling)
            if secret_handling.as_str() == raw_secret_handling
                && !secret_handling.allows_value_material()
    ));
}

#[test]
fn parses_connect_command_ids() {
    // Arrange
    let valid_id = "START_CONNECT_DOWNLOAD";
    let oversized_id = "A".repeat(97);
    let invalid_ids = ["", "../START", "START CONNECT", "START\nCONNECT"];

    // Act
    let valid_result = ConnectCommandId::parse(valid_id);
    let oversized_result = ConnectCommandId::parse(oversized_id);
    let invalid_results = invalid_ids.map(ConnectCommandId::parse);

    // Assert
    assert!(matches!(
        valid_result,
        Ok(command_id) if command_id.as_str() == valid_id
    ));
    assert!(
        invalid_results
            .iter()
            .all(|result| *result == Err(InvariantError::InvalidConnectCommandId))
    );
    assert_eq!(
        oversized_result,
        Err(InvariantError::InvalidConnectCommandId)
    );
}

#[test]
fn preserves_proxy_tls_only_limitations() {
    // Arrange
    let raw_proxy_mode = "http-connect-tls-only";

    // Act
    let result = ProxyMode::parse(raw_proxy_mode);

    // Assert
    assert!(matches!(
        result,
        Ok(proxy_mode)
            if proxy_mode.as_str() == raw_proxy_mode
                && proxy_mode.requires_tls()
                && !proxy_mode.supports_authentication()
    ));
}

#[test]
fn parses_wui_auth_modes() {
    // Arrange
    let raw_modes = ["digest", "api-key", "named-only-secret"];

    // Act
    let results = raw_modes.map(WuiAuthMode::parse);

    // Assert
    assert_eq!(
        results,
        [
            Ok(WuiAuthMode::Digest),
            Ok(WuiAuthMode::ApiKey),
            Ok(WuiAuthMode::NamedOnlySecret),
        ]
    );
}

#[test]
fn rejects_invalid_transfer_range() {
    // Arrange
    let start = 100;

    // Act
    let invalid_result = TransferRange::new(start, Some(99));
    let open_ended_result = TransferRange::new(start, None);

    // Assert
    assert_eq!(invalid_result, Err(InvariantError::InvalidTransferRange));
    assert!(matches!(
        open_ended_result,
        Ok(range) if range.start() == start && range.maybe_inclusive_end().is_none()
    ));
}

#[test]
fn stores_encrypted_payload_metadata_without_key_bytes() {
    // Arrange
    let key_identity = "transfer-key-id";

    // Act
    let metadata = EncryptedPayloadMetadata::aes_ctr_named_only(key_identity);

    // Assert
    assert!(matches!(
        metadata,
        Ok(metadata)
            if metadata.encryption_mode() == TransferEncryptionMode::AesCtr
                && metadata.key_identity() == Some(key_identity)
                && !metadata.allows_value_material()
    ));
}

#[test]
fn gates_connect_service_by_feature() {
    // Arrange
    let connect_features = FeatureSet::from_features([Feature::Connect]);
    let connect_with_wui_features = FeatureSet::from_features([Feature::Connect, Feature::WebUi]);

    // Act
    let missing_feature_result =
        NetworkServiceContract::new(NetworkServiceSurface::PrusaConnect, FeatureSet::empty());
    let missing_wui_result =
        NetworkServiceContract::new(NetworkServiceSurface::PrusaConnect, connect_features);
    let enabled_result = NetworkServiceContract::new(
        NetworkServiceSurface::PrusaConnect,
        connect_with_wui_features,
    );

    // Assert
    assert_eq!(
        missing_feature_result,
        Err(InvariantError::UnsupportedNetworkService)
    );
    assert_eq!(
        missing_wui_result,
        Err(InvariantError::UnsupportedNetworkService)
    );
    assert!(matches!(
        enabled_result,
        Ok(contract) if contract.surface() == NetworkServiceSurface::PrusaConnect
    ));
}

#[test]
fn gates_wui_and_local_services_by_feature() {
    // Arrange
    let web_ui_features = FeatureSet::from_features([Feature::WebUi]);
    let surfaces = [
        NetworkServiceSurface::PrusaLinkWui,
        NetworkServiceSurface::Sntp,
        NetworkServiceSurface::Mdns,
        NetworkServiceSurface::Dns,
        NetworkServiceSurface::Metrics,
        NetworkServiceSurface::Syslog,
    ];

    // Act
    let missing_feature_results =
        surfaces.map(|surface| NetworkServiceContract::new(surface, FeatureSet::empty()));
    let enabled_results =
        surfaces.map(|surface| NetworkServiceContract::new(surface, web_ui_features.clone()));

    // Assert
    assert!(
        missing_feature_results
            .iter()
            .all(|result| *result == Err(InvariantError::UnsupportedNetworkService))
    );
    assert!(
        enabled_results
            .iter()
            .all(|result| matches!(result, Ok(contract) if surfaces.contains(&contract.surface())))
    );
}

#[test]
fn exposes_planned_network_contract_surfaces() {
    // Arrange
    let _connect_identity = ConnectIdentity::TokenConfigKey;
    let _connect_command_state = ConnectCommandState::Pending;
    let _telemetry_surface = TelemetryEventSurface::Telemetry;
    let _websocket_state = WebSocketCommandState::Accepted;
    let _endpoint_family = WuiEndpointFamily::PrusaLinkApiV1;
    let _transfer_source = TransferSource::ConnectCommand;
    let _transfer_slot_state = TransferSlotState::Idle;
    let _transfer_recovery_state = TransferRecoveryState::NotNeeded;
    let _transfer_error_class = TransferErrorClass::Storage;
    let _service_input = NetworkServiceContractInput {
        surface: NetworkServiceSurface::PrusaConnect,
        features: FeatureSet::from_features([Feature::Connect]),
    };

    // Act
    let proof_scope = NetworkProofScope::parse("non-local");

    // Assert
    assert_eq!(proof_scope, Ok(NetworkProofScope::NonLocal));
}
