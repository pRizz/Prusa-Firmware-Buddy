use crate::InvariantError;

/// Supported GUI display class recorded by Phase 8 parity rows.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum DisplayClass {
    /// MINI-class 240x320 display.
    Mini240x320,
    /// Large 480x320 display.
    Large480x320,
    /// Test-only mock display from the retained GUI configuration.
    MockTestOnly,
}

impl DisplayClass {
    /// Parses the display-class value used by GUI parity manifests.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "240x320" => Ok(Self::Mini240x320),
            "480x320" => Ok(Self::Large480x320),
            "mock" => Ok(Self::MockTestOnly),
            _ => Err(InvariantError::InvalidDisplayClass),
        }
    }

    /// Returns the manifest string for this display class.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Mini240x320 => "240x320",
            Self::Large480x320 => "480x320",
            Self::MockTestOnly => "mock",
        }
    }

    /// Returns the display width in pixels.
    pub fn width(self) -> u16 {
        match self {
            Self::Mini240x320 | Self::MockTestOnly => 240,
            Self::Large480x320 => 480,
        }
    }

    /// Returns the display height in pixels.
    pub fn height(self) -> u16 {
        320
    }

    /// Returns whether this display class can prove physical LCD behavior.
    pub fn is_physical_display_proof(self) -> bool {
        !matches!(self, Self::MockTestOnly)
    }
}

/// Phase 8 GUI workflow identity.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum GuiWorkflow {
    /// Screen stack bootstrap, home, and navigation flow.
    ScreenStack,
    /// Dialog finite-state-machine display flow.
    DialogFsm,
    /// Menu and settings workflow.
    MenuWorkflow,
    /// Print preview workflow.
    PrintPreview,
    /// Print pause, resume, cancel, stop, and reprint controls.
    PrintControl,
    /// Setup, selftest, and calibration workflows.
    SetupSelftestCalibration,
    /// Connect registration entry workflow.
    ConnectRegistrationEntry,
    /// PrusaLink credential display workflow.
    PrusaLinkCredentialDisplay,
    /// Warning, redscreen, and error workflow.
    WarningRedscreenError,
    /// Localization and layout workflow.
    LocalizationLayout,
}

impl GuiWorkflow {
    /// Parses the GUI workflow value used by Phase 8 manifests.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "screen-stack" => Ok(Self::ScreenStack),
            "dialog-fsm" => Ok(Self::DialogFsm),
            "menu-workflow" => Ok(Self::MenuWorkflow),
            "print-preview" => Ok(Self::PrintPreview),
            "print-control" => Ok(Self::PrintControl),
            "setup-selftest-calibration" => Ok(Self::SetupSelftestCalibration),
            "connect-registration-entry" => Ok(Self::ConnectRegistrationEntry),
            "prusa-link-credential-display" => Ok(Self::PrusaLinkCredentialDisplay),
            "warning-redscreen-error" => Ok(Self::WarningRedscreenError),
            "localization-layout" => Ok(Self::LocalizationLayout),
            _ => Err(InvariantError::InvalidGuiWorkflow),
        }
    }

    /// Returns the manifest string for this workflow.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::ScreenStack => "screen-stack",
            Self::DialogFsm => "dialog-fsm",
            Self::MenuWorkflow => "menu-workflow",
            Self::PrintPreview => "print-preview",
            Self::PrintControl => "print-control",
            Self::SetupSelftestCalibration => "setup-selftest-calibration",
            Self::ConnectRegistrationEntry => "connect-registration-entry",
            Self::PrusaLinkCredentialDisplay => "prusa-link-credential-display",
            Self::WarningRedscreenError => "warning-redscreen-error",
            Self::LocalizationLayout => "localization-layout",
        }
    }
}

/// Local GUI surface named by a Phase 8 parity row.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum GuiSurface {
    /// Screen stack surface.
    ScreenStack,
    /// Dialog surface.
    Dialog,
    /// Menu surface.
    Menu,
    /// Wizard surface.
    Wizard,
    /// Print control surface.
    PrintControl,
    /// Localization surface.
    Localization,
    /// Error and warning surface.
    ErrorWarning,
    /// Connect entry surface.
    ConnectEntry,
}

impl GuiSurface {
    /// Returns the manifest string for this GUI surface.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::ScreenStack => "screen-stack",
            Self::Dialog => "dialog",
            Self::Menu => "menu",
            Self::Wizard => "wizard",
            Self::PrintControl => "print-control",
            Self::Localization => "localization",
            Self::ErrorWarning => "error-warning",
            Self::ConnectEntry => "connect-entry",
        }
    }
}

/// Evidence class for a Phase 8 GUI parity claim.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum GuiEvidenceClass {
    /// Manifest structure and source paths are checked locally.
    ManifestCheck,
    /// Source audit against retained GUI paths.
    SourceAudit,
    /// Static source audit against retained GUI boundary paths.
    StaticSourceAudit,
    /// Host test evidence in the retained or mixed codebase.
    HostTest,
    /// Rust host test evidence for pure Rust GUI classification.
    RustHostTest,
    /// Simulator evidence is required for runtime display flow behavior.
    SimulatorFlow,
    /// Hardware smoke evidence is required.
    HardwareSmoke,
    /// Manual hardware or failure-injection evidence is required.
    ManualHardwareRequired,
}

