class Context:
    """Root class of all contexts."""
    pass


class ClientActionContext(Context):
    """Context that provides client actions, which include failing and forwarding.
    These contexts are typically made available in response to commands."""

    def fail(self, error_message: str) -> Exception:
        """Fail the command with the given message"""
        pass
