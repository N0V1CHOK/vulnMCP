import logging
import posixpath
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .base import BaseChallenge, ChallengeInfo, Difficulty, Hint

logger = logging.getLogger(__name__)


class Level2ResourceURI(BaseChallenge):
    """Level 2: MCP Resource URI Manipulation"""

    def __init__(self):
        super().__init__()
        self.info = self.get_challenge_info()

        self.resources_db = {
            "public": {
                "welcome": "Welcome to VulnMCP! This is public documentation.",
                "about": "VulnMCP is a security training platform for MCP vulnerabilities.",
                "help": "Use MCP resources to access documentation. Try different URIs!",
            },
            "admin": {
                "config": f"ADMIN CONFIG - FLAG: {self.info.flag}",
                "secrets": "Admin secrets database - Restricted access",
                "internal": "Internal documentation - Do not distribute",
            },
        }

    def get_challenge_info(self) -> ChallengeInfo:
        return ChallengeInfo(
            id=2,
            name="level02_resource_uri",
            title="Level 2: Resource URI Manipulation",
            description=(
                "VulnMCP has a documentation system accessible via MCP resources.\n\n"
                "You can access public docs using:\n"
                "  vulnmcp://docs/public/welcome\n"
                "  vulnmcp://docs/public/about\n"
                "  vulnmcp://docs/public/help\n\n"
                "OBJECTIVE: Find a way to access admin documentation and retrieve the flag!\n\n"
                "The resource URI handler might not be as secure as it seems..."
            ),
            difficulty=Difficulty.BEGINNER,
            points=150,
            flag="FLAG{MCP_R3S0URC3_UR1_H4CK3D}",
            category="MCP Resource Security",
            tags=["uri-manipulation", "mcp-resources", "path-traversal"],
            hints=[
                Hint(level=1, text="Try exploring different paths in the URI.", points_cost=15),
                Hint(level=2, text="What if you try 'admin' instead of 'public'?", points_cost=25),
                Hint(level=3, text="Try: vulnmcp://docs/admin/config", points_cost=35),
            ],
        )

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        IMPORTANT:
        Some MCP clients (including various desktop chat UIs) do NOT expose MCP protocol
        resources/read to the user, and instead try to call a tool named read_resource.

        To make Level 2 solvable everywhere, we add a Level 2 tool that proxies to the
        resource handler. This does not change the vulnerability; it only provides an interface.
        """
        return [
            {
                "name": "read_doc",
                "description": "Read a docs URI under vulnmcp://docs/... (Level 2)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "uri": {"type": "string", "description": "Docs URI to read"},
                    },
                    "required": ["uri"],
                },
            },
            {
                "name": "submit_flag",
                "description": "Submit the flag you discovered (Level 2)",
                "inputSchema": {
                    "type": "object",
                    "properties": {"flag": {"type": "string"}},
                    "required": ["flag"],
                },
            },
        ]

    def get_resources(self) -> List[Dict[str, Any]]:
        # Public only; admin is discoverable by URI manipulation
        return [
            {
                "uri": "vulnmcp://docs/public/welcome",
                "name": "Welcome Documentation",
                "description": "Public welcome documentation",
                "mimeType": "text/plain",
            },
            {
                "uri": "vulnmcp://docs/public/about",
                "name": "About VulnMCP",
                "description": "Information about this platform",
                "mimeType": "text/plain",
            },
            {
                "uri": "vulnmcp://docs/public/help",
                "name": "Help Documentation",
                "description": "How to use MCP resources",
                "mimeType": "text/plain",
            },
        ]

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[Any]:
        if name == "read_doc":
            uri = arguments.get("uri", "")
            text = await self.handle_resource_read(uri)
            return [{"type": "text", "text": text}]

        if name == "submit_flag":
            return await self._submit_flag(arguments.get("flag", ""))

        return [{"type": "text", "text": f"Unknown tool: {name}"}]

    async def handle_resource_read(self, uri: str) -> str:
        """
        VULNERABLE (intended):
        - Normalizes path (.. traversal) without enforcing safe base.
        - Performs existence checks only (no authorization).
        """
        self.attempts += 1
        logger.warning(f"[LEVEL 2] Resource requested: {uri}")

        parsed = urlparse(uri)
        if parsed.scheme != "vulnmcp" or parsed.netloc != "docs":
            return "Invalid resource URI. Format: vulnmcp://docs/<category>/<document>"

        normalized_path = posixpath.normpath(parsed.path or "")
        if normalized_path in ("", "."):
            return "Invalid resource URI. Format: vulnmcp://docs/<category>/<document>"

        parts = [p for p in normalized_path.strip("/").split("/") if p]
        if len(parts) < 2:
            return "Invalid resource URI. Format: vulnmcp://docs/<category>/<document>"

        category, document = parts[0], parts[1]

        if category not in self.resources_db:
            return f"Unknown category: {category}\n\nAvailable: public"

        if document not in self.resources_db[category]:
            return f"Document '{document}' not found in category '{category}'"

        content = self.resources_db[category][document]

        if "FLAG{" in content and category == "admin":
            return (
                "ACCESS GRANTED TO ADMIN RESOURCE!\n\n"
                f"Category: {category}\nDocument: {document}\n\n"
                f"{'='*50}\n{content}\n{'='*50}\n\n"
                "Submit the flag using Level 2 submit_flag."
            )

        return f"{category}/{document}\n\n{content}"

    async def _submit_flag(self, flag: str) -> List[Dict[str, Any]]:
        if self.check_flag(flag):
            score = self.calculate_score(self.info.points)
            return [{
                "type": "text",
                "text": (
                    "LEVEL 2 COMPLETED!\n\n"
                    f"Flag Correct: {flag}\n"
                    f"Points Earned: {score}/{self.info.points}\n"
                    f"Hints Used: {self.hints_used}\n"
                    f"Attempts: {self.attempts}\n"
                ),
            }]
        return [{"type": "text", "text": "Incorrect flag."}]

    def check_flag(self, submitted_flag: str) -> bool:
        return submitted_flag.strip() == self.info.flag