impl GuiEvidenceClass {
    /// Parses a Phase 8 GUI evidence class string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "manifest-check" => Ok(Self::ManifestCheck),
            "source-audit" => Ok(Self::SourceAudit),
            "static-source-audit" => Ok(Self::StaticSourceAudit),
            "host-test" => Ok(Self::HostTest),
            "rust-host-test" => Ok(Self::RustHostTest),
            "simulator-flow" => Ok(Self::SimulatorFlow),
            "hardware-smoke" => Ok(Self::HardwareSmoke),
            "manual-hardware-required" => Ok(Self::ManualHardwareRequired),
            _ => Err(InvariantError::InvalidGuiEvidenceClass),
        }
    }

    /// Returns the manifest string for this evidence class.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::ManifestCheck => "manifest-check",
            Self::SourceAudit => "source-audit",
            Self::StaticSourceAudit => "static-source-audit",
            Self::HostTest => "host-test",
            Self::RustHostTest => "rust-host-test",
            Self::SimulatorFlow => "simulator-flow",
            Self::HardwareSmoke => "hardware-smoke",
            Self::ManualHardwareRequired => "manual-hardware-required",
        }
    }

    /// Returns whether this evidence class can support a local proof scope.
    pub fn is_local_proof(self) -> bool {
        matches!(
            self,
            Self::ManifestCheck
                | Self::SourceAudit
                | Self::StaticSourceAudit
                | Self::HostTest
                | Self::RustHostTest
        )
    }
}

/// Locality scope for Phase 8 proof.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum GuiProofScope {
    /// Locally provable by manifest, source, host, or Rust checks.
    Local,
    /// Requires simulator, hardware, or manual evidence outside local checks.
    NonLocal,
}

impl GuiProofScope {
    /// Parses a Phase 8 proof-scope string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "local" => Ok(Self::Local),
            "non-local" => Ok(Self::NonLocal),
            _ => Err(InvariantError::InvalidGuiProofScope),
        }
    }

    /// Returns the manifest string for this proof scope.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Local => "local",
            Self::NonLocal => "non-local",
        }
    }
}

/// Phase 8 parity row identity parsed before adapter code consumes it.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct GuiParityRowId(String);

impl GuiParityRowId {
    /// Parses a GUI parity row ID while rejecting path-like or non-printable
    /// values.
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if raw.is_empty() {
            return Err(InvariantError::EmptyGuiParityRowId);
        }

        if raw.len() > 96
            || raw == "."
            || raw == ".."
            || raw.contains('/')
            || raw.contains('\\')
            || raw.bytes().any(|byte| byte.is_ascii_control())
            || !raw
                .bytes()
                .all(|byte| byte.is_ascii_lowercase() || byte.is_ascii_digit() || byte == b'-')
        {
            return Err(InvariantError::InvalidGuiParityRowId);
        }

        Ok(Self(raw))
    }

    /// Returns the validated row ID as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Localization and text layout surface covered by Phase 8.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum LocalizationSurface {
    /// Localized text capacity.
    TextCapacity,
    /// Font resource visibility.
    FontResource,
    /// Truncation behavior.
    Truncation,
    /// Print preview text.
    PrintPreviewText,
    /// Progress text.
    ProgressText,
    /// Warning and error text.
    WarningErrorText,
}

impl LocalizationSurface {
    /// Returns the manifest string for this localization surface.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::TextCapacity => "text-capacity",
            Self::FontResource => "font-resource",
            Self::Truncation => "truncation",
            Self::PrintPreviewText => "print-preview-text",
            Self::ProgressText => "progress-text",
            Self::WarningErrorText => "warning-error-text",
        }
    }
}

/// Intentional-delta status for a Phase 8 GUI parity row.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum IntentionalDeltaStatus {
    /// No intentional delta is recorded.
    None,
    /// Intentional delta is approved and evidenced.
    Approved,
    /// Intentional delta is blocked.
    Blocked,
}

impl IntentionalDeltaStatus {
    /// Parses a Phase 8 intentional-delta status string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "none" => Ok(Self::None),
            "approved" => Ok(Self::Approved),
            "blocked" => Ok(Self::Blocked),
            _ => Err(InvariantError::InvalidIntentionalDeltaStatus),
        }
    }

    /// Returns the manifest string for this intentional-delta status.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::None => "none",
            Self::Approved => "approved",
            Self::Blocked => "blocked",
        }
    }
}

/// Source-backed semantic action identity for GUI print controls.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum GuiSemanticAction {
    /// Pause print action.
    Pause,
    /// Resume print action.
    Resume,
    /// Cancel print action.
    Cancel,
    /// Stop print action.
    Stop,
    /// Reprint action.
    Reprint,
    /// Print preview action.
    Preview,
}

