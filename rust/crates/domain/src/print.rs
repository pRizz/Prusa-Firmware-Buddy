use core::fmt;

/// Source family for an active print.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum PrintSource {
    /// File-backed print that uses preview, media prefetch, and recovery data.
    File,
    /// Serial-host print that uses host action hooks and no file preview.
    Serial,
}

/// Valid Phase 6 fixture identity for a retained print behavior contract.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct FixtureId(String);

impl FixtureId {
    /// Parses a fixture identity before policy code consumes it.
    pub fn new(raw: impl AsRef<str>) -> Result<Self, PrintTransitionError> {
        let value = raw.as_ref().trim();
        if value.is_empty() || value.contains('/') || value.contains('\\') {
            return Err(PrintTransitionError::InvalidFixtureId);
        }

        Ok(Self(value.to_owned()))
    }

    /// Returns the validated fixture identity.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Typed Rust print state surface for retained Marlin/Buddy behavior contracts.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PrintJobState {
    /// No active print.
    Idle,
    /// File print is waiting for preview confirmation.
    Previewing(PrintSource),
    /// Planner-visible print is active.
    Printing(PrintSource),
    /// Pause was requested and the retained planner is draining or parking.
    Pausing(PrintSource),
    /// Print is paused and can resume or cancel.
    Paused(PrintSource),
    /// Resume was requested and the retained planner is buffering or reheating.
    Resuming(PrintSource),
    /// Cancel was requested and retained cleanup is in progress.
    Cancelling(PrintSource),
    /// Retained print finished successfully.
    Finished,
    /// Power panic recovery is waiting for an explicit resume.
    PowerPanicAwaitingResume(PrintSource),
    /// File print hit a recoverable media error and needs retry/recovery.
    MediaErrorAwaitingRecovery,
}

/// Commands that drive pure print-state policy transitions.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PrintCommand {
    /// Start a file-backed print from a retained fixture.
    StartFile(FixtureId),
    /// Confirm preview and enter actual printing.
    ConfirmPreview,
    /// Start a serial-host print.
    StartSerial,
    /// Request pause.
    Pause,
    /// Retained pause sequence reached parked/paused state.
    PauseComplete,
    /// Request resume.
    Resume,
    /// Retained planner is ready after resume buffering/reheating.
    PlannerReady,
    /// Request cancellation.
    Cancel,
    /// Retained cancellation cleanup completed.
    CancelComplete,
    /// Retained print reached end-of-file or equivalent completion.
    Finish,
    /// Enter power panic recovery.
    EnterPowerPanic,
    /// Resume from power panic.
    RecoverPowerPanic,
    /// Enter recoverable media-error recovery.
    EnterMediaError,
    /// Retry media recovery.
    RecoverMediaError,
}

/// Planner-visible print flow class for retained source contracts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum PlannerFlowState {
    /// No retained planner print flow is active.
    NoActivePrint,
    /// File print is waiting for preview/GUI confirmation.
    WaitingForPreview,
    /// Planner-visible print work is active.
    PlannerActive,
    /// Planner-visible print is paused.
    PlannerPaused,
    /// Planner-visible cancellation cleanup is active.
    PlannerCancelling,
    /// Power-panic or media recovery is required before planner flow continues.
    RecoveryRequired,
}

impl From<&PrintJobState> for PlannerFlowState {
    fn from(state: &PrintJobState) -> Self {
        match state {
            PrintJobState::Idle | PrintJobState::Finished => Self::NoActivePrint,
            PrintJobState::Previewing(_) => Self::WaitingForPreview,
            PrintJobState::Printing(_) | PrintJobState::Pausing(_) | PrintJobState::Resuming(_) => {
                Self::PlannerActive
            }
            PrintJobState::Paused(_) => Self::PlannerPaused,
            PrintJobState::Cancelling(_) => Self::PlannerCancelling,
            PrintJobState::PowerPanicAwaitingResume(_)
            | PrintJobState::MediaErrorAwaitingRecovery => Self::RecoveryRequired,
        }
    }
}

/// Command-route class for a parsed G-code mnemonic.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum CommandRoute {
    /// Buddy-specific handler selected by retained Prusa G-code dispatch.
    BuddyGcodeHandler,
    /// Retained Marlin queue handles the command.
    MarlinQueue,
    /// Command is outside the current Phase 6 local routing contract.
    Unknown,
}

