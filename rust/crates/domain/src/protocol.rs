use crate::InvariantError;

/// User-visible Connect registration code.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct RegistrationCode(String);

impl RegistrationCode {
    /// Parses an eight-character ASCII alphanumeric registration code.
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if raw.len() != 8
            || !raw
                .chars()
                .all(|character| character.is_ascii_alphanumeric())
        {
            return Err(InvariantError::InvalidRegistrationCode);
        }

        Ok(Self(raw))
    }

    /// Returns the registration code as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Connect endpoint URL accepted by the domain state machine.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct ConnectEndpoint(String);

impl ConnectEndpoint {
    /// Parses a Connect endpoint URL with an accepted HTTP scheme.
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if !(raw.starts_with("https://") || raw.starts_with("http://")) {
            return Err(InvariantError::InvalidConnectEndpoint);
        }

        Ok(Self(raw))
    }

    /// Returns the endpoint URL as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Initial disconnected protocol state.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Disconnected;

impl Disconnected {
    /// Moves from disconnected to registered only after a validated
    /// registration code exists.
    pub fn register(self, code: RegistrationCode) -> Registered {
        Registered { code }
    }
}

/// Registered protocol state before a live endpoint connection exists.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Registered {
    code: RegistrationCode,
}

impl Registered {
    /// Connects to a validated endpoint and consumes the registration state.
    pub fn connect(self, endpoint: ConnectEndpoint) -> Connected {
        Connected {
            code: self.code,
            endpoint,
        }
    }

    /// Returns the registration code.
    pub fn code(&self) -> &RegistrationCode {
        &self.code
    }
}

/// Connected protocol state with both registration code and endpoint present.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Connected {
    code: RegistrationCode,
    endpoint: ConnectEndpoint,
}

impl Connected {
    /// Returns the registration code used for this connection.
    pub fn code(&self) -> &RegistrationCode {
        &self.code
    }

    /// Returns the connected endpoint.
    pub fn endpoint(&self) -> &ConnectEndpoint {
        &self.endpoint
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_malformed_registration_code() {
        // Arrange
        let raw_code = "ABC-123";

        // Act
        let result = RegistrationCode::parse(raw_code);

        // Assert
        assert_eq!(result, Err(InvariantError::InvalidRegistrationCode));
    }

    #[test]
    fn rejects_endpoint_without_http_scheme() {
        // Arrange
        let raw_endpoint = "connect.prusa3d.com";

        // Act
        let result = ConnectEndpoint::parse(raw_endpoint);

        // Assert
        assert_eq!(result, Err(InvariantError::InvalidConnectEndpoint));
    }

    #[test]
    fn moves_through_registration_state_machine() {
        // Arrange
        let disconnected = Disconnected;
        let code = RegistrationCode::parse("ABC12345").expect("registration code has valid shape");
        let endpoint =
            ConnectEndpoint::parse("https://connect.prusa3d.com").expect("endpoint has scheme");

        // Act
        let connected = disconnected.register(code).connect(endpoint);

        // Assert
        assert_eq!(connected.code().as_str(), "ABC12345");
        assert_eq!(connected.endpoint().as_str(), "https://connect.prusa3d.com");
    }
}
