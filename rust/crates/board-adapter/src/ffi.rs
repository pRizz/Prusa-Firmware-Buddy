/// Retained foreign-code component that may own a named symbol contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ForeignComponentId {
    /// STM32 HAL/CMSIS retained vendor surface.
    HalCmsis,
    /// Retained FreeRTOS kernel and wrappers.
    FreeRtos,
    /// Buddy-owned retained runtime shell.
    BuddyRuntime,
    /// xBuddy Extension retained runtime surface.
    XbuddyExtensionRuntime,
}

/// Error returned when an FFI symbol name is not narrow and stable.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ForeignSymbolError {
    /// Symbol names must not be empty.
    EmptyName,
    /// Symbol names must not contain whitespace.
    NameContainsWhitespace,
}

/// Named retained-code FFI symbol contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ForeignSymbol {
    component_id: ForeignComponentId,
    name: &'static str,
}

impl ForeignSymbol {
    /// Creates a named symbol contract without generating broad C/C++ bindings.
    pub fn new(
        component_id: ForeignComponentId,
        name: &'static str,
    ) -> Result<Self, ForeignSymbolError> {
        if name.is_empty() {
            return Err(ForeignSymbolError::EmptyName);
        }

        if name.chars().any(char::is_whitespace) {
            return Err(ForeignSymbolError::NameContainsWhitespace);
        }

        Ok(Self { component_id, name })
    }

    /// Returns the retained component that owns the symbol.
    pub fn component_id(&self) -> ForeignComponentId {
        self.component_id
    }

    /// Returns the exact retained symbol name.
    pub fn name(&self) -> &'static str {
        self.name
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn foreign_symbol_rejects_empty_names() {
        // Arrange
        let component_id = ForeignComponentId::HalCmsis;

        // Act
        let result = ForeignSymbol::new(component_id, "");

        // Assert
        assert!(matches!(result, Err(ForeignSymbolError::EmptyName)));
    }

    #[test]
    fn foreign_symbol_rejects_names_with_whitespace() {
        // Arrange
        let component_id = ForeignComponentId::HalCmsis;

        // Act
        let result = ForeignSymbol::new(component_id, "HAL RCC");

        // Assert
        assert!(matches!(
            result,
            Err(ForeignSymbolError::NameContainsWhitespace)
        ));
    }

    #[test]
    fn unsafe_operations_stay_in_audited_board_adapter_modules() {
        // Arrange
        let audit_manifest =
            include_str!("../../../../tools/bazel/manifests/unsafe_boundary_audit.json");
        let unsafe_block = concat!("unsafe", " {");
        let unsafe_fn = concat!("unsafe", " fn");
        let unsafe_extern = concat!("unsafe", " extern");
        let allowed_paths = [
            "rust/crates/board-adapter/src/mmio.rs",
            "rust/crates/board-adapter/src/interrupt.rs",
            "rust/crates/board-adapter/src/ffi.rs",
        ];
        let sources = [
            (
                "rust/crates/board-adapter/src/lib.rs",
                include_str!("lib.rs"),
            ),
            (
                "rust/crates/board-adapter/src/clock.rs",
                include_str!("clock.rs"),
            ),
            (
                "rust/crates/board-adapter/src/dma.rs",
                include_str!("dma.rs"),
            ),
            (
                "rust/crates/board-adapter/src/mcu.rs",
                include_str!("mcu.rs"),
            ),
            (
                "rust/crates/board-adapter/src/memory_region.rs",
                include_str!("memory_region.rs"),
            ),
            (
                "rust/crates/board-adapter/src/mmio.rs",
                include_str!("mmio.rs"),
            ),
            (
                "rust/crates/board-adapter/src/interrupt.rs",
                include_str!("interrupt.rs"),
            ),
            (
                "rust/crates/board-adapter/src/ffi.rs",
                include_str!("ffi.rs"),
            ),
        ];

        // Act
        let source_paths_with_unsafe_operations = sources
            .into_iter()
            .filter_map(|(path, source)| {
                if source.contains(unsafe_block)
                    || source.contains(unsafe_fn)
                    || source.contains(unsafe_extern)
                {
                    return Some(path);
                }

                None
            })
            .collect::<Vec<_>>();

        // Assert
        assert!(
            source_paths_with_unsafe_operations.contains(&"rust/crates/board-adapter/src/mmio.rs")
        );
        for path in &source_paths_with_unsafe_operations {
            assert!(allowed_paths.contains(path));
            assert!(audit_manifest.contains(path));
        }
    }
}
