from typing import Optional

class MCPTransport:
    def __init__(self, transport_type: str = "STDIO"):
        self.transport_type = transport_type

    def format_rpc_payload(self, method: str, params: dict, msg_id: int) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": method,
            "params": params
        }
