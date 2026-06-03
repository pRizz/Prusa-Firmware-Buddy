/// Error returned when an interrupt priority cannot satisfy caller limits.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum InterruptPriorityError {
    /// Priority exceeded the caller-provided maximum value.
    AboveMaximum,
}

/// Checked interrupt priority value.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct InterruptPriority {
    value: u8,
    max_priority: u8,
}

impl InterruptPriority {
    /// Creates a priority that is at most the caller-provided maximum.
    pub fn new(value: u8, max_priority: u8) -> Result<Self, InterruptPriorityError> {
        if value > max_priority {
            return Err(InterruptPriorityError::AboveMaximum);
        }

        Ok(Self {
            value,
            max_priority,
        })
    }

    /// Returns the checked priority value.
    pub fn value(&self) -> u8 {
        self.value
    }

    /// Returns the maximum priority value used for this check.
    pub fn max_priority(&self) -> u8 {
        self.max_priority
    }
}

/// Named retained interrupt line contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct InterruptLine {
    irq_number: i16,
    priority: InterruptPriority,
    owner_source_path: &'static str,
    audit_risk: &'static str,
}

impl InterruptLine {
    /// Creates a named interrupt line without changing production IRQ behavior.
    pub fn new(irq_number: i16, priority: InterruptPriority) -> Self {
        Self {
            irq_number,
            priority,
            owner_source_path: "src/common/Pin.cpp",
            audit_risk: "STM32G0 already-enabled IRQ concern remains a named audit risk",
        }
    }

    /// Returns the retained IRQ number.
    pub fn irq_number(&self) -> i16 {
        self.irq_number
    }

    /// Returns the checked interrupt priority.
    pub fn priority(&self) -> InterruptPriority {
        self.priority
    }

    /// Returns the retained source path that owns interrupt behavior.
    pub fn owner_source_path(&self) -> &'static str {
        self.owner_source_path
    }

    /// Returns the named audit risk retained from `src/common/Pin.cpp`.
    pub fn audit_risk(&self) -> &'static str {
        self.audit_risk
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn interrupt_priority_rejects_values_above_maximum() {
        // Arrange
        let priority = 16;
        let max_priority = 15;

        // Act
        let result = InterruptPriority::new(priority, max_priority);

        // Assert
        assert!(matches!(result, Err(InterruptPriorityError::AboveMaximum)));
    }
}
