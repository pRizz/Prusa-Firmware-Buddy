#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fixture_id_accepts_named_fixture_and_rejects_empty_or_path_like_values() {
        // Arrange
        let valid_fixture = "print-file-start-preview-stream-recovery";
        let invalid_fixtures = ["", "   ", "fixtures/print", r"fixtures\print"];

        // Act
        let valid_result = FixtureId::new(valid_fixture);
        let invalid_results = invalid_fixtures.map(FixtureId::new);

        // Assert
        assert!(valid_result.is_ok());
        assert!(invalid_results.iter().all(Result::is_err));
    }

    #[test]
    fn file_print_start_requires_preview_confirmation_before_printing() {
        // Arrange
        let fixture =
            FixtureId::new("print-file-start-preview-stream-recovery").expect("valid fixture id");

        // Act
        let preview_state =
            transition_print_state(PrintJobState::Idle, PrintCommand::StartFile(fixture))
                .expect("file print should enter preview");
        let printing_state = transition_print_state(preview_state, PrintCommand::ConfirmPreview)
            .expect("confirmed preview should start file printing");

        // Assert
        assert_eq!(printing_state, PrintJobState::Printing(PrintSource::File));
    }

    #[test]
    fn serial_print_start_enters_printing_without_preview() {
        // Arrange
        let state = PrintJobState::Idle;

        // Act
        let result = transition_print_state(state, PrintCommand::StartSerial);

        // Assert
        assert_eq!(result, Ok(PrintJobState::Printing(PrintSource::Serial)));
    }

    #[test]
    fn pause_resume_and_cancel_reject_unsupported_transitions() {
        // Arrange
        let printing = PrintJobState::Printing(PrintSource::File);
        let idle = PrintJobState::Idle;

        // Act
        let pausing = transition_print_state(printing, PrintCommand::Pause)
            .expect("printing state should start pausing");
        let paused = transition_print_state(pausing, PrintCommand::PauseComplete)
            .expect("pausing state should become paused");
        let resuming = transition_print_state(paused.clone(), PrintCommand::Resume)
            .expect("paused state should start resuming");
        let resumed = transition_print_state(resuming, PrintCommand::PlannerReady)
            .expect("planner-ready state should resume printing");
        let cancelling = transition_print_state(resumed, PrintCommand::Cancel)
            .expect("printing state should begin cancellation");
        let cancelled = transition_print_state(cancelling, PrintCommand::CancelComplete)
            .expect("cancelling state should return idle");
        let invalid_pause = transition_print_state(idle.clone(), PrintCommand::Pause);
        let invalid_resume = transition_print_state(idle.clone(), PrintCommand::Resume);
        let invalid_cancel = transition_print_state(idle, PrintCommand::Cancel);

        // Assert
        assert_eq!(cancelled, PrintJobState::Idle);
        assert!(matches!(
            invalid_pause,
            Err(PrintTransitionError::UnsupportedTransition { .. })
        ));
        assert!(matches!(
            invalid_resume,
            Err(PrintTransitionError::UnsupportedTransition { .. })
        ));
        assert!(matches!(
            invalid_cancel,
            Err(PrintTransitionError::UnsupportedTransition { .. })
        ));
    }

    #[test]
    fn gcode_mnemonics_route_to_buddy_handlers_or_marlin_queue() {
        // Arrange
        let buddy_mnemonics = [
            "M862.1", "M862.2", "M862.3", "M862.4", "M862.5", "M862.6", "M600", "M0",
        ];
        let marlin_mnemonics = ["G0", "G1", "M104", "M109", "M140", "M190"];

        // Act
        let buddy_routes = buddy_mnemonics.map(|raw| {
            let mnemonic = GcodeMnemonic::new(raw).expect("valid Buddy mnemonic");
            route_gcode_mnemonic(&mnemonic)
        });
        let marlin_routes = marlin_mnemonics.map(|raw| {
            let mnemonic = GcodeMnemonic::new(raw).expect("valid Marlin mnemonic");
            route_gcode_mnemonic(&mnemonic)
        });

        // Assert
        assert!(
            buddy_routes
                .iter()
                .all(|route| *route == CommandRoute::BuddyGcodeHandler)
        );
        assert!(
            marlin_routes
                .iter()
                .all(|route| *route == CommandRoute::MarlinQueue)
        );
    }
}
