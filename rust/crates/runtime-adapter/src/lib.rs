#![forbid(unsafe_code)]

//! Thin runtime adapter boundary for validated product profiles.
//!
//! This crate intentionally does not boot FreeRTOS or STM32 startup code. It
//! gives later runtime work a typed shell around the pure domain profile.

use buddy_domain::{BootloaderMode, ProductProfile};

pub mod allocator;
pub mod linker;
pub mod panic_boundary;
pub mod queue;
pub mod startup;
pub mod static_memory;
pub mod synchronization;
pub mod task;
pub mod timer;

pub use allocator::AllocatorBoundary;
pub use linker::{BootModeLinkerScript, LinkerSection};
pub use panic_boundary::{CrashDumpBoundary, PanicBoundary, WatchdogBoundary};
pub use queue::StaticQueueStorage;
pub use startup::{EvidenceClass, StartupSurface, StartupVectorTable};
pub use static_memory::StaticTaskMemory;
pub use synchronization::{
    EventGroupContract, MutexContract, SemaphoreContract, SynchronizationEvidence,
    SynchronizationPrimitive, WaitConditionContract,
};
pub use task::{DependencyMask, RuntimeTask, TaskDependency, TaskStartupContract};
pub use timer::TimerTaskMemory;

/// Runtime adapter boundary selected by validated firmware profile data.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RuntimeAdapterBoundary {
    profile: ProductProfile,
}

impl RuntimeAdapterBoundary {
    /// Creates a runtime adapter boundary from a validated profile.
    pub fn new(profile: ProductProfile) -> Self {
        Self { profile }
    }

    /// Returns the selected bootloader mode.
    pub fn bootloader_mode(&self) -> BootloaderMode {
        self.profile.bootloader_mode()
    }

    /// Returns true for auxiliary-controller runtime personalities.
    pub fn is_auxiliary_runtime(&self) -> bool {
        self.profile.is_auxiliary()
    }
}