/// Uppercase G-code mnemonic parsed at the Rust policy boundary.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct GcodeMnemonic(String);

impl GcodeMnemonic {
    /// Parses a raw command mnemonic and normalizes it to uppercase ASCII.
    pub fn new(raw: impl AsRef<str>) -> Result<Self, PrintTransitionError> {
        let value = raw.as_ref().trim();
        if value.is_empty() {
            return Err(PrintTransitionError::InvalidGcodeMnemonic);
        }

        Ok(Self(value.to_ascii_uppercase()))
    }

    /// Returns the normalized mnemonic.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Error returned when a print policy input or transition is unsupported.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PrintTransitionError {
    /// Fixture identity was empty, whitespace-only, or path-like.
    InvalidFixtureId,
    /// G-code mnemonic was empty after trimming.
    InvalidGcodeMnemonic,
    /// The command is impossible from the current typed state.
    UnsupportedTransition {
        /// State before the rejected transition.
        state: PrintJobState,
        /// Command that was rejected.
        command: PrintCommand,
    },
}

impl fmt::Display for PrintTransitionError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidFixtureId => {
                formatter.write_str("fixture id must be non-empty and not path-like")
            }
            Self::InvalidGcodeMnemonic => formatter.write_str("g-code mnemonic must not be empty"),
            Self::UnsupportedTransition { state, command } => {
                write!(
                    formatter,
                    "unsupported print transition: {state:?} + {command:?}"
                )
            }
        }
    }
}

impl std::error::Error for PrintTransitionError {}

/// Applies a pure print-state transition without calling retained C/C++ code.
pub fn transition_print_state(
    state: PrintJobState,
    command: PrintCommand,
) -> Result<PrintJobState, PrintTransitionError> {
    match (state, command) {
        (PrintJobState::Idle, PrintCommand::StartFile(_)) => {
            Ok(PrintJobState::Previewing(PrintSource::File))
        }
        (PrintJobState::Idle, PrintCommand::StartSerial) => {
            Ok(PrintJobState::Printing(PrintSource::Serial))
        }
        (PrintJobState::Previewing(PrintSource::File), PrintCommand::ConfirmPreview) => {
            Ok(PrintJobState::Printing(PrintSource::File))
        }
        (PrintJobState::Printing(source), PrintCommand::Pause) => {
            Ok(PrintJobState::Pausing(source))
        }
        (PrintJobState::Pausing(source), PrintCommand::PauseComplete) => {
            Ok(PrintJobState::Paused(source))
        }
        (PrintJobState::Paused(source), PrintCommand::Resume) => {
            Ok(PrintJobState::Resuming(source))
        }
        (PrintJobState::Resuming(source), PrintCommand::PlannerReady) => {
            Ok(PrintJobState::Printing(source))
        }
        (PrintJobState::Printing(_), PrintCommand::Finish) => Ok(PrintJobState::Finished),
        (PrintJobState::Printing(source), PrintCommand::EnterPowerPanic) => {
            Ok(PrintJobState::PowerPanicAwaitingResume(source))
        }
        (PrintJobState::PowerPanicAwaitingResume(source), PrintCommand::RecoverPowerPanic) => {
            Ok(PrintJobState::Resuming(source))
        }
        (PrintJobState::Printing(PrintSource::File), PrintCommand::EnterMediaError) => {
            Ok(PrintJobState::MediaErrorAwaitingRecovery)
        }
        (PrintJobState::MediaErrorAwaitingRecovery, PrintCommand::RecoverMediaError) => {
            Ok(PrintJobState::Resuming(PrintSource::File))
        }
        (state, PrintCommand::Cancel) => match cancel_source(&state) {
            Some(source) => Ok(PrintJobState::Cancelling(source)),
            None => Err(PrintTransitionError::UnsupportedTransition {
                state,
                command: PrintCommand::Cancel,
            }),
        },
        (PrintJobState::Cancelling(_), PrintCommand::CancelComplete) => Ok(PrintJobState::Idle),
        (state, command) => Err(PrintTransitionError::UnsupportedTransition { state, command }),
    }
}

