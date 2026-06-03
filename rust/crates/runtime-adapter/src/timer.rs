use crate::EvidenceClass;

const TIMER_SOURCE_EVIDENCE: &[&str] = &["src/freertos/system_tasks.cpp"];
const TIMER_EVIDENCE: &[EvidenceClass] = &[
    EvidenceClass::StaticSourceAudit,
    EvidenceClass::RustHostTest,
    EvidenceClass::SimulatorFlow,
    EvidenceClass::HardwareSmoke,
    EvidenceClass::ManualHardwareRequired,
];

/// Error returned when timer task memory cannot represent a valid contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TimerTaskMemoryError {
    /// FreeRTOS timer task stack depth must not be zero when timers are enabled.
    ZeroStackWords,
}

/// Timer service static-memory contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TimerTaskMemory {
    /// `configUSE_TIMERS == 1` and retained callbacks provide timer task memory.
    Enabled {
        stack_depth_symbol: &'static str,
        stack_words: usize,
        control_block_section: &'static str,
        stack_section: &'static str,
        callback_symbol: &'static str,
        audit_surface_id: &'static str,
        source_evidence_paths: &'static [&'static str],
        evidence_classes: &'static [EvidenceClass],
    },
    /// `configUSE_TIMERS == 0`; no timer task memory callback is active.
    Disabled {
        config_symbol: &'static str,
        source_evidence_paths: &'static [&'static str],
        evidence_classes: &'static [EvidenceClass],
    },
}

impl TimerTaskMemory {
    /// Creates an enabled timer-service memory contract.
    pub fn enabled(
        stack_depth_symbol: &'static str,
        stack_words: usize,
    ) -> Result<Self, TimerTaskMemoryError> {
        if stack_words == 0 {
            return Err(TimerTaskMemoryError::ZeroStackWords);
        }

        Ok(Self::Enabled {
            stack_depth_symbol,
            stack_words,
            control_block_section: ".ccmram",
            stack_section: ".ccmram",
            callback_symbol: "vApplicationGetTimerTaskMemory",
            audit_surface_id: "freertos-timer-contracts",
            source_evidence_paths: TIMER_SOURCE_EVIDENCE,
            evidence_classes: TIMER_EVIDENCE,
        })
    }

    /// Creates a disabled timer-service contract.
    pub fn disabled() -> Self {
        Self::Disabled {
            config_symbol: "configUSE_TIMERS",
            source_evidence_paths: TIMER_SOURCE_EVIDENCE,
            evidence_classes: TIMER_EVIDENCE,
        }
    }

    /// Returns true when the retained build enables FreeRTOS software timers.
    pub fn is_enabled(&self) -> bool {
        matches!(self, Self::Enabled { .. })
    }

    /// Returns stack depth in `StackType_t` words when timers are enabled.
    pub fn maybe_stack_words(&self) -> Option<usize> {
        match self {
            Self::Enabled { stack_words, .. } => Some(*stack_words),
            Self::Disabled { .. } => None,
        }
    }

    /// Returns the retained config or stack-depth symbol that controls this contract.
    pub fn config_symbol(&self) -> &'static str {
        match self {
            Self::Enabled {
                stack_depth_symbol, ..
            } => stack_depth_symbol,
            Self::Disabled { config_symbol, .. } => config_symbol,
        }
    }

    /// Returns the timer callback symbol when timer memory is enabled.
    pub fn maybe_callback_symbol(&self) -> Option<&'static str> {
        match self {
            Self::Enabled {
                callback_symbol, ..
            } => Some(callback_symbol),
            Self::Disabled { .. } => None,
        }
    }

    /// Returns the Phase 5 unsafe-audit surface ID when retained timer storage exists.
    pub fn maybe_audit_surface_id(&self) -> Option<&'static str> {
        match self {
            Self::Enabled {
                audit_surface_id, ..
            } => Some(audit_surface_id),
            Self::Disabled { .. } => None,
        }
    }

    /// Returns source paths proving retained timer callback behavior.
    pub fn source_evidence_paths(&self) -> &'static [&'static str] {
        match self {
            Self::Enabled {
                source_evidence_paths,
                ..
            }
            | Self::Disabled {
                source_evidence_paths,
                ..
            } => source_evidence_paths,
        }
    }

    /// Returns evidence classes for timer memory and scheduler timing.
    pub fn evidence_classes(&self) -> &'static [EvidenceClass] {
        match self {
            Self::Enabled {
                evidence_classes, ..
            }
            | Self::Disabled {
                evidence_classes, ..
            } => evidence_classes,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn timer_task_memory_distinguishes_enabled_from_disabled() {
        // Arrange
        let enabled = TimerTaskMemory::enabled("configTIMER_TASK_STACK_DEPTH", 1_024)
            .expect("nonzero timer task stack creates enabled memory");
        let disabled = TimerTaskMemory::disabled();

        // Act, Assert
        assert!(enabled.is_enabled());
        assert!(!disabled.is_enabled());
        assert_eq!(enabled.maybe_stack_words(), Some(1_024));
        assert_eq!(disabled.maybe_stack_words(), None);
    }

    #[test]
    fn timer_task_memory_rejects_zero_stack_words_when_enabled() {
        // Arrange, Act
        let result = TimerTaskMemory::enabled("configTIMER_TASK_STACK_DEPTH", 0);

        // Assert
        assert_eq!(result, Err(TimerTaskMemoryError::ZeroStackWords));
    }
}
