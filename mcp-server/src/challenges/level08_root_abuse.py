"""
Level 8: MCP Root Resource Listing Abuse
Difficulty: Advanced
Category: Information Disclosure

VULNERABILITY:
The MCP server's root resource listing exposes internal resources
that shouldn't be publicly accessible, leaking sensitive information.

OBJECTIVE:
Abuse the root listing feature to discover and access hidden resources.

FIX APPLIED (to avoid breaking other challenges / clients):
- Renamed tools that collide with MCP protocol methods:
  - list_resources  -> public_list_resources
  - read_resource   -> public_read_resource
This prevents some MCP clients from calling Level 8 tools when they intended
to use MCP protocol resource operations (resources/list, resources/read).
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseChallenge, ChallengeInfo, Difficulty, Hint

logger = logging.getLogger(__name__)


class Level8RootAbuse(BaseChallenge):
    """Level 8: Root Resource Listing Information Disclosure"""

    def __init__(self):
        super().__init__()
        self.info = self.get_challenge_info()

        self.all_resources = {
            # Public resources
            "vulnmcp://public/welcome": "Welcome to VulnMCP Level 8!",
            "vulnmcp://public/docs": "Public documentation...",

            # Internal resources (should be hidden!)
            "vulnmcp://internal/config": f"Internal config - Flag: {self.info.flag}",
            "vulnmcp://internal/secrets": "Database: postgres://admin:secret@localhost",
            "vulnmcp://internal/keys": "API_KEY=sk-secret-key-12345",

            # Debug resources (should never be exposed!)
            "vulnmcp://debug/logs": "Error logs and stack traces...",
            "vulnmcp://debug/state": "Application state dump...",
        }

    def get_challenge_info(self) -> ChallengeInfo:
        return ChallengeInfo(
            id=8,
            name="level08_root_abuse",
            title="🎯 Level 8: Root Listing Disclosure",
            description=(
                "The FileSystem MCP server provides resource access.\n\n"
                "You can list available resources and read them.\n"
                "Only public resources should be visible...\n\n"
                "Available tools:\n"
                "- 'public_list_resources' - List available resources\n"
                "- 'public_read_resource'  - Read resource content\n\n"
                "🎯 OBJECTIVE: Find and access internal resources to get the flag!\n\n"
                "💡 Sometimes servers expose more than they should in listings..."
            ),
            difficulty=Difficulty.ADVANCED,
            points=350,
            flag="FLAG{R00T_L1ST1NG_L34K_PR0}",
            category="MCP Information Disclosure",
            tags=["information-disclosure", "enumeration", "root-listing"],
            hints=[
                Hint(
                    level=1,
                    text="Try public_list_resources() with different parameters. What if you requested the root listing?",
                    points_cost=35,
                ),
                Hint(
                    level=2,
                    text="Use public_list_resources(show_all=true) or public_list_resources(filter='*')",
                    points_cost=60,
                ),
                Hint(
                    level=3,
                    text="The server accepts 'show_all' parameter that exposes internal resources!",
                    points_cost=80,
                ),
            ],
        )

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "public_list_resources",
                "description": "List available resources (with optional parameters) (Level 8)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "description": "Filter resources by pattern (optional)",
                        },
                        "show_all": {
                            "type": "boolean",
                            "description": "Show all resources including internal (optional)",
                        },
                    },
                },
            },
            {
                "name": "public_read_resource",
                "description": "Read a resource by URI (Level 8)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "uri": {
                            "type": "string",
                            "description": "Resource URI to read",
                        }
                    },
                    "required": ["uri"],
                },
            },
            {
                "name": "submit_flag",
                "description": "Submit the flag (Level 8)",
                "inputSchema": {
                    "type": "object",
                    "properties": {"flag": {"type": "string"}},
                    "required": ["flag"],
                },
            },
        ]

    def get_resources(self) -> List[Dict[str, Any]]:
        """Default public resources"""
        return [
            {
                "uri": "vulnmcp://public/welcome",
                "name": "Welcome Page",
                "description": "Public welcome page",
                "mimeType": "text/plain",
            },
            {
                "uri": "vulnmcp://public/docs",
                "name": "Documentation",
                "description": "Public documentation",
                "mimeType": "text/plain",
            },
        ]

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[Any]:
        if name == "public_list_resources":
            return await self._list_resources(
                arguments.get("filter"),
                arguments.get("show_all", False),
            )
        if name == "public_read_resource":
            return await self._read_resource(arguments.get("uri", ""))
        if name == "submit_flag":
            return await self._submit_flag(arguments.get("flag", ""))

        return [{"type": "text", "text": f"Unknown tool: {name}"}]

    async def _list_resources(
        self,
        filter_pattern: Optional[str] = None,
        show_all: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        VULNERABLE: When show_all=true, exposes internal resources!
        This is an information disclosure vulnerability.
        """
        self.attempts += 1

        logger.warning(
            f"⚠️ [LEVEL 8] public_list_resources called with filter={filter_pattern}, show_all={show_all}"
        )

        # NOTE: filter_pattern is intentionally not enforced strictly; this is a training vuln.
        if show_all:
            logger.warning("🚨 [LEVEL 8] INTERNAL RESOURCES EXPOSED!")

            result = "📋 ALL RESOURCES (INCLUDING INTERNAL):\n\n"
            result += "⚠️ WARNING: Internal resources exposed!\n\n"

            for uri in self.all_resources.keys():
                category = uri.split("://", 1)[1].split("/", 1)[0]
                name = uri.split("/")[-1]
                result += f"URI: {uri}\n"
                result += f"Category: {category}\n"
                result += f"Name: {name}\n"
                result += "-" * 40 + "\n"

            result += "\n💡 Now try reading the internal resources!"
            return [{"type": "text", "text": result}]

        # Normal listing - only public resources
        result = "📋 Available Resources:\n\n"
        for uri in self.all_resources:
            if uri.startswith("vulnmcp://public/"):
                result += f"- {uri}\n"

        result += "\n💡 Use public_read_resource to access content"
        return [{"type": "text", "text": result}]

    async def _read_resource(self, uri: str) -> List[Dict[str, Any]]:
        """Read resource content (Level 8 tool, not MCP protocol resource read)"""
        logger.warning(f"⚠️ [LEVEL 8] public_read_resource: {uri}")

        if uri not in self.all_resources:
            return [{"type": "text", "text": f"❌ Resource not found: {uri}"}]

        content = self.all_resources[uri]

        if uri.startswith("vulnmcp://internal/") or uri.startswith("vulnmcp://debug/"):
            logger.warning(f"🚨 [LEVEL 8] INTERNAL RESOURCE ACCESSED: {uri}")

            if "FLAG{" in content:
                return [{
                    "type": "text",
                    "text": (
                        "🎉 INTERNAL RESOURCE ACCESSED!\n\n"
                        f"URI: {uri}\n"
                        f"{'='*50}\n"
                        f"Content:\n{content}\n"
                        f"{'='*50}\n\n"
                        "Submit this flag to complete the level!"
                    ),
                }]

        return [{"type": "text", "text": f"📄 {uri}\n\n{content}"}]

    async def _submit_flag(self, flag: str) -> List[Dict[str, Any]]:
        if self.check_flag(flag):
            score = self.calculate_score(self.info.points)
            return [{
                "type": "text",
                "text": (
                    "🎉🎉🎉 LEVEL 8 COMPLETED! 🎉🎉🎉\n\n"
                    f"✅ Flag: {flag}\n"
                    f"⭐ Score: {score}/{self.info.points}\n\n"
                    "═══════════════════════════════════════\n"
                    "INFORMATION DISCLOSURE ANALYSIS:\n"
                    "═══════════════════════════════════════\n\n"
                    "The Vulnerability:\n"
                    "- Root resource listing exposed internals\n"
                    "- show_all parameter not properly restricted\n"
                    "- No access control on resource enumeration\n"
                    "- Information leakage through discovery\n\n"
                    "SECURE IMPLEMENTATION:\n"
                    "✅ Never expose internal resources in listings\n"
                    "✅ Implement proper access control\n"
                    "✅ Whitelist public resources only\n"
                    "✅ Remove debug parameters in production\n"
                ),
            }]

        return [{"type": "text", "text": "❌ Incorrect flag!"}]

    async def handle_resource_read(self, uri: str) -> str:
        # Keep behavior as-is for this level: it teaches tool-based enumeration,
        # not MCP protocol resources/read.
        return "Use the public_read_resource tool instead"

    def check_flag(self, submitted_flag: str) -> bool:
        return submitted_flag.strip() == self.info.flag