fn cancel_source(state: &PrintJobState) -> Option<PrintSource> {
    match state {
        PrintJobState::Previewing(source)
        | PrintJobState::Printing(source)
        | PrintJobState::Pausing(source)
        | PrintJobState::Paused(source)
        | PrintJobState::Resuming(source)
        | PrintJobState::PowerPanicAwaitingResume(source) => Some(*source),
        PrintJobState::MediaErrorAwaitingRecovery => Some(PrintSource::File),
        PrintJobState::Idle | PrintJobState::Cancelling(_) | PrintJobState::Finished => None,
    }
}

/// Classifies a parsed G-code mnemonic against retained routing contracts.
pub fn route_gcode_mnemonic(mnemonic: &GcodeMnemonic) -> CommandRoute {
    let mnemonic = mnemonic.as_str();
    if is_retained_buddy_gcode_handler(mnemonic) {
        return CommandRoute::BuddyGcodeHandler;
    }

    if is_common_marlin_queue_mnemonic(mnemonic) {
        return CommandRoute::MarlinQueue;
    }

    CommandRoute::Unknown
}

fn is_retained_buddy_gcode_handler(mnemonic: &str) -> bool {
    matches!(
        mnemonic,
        "G12"
            | "G26"
            | "G64"
            | "G123"
            | "G162"
            | "G163"
            | "M0"
            | "M104.1"
            | "M123"
            | "M141"
            | "M147"
            | "M148"
            | "M150"
            | "M151"
            | "M191"
            | "M262"
            | "M263"
            | "M264"
            | "M265"
            | "M267"
            | "M268"
            | "M300"
            | "M331"
            | "M332"
            | "M333"
            | "M334"
            | "M340"
            | "M591"
            | "M600"
            | "M704"
            | "M705"
            | "M706"
            | "M707"
            | "M708"
            | "M709"
            | "M862.1"
            | "M862.2"
            | "M862.3"
            | "M862.4"
            | "M862.5"
            | "M862.6"
            | "M863"
            | "M864"
            | "M865"
            | "M870"
            | "M919"
            | "M920"
            | "M960"
            | "M961"
            | "M997"
            | "M999"
            | "M1200"
            | "M1600"
            | "M1601"
            | "M1700"
            | "M1701"
            | "M1702"
            | "M1703"
            | "M1704"
            | "M1959"
            | "M1977"
            | "M1978"
            | "M1979"
            | "M1980"
            | "M9140"
            | "M9141"
            | "M9150"
            | "M9200"
            | "M9201"
            | "M9202"
            | "M9933"
            | "P0"
    )
}

fn is_common_marlin_queue_mnemonic(mnemonic: &str) -> bool {
    matches!(mnemonic, "G0" | "G1" | "M104" | "M109" | "M140" | "M190")
}

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
            "G12", "G26", "G64", "G123", "G162", "G163", "M0", "M104.1", "M123", "M141", "M147",
            "M148", "M150", "M151", "M191", "M262", "M263", "M264", "M265", "M267", "M268", "M300",
            "M331", "M332", "M333", "M334", "M340", "M591", "M600", "M704", "M705", "M706", "M707",
            "M708", "M709", "M862.1", "M862.2", "M862.3", "M862.4", "M862.5", "M862.6", "M863",
            "M864", "M865", "M870", "M919", "M920", "M960", "M961", "M997", "M999", "M1200",
            "M1600", "M1601", "M1700", "M1701", "M1702", "M1703", "M1704", "M1959", "M1977",
            "M1978", "M1979", "M1980", "M9140", "M9141", "M9150", "M9200", "M9201", "M9202",
            "M9933", "P0",
        ];
        let marlin_mnemonics = ["G0", "G1", "M104", "M109", "M140", "M190"];
        let unknown_mnemonic = GcodeMnemonic::new("M42").expect("valid unknown mnemonic");

        // Act
        let buddy_routes = buddy_mnemonics.map(|raw| {
            let mnemonic = GcodeMnemonic::new(raw).expect("valid Buddy mnemonic");
            route_gcode_mnemonic(&mnemonic)
        });
        let marlin_routes = marlin_mnemonics.map(|raw| {
            let mnemonic = GcodeMnemonic::new(raw).expect("valid Marlin mnemonic");
            route_gcode_mnemonic(&mnemonic)
        });
        let unknown_route = route_gcode_mnemonic(&unknown_mnemonic);

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
        assert_eq!(unknown_route, CommandRoute::Unknown);
    }
}
