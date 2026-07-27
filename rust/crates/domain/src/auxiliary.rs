mod controller;
mod identity;
mod transport;

pub use controller::{
    AuxiliaryControllerContract, AuxiliaryControllerContractInput, AuxiliaryParityContract,
    AuxiliaryParityContractInput, AuxiliaryParityRowId, ControllerFaultClass, DockIdentity,
    ToolOffsetAxis, ToolOffsetIdentity,
};
pub use identity::{
    AuxiliaryControllerKind, AuxiliaryRuntimeState, AuxiliaryUpdateMode, FirmwareImageSource,
};
pub use transport::{
    AuxiliaryProofScope, BusEvidenceClass, MmuTransportState, MmuTransportSurface,
    ModbusRequestKind, ModbusUnitIdentity,
};

#[cfg(test)]
mod tests;