impl GuiSemanticAction {
    /// Parses an exact semantic action manifest ID.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "pause" => Ok(Self::Pause),
            "resume" => Ok(Self::Resume),
            "cancel" => Ok(Self::Cancel),
            "stop" => Ok(Self::Stop),
            "reprint" => Ok(Self::Reprint),
            "preview" => Ok(Self::Preview),
            _ => Err(InvariantError::InvalidGuiSemanticAction),
        }
    }

    /// Returns the exact semantic action manifest ID.
    pub fn as_manifest_id(self) -> &'static str {
        match self {
            Self::Pause => "pause",
            Self::Resume => "resume",
            Self::Cancel => "cancel",
            Self::Stop => "stop",
            Self::Reprint => "reprint",
            Self::Preview => "preview",
        }
    }

    /// Returns the only workflow that may bind this semantic action.
    pub fn expected_workflow(self) -> GuiWorkflow {
        match self {
            Self::Preview => GuiWorkflow::PrintPreview,
            Self::Pause | Self::Resume | Self::Cancel | Self::Stop | Self::Reprint => {
                GuiWorkflow::PrintControl
            }
        }
    }
}

/// Validated Phase 8 GUI parity row contract.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GuiParityContract {
    row_id: GuiParityRowId,
    workflow: GuiWorkflow,
    surface: GuiSurface,
    display_classes: &'static [DisplayClass],
    evidence_class: GuiEvidenceClass,
    proof_scope: GuiProofScope,
    maybe_localization_surface: Option<LocalizationSurface>,
    intentional_delta_status: IntentionalDeltaStatus,
    maybe_semantic_action: Option<GuiSemanticAction>,
}

/// Raw validated inputs for building a [`GuiParityContract`].
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GuiParityContractInput {
    /// GUI parity row ID.
    pub row_id: GuiParityRowId,
    /// GUI workflow.
    pub workflow: GuiWorkflow,
    /// GUI surface.
    pub surface: GuiSurface,
    /// Display classes covered by the parity row.
    pub display_classes: &'static [DisplayClass],
    /// Evidence class.
    pub evidence_class: GuiEvidenceClass,
    /// Proof scope.
    pub proof_scope: GuiProofScope,
    /// Localization surface, when this is a localization row.
    pub maybe_localization_surface: Option<LocalizationSurface>,
    /// Intentional-delta status.
    pub intentional_delta_status: IntentionalDeltaStatus,
    /// Semantic action, when this row describes a source-backed GUI action.
    pub maybe_semantic_action: Option<GuiSemanticAction>,
}

impl GuiParityContract {
    /// Creates a GUI parity contract only when evidence/proof and semantic
    /// action bindings are internally consistent.
    pub fn new(input: GuiParityContractInput) -> Result<Self, InvariantError> {
        let GuiParityContractInput {
            row_id,
            workflow,
            surface,
            display_classes,
            evidence_class,
            proof_scope,
            maybe_localization_surface,
            intentional_delta_status,
            maybe_semantic_action,
        } = input;

        if display_classes.is_empty() {
            return Err(InvariantError::InvalidDisplayClass);
        }

        if matches!(proof_scope, GuiProofScope::Local) && !evidence_class.is_local_proof() {
            return Err(InvariantError::InvalidGuiProofScope);
        }

        if maybe_semantic_action
            .is_some_and(|semantic_action| semantic_action.expected_workflow() != workflow)
        {
            return Err(InvariantError::InvalidGuiSemanticActionBinding);
        }

        Ok(Self {
            row_id,
            workflow,
            surface,
            display_classes,
            evidence_class,
            proof_scope,
            maybe_localization_surface,
            intentional_delta_status,
            maybe_semantic_action,
        })
    }

    /// Returns the GUI workflow.
    pub fn workflow(&self) -> GuiWorkflow {
        self.workflow
    }

    /// Returns the GUI surface.
    pub fn surface(&self) -> GuiSurface {
        self.surface
    }

    /// Returns the display classes covered by this contract.
    pub fn display_classes(&self) -> &'static [DisplayClass] {
        self.display_classes
    }

    /// Returns the evidence class.
    pub fn evidence_class(&self) -> GuiEvidenceClass {
        self.evidence_class
    }

    /// Returns the proof scope.
    pub fn proof_scope(&self) -> GuiProofScope {
        self.proof_scope
    }

    /// Returns the row ID.
    pub fn row_id(&self) -> &GuiParityRowId {
        &self.row_id
    }

    /// Returns the localization surface, when this is a localization row.
    pub fn localization_surface(&self) -> Option<LocalizationSurface> {
        self.maybe_localization_surface
    }

    /// Returns the intentional-delta status.
    pub fn intentional_delta_status(&self) -> IntentionalDeltaStatus {
        self.intentional_delta_status
    }

    /// Returns the optional semantic GUI action.
    pub fn semantic_action(&self) -> Option<GuiSemanticAction> {
        self.maybe_semantic_action
    }
}

#[cfg(test)]
mod tests;
