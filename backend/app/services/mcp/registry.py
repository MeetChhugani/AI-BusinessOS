from typing import Dict, Any, List

class MCPServerRegistry:
    def __init__(self):
        self._servers = {}

    def register_server(self, server_name: str, config: Dict[str, Any]) -> None:
        self._servers[server_name] = {
            "name": server_name,
            "config": config,
            "status": "REGISTERED"
        }

    def list_servers(self) -> List[Dict[str, Any]]:
        return list(self._servers.values())
