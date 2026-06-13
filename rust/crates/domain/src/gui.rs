#[cfg(test)]
mod tests {
    use super::*;
    use crate::InvariantError;

    const DISPLAY_CLASSES: &[DisplayClass] =
        &[DisplayClass::Mini240x320, DisplayClass::Large480x320];

    fn valid_row_id() -> GuiParityRowId {
        GuiParityRowId::parse("screen-stack-home-bootstrap").expect("valid GUI parity row ID")
    }

    #[test]
    fn parses_mini_display_class() {
        // Arrange
        let raw_display_class = "240x320";

        // Act
        let result = DisplayClass::parse(raw_display_class);

        // Assert
        assert_eq!(result, Ok(DisplayClass::Mini240x320));
        let display_class = result.expect("display class should parse");
        assert_eq!(display_class.width(), 240);
        assert_eq!(display_class.height(), 320);
        assert_eq!(display_class.as_str(), raw_display_class);
    }

    #[test]
    fn parses_large_display_class() {
        // Arrange
        let raw_display_class = "480x320";

        // Act
        let result = DisplayClass::parse(raw_display_class);

        // Assert
        assert_eq!(result, Ok(DisplayClass::Large480x320));
        let display_class = result.expect("display class should parse");
        assert_eq!(display_class.width(), 480);
        assert_eq!(display_class.height(), 320);
        assert_eq!(display_class.as_str(), raw_display_class);
    }

    #[test]
    fn classifies_gui_evidence_locality() {
        // Arrange
        let local_evidence = "manifest-check";
        let non_local_evidence = "simulator-flow";

        // Act
        let local_result = GuiEvidenceClass::parse(local_evidence);
        let non_local_result = GuiEvidenceClass::parse(non_local_evidence);

        // Assert
        assert!(matches!(
            local_result,
            Ok(evidence_class) if evidence_class.is_local_proof()
        ));
        assert!(matches!(
            non_local_result,
            Ok(evidence_class) if !evidence_class.is_local_proof()
        ));
    }

    #[test]
    fn validates_gui_parity_row_id() {
        // Arrange
        let valid_id = "screen-stack-home-bootstrap";
        let invalid_ids = ["", "../screen-stack", "screen\nstack"];

        // Act
        let valid_result = GuiParityRowId::parse(valid_id);
        let invalid_results = invalid_ids.map(GuiParityRowId::parse);

        // Assert
        assert!(matches!(
            valid_result,
            Ok(row_id) if row_id.as_str() == valid_id
        ));
        assert_eq!(invalid_results[0], Err(InvariantError::EmptyGuiParityRowId));
        assert!(invalid_results[1..].iter().all(Result::is_err));
    }

    #[test]
    fn parses_gui_semantic_action_manifest_ids() {
        // Arrange
        let action_ids = ["pause", "resume", "cancel", "stop", "reprint", "preview"];

        // Act
        let actions = action_ids.map(GuiSemanticAction::parse);

        // Assert
        assert_eq!(
            actions,
            [
                Ok(GuiSemanticAction::Pause),
                Ok(GuiSemanticAction::Resume),
                Ok(GuiSemanticAction::Cancel),
                Ok(GuiSemanticAction::Stop),
                Ok(GuiSemanticAction::Reprint),
                Ok(GuiSemanticAction::Preview),
            ]
        );
    }

    #[test]
    fn rejects_non_local_evidence_as_local_proof() {
        // Arrange
        let non_local_evidence_classes = [
            GuiEvidenceClass::HardwareSmoke,
            GuiEvidenceClass::SimulatorFlow,
            GuiEvidenceClass::ManualHardwareRequired,
        ];

        // Act
        let results = non_local_evidence_classes.map(|evidence_class| {
            GuiParityContract::new(
                valid_row_id(),
                GuiWorkflow::ScreenStack,
                GuiSurface::ScreenStack,
                DISPLAY_CLASSES,
                evidence_class,
                GuiProofScope::Local,
                None,
                IntentionalDeltaStatus::None,
                None,
            )
        });

        // Assert
        assert!(
            results
                .iter()
                .all(|result| *result == Err(InvariantError::InvalidGuiProofScope))
        );
    }

    #[test]
    fn accepts_preview_semantic_action_for_print_preview() {
        // Arrange
        let maybe_semantic_action = Some(GuiSemanticAction::Preview);

        // Act
        let result = GuiParityContract::new(
            valid_row_id(),
            GuiWorkflow::PrintPreview,
            GuiSurface::PrintControl,
            DISPLAY_CLASSES,
            GuiEvidenceClass::RustHostTest,
            GuiProofScope::Local,
            Some(LocalizationSurface::PrintPreviewText),
            IntentionalDeltaStatus::None,
            maybe_semantic_action,
        );

        // Assert
        assert!(matches!(
            result,
            Ok(contract) if contract.semantic_action() == maybe_semantic_action
                && contract.workflow() == GuiWorkflow::PrintPreview
        ));
    }

    #[test]
    fn rejects_semantic_actions_for_wrong_workflow() {
        // Arrange
        let print_control_actions = [
            GuiSemanticAction::Pause,
            GuiSemanticAction::Resume,
            GuiSemanticAction::Cancel,
            GuiSemanticAction::Stop,
            GuiSemanticAction::Reprint,
        ];

        // Act
        let print_control_results = print_control_actions.map(|semantic_action| {
            GuiParityContract::new(
                valid_row_id(),
                GuiWorkflow::PrintPreview,
                GuiSurface::PrintControl,
                DISPLAY_CLASSES,
                GuiEvidenceClass::RustHostTest,
                GuiProofScope::Local,
                None,
                IntentionalDeltaStatus::None,
                Some(semantic_action),
            )
        });
        let preview_result = GuiParityContract::new(
            valid_row_id(),
            GuiWorkflow::PrintControl,
            GuiSurface::PrintControl,
            DISPLAY_CLASSES,
            GuiEvidenceClass::RustHostTest,
            GuiProofScope::Local,
            None,
            IntentionalDeltaStatus::None,
            Some(GuiSemanticAction::Preview),
        );

        // Assert
        assert!(
            print_control_results
                .iter()
                .all(|result| *result == Err(InvariantError::InvalidGuiSemanticActionBinding))
        );
        assert_eq!(
            preview_result,
            Err(InvariantError::InvalidGuiSemanticActionBinding)
        );
    }
}
