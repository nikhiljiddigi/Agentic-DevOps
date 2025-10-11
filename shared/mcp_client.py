class MockMCPClient:
    """Simulates MCP client behavior (local demo)."""
    def __call__(self, context_request, tool_name=None, tool_args=None):
        print(f"🧩 Mock MCP request: {context_request}")
        return None  # can return fake data later
