"""
Level 2: MCP Resource URI Manipulation
Difficulty: Beginner
Category: Access Control

VULNERABILITY:
The resource handler doesn't properly validate URI paths, allowing
attackers to manipulate the URI to access restricted resources.

OBJECTIVE:
Manipulate resource URIs to access the admin documentation and find the flag.

LEARNING GOALS:
- Understanding MCP resource URI structure
- Path traversal in MCP resources
- URI manipulation techniques
"""

import logging
from typing import Any, Dict, List
from urllib.parse import urlparse, parse_qs
from .base import BaseChallenge, ChallengeInfo, Difficulty, Hint

logger = logging.getLogger(__name__)


class Level2ResourceURI(BaseChallenge):
    """Level 2: MCP Resource URI Manipulation"""
    
    def __init__(self):
        super().__init__()
        self.resources_db = {
            "public": {
                "welcome": "Welcome to VulnMCP! This is public documentation.",
                "about": "VulnMCP is a security training platform for MCP vulnerabilities.",
                "help": "Use MCP resources to access documentation. Try different URIs!"
            },
            "admin": {
                "config": f"ADMIN CONFIG - FLAG: {self.get_challenge_info().flag}",
                "secrets": "Admin secrets database - Restricted access",
                "internal": "Internal documentation - Do not distribute"
            }
        }
    
    def get_challenge_info(self) -> ChallengeInfo:
        return ChallengeInfo(
            id=2,
            name="level02_resource_uri",
            title=" Level 2: Resource URI Manipulation",
            description=(
                "VulnMCP has a documentation system accessible via MCP resources.\n\n"
                "You can access public docs using:\n"
                "  vulnmcp://docs/public/welcome\n"
                "  vulnmcp://docs/public/about\n"
                "  vulnmcp://docs/public/help\n\n"
                " OBJECTIVE: Find a way to access admin documentation and retrieve the flag!\n\n"
                " The resource URI handler might not be as secure as it seems..."
            ),
            difficulty=Difficulty.BEGINNER,
            points=150,
            flag="FLAG{MCP_R3S0URC3_UR1_H4CK3D}",
            category="MCP Resource Security",
            tags=["uri-manipulation", "mcp-resources", "path-traversal"],
            hints=[
                Hint(
                    level=1,
                    text="MCP resources use URI schemes. Try exploring different paths in the URI.",
                    points_cost=15
                ),
                Hint(
                    level=2,
                    text="The handler might check for 'public' but what if you try 'admin' instead?",
                    points_cost=25
                ),
                Hint(
                    level=3,
                    text="Try: vulnmcp://docs/admin/config",
                    points_cost=35
                )
            ]
        )
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Tools for Level 2"""
        return [
            {
                "name": "submit_flag",
                "description": "Submit the flag you discovered",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "flag": {"type": "string"}
                    },
                    "required": ["flag"]
                }
            }
        ]
    
    def get_resources(self) -> List[Dict[str, Any]]:
        """MCP Resources for Level 2"""
        return [
            {
                "uri": "vulnmcp://docs/public/welcome",
                "name": " Welcome Documentation",
                "description": "Public welcome documentation",
                "mimeType": "text/plain"
            },
            {
                "uri": "vulnmcp://docs/public/about",
                "name": " About VulnMCP",
                "description": "Information about this platform",
                "mimeType": "text/plain"
            },
            {
                "uri": "vulnmcp://docs/public/help",
                "name": " Help Documentation",
                "description": "How to use MCP resources",
                "mimeType": "text/plain"
            },
            {
                "uri": "vulnmcp://docs/admin/config",
                "name": " Admin Configuration",
                "description": "Restricted - Admin access only",
                "mimeType": "text/plain"
            },
            {
                "uri": "vulnmcp://docs/admin/secrets",
                "name": " Admin Secrets",
                "description": "Restricted - Admin access only",
                "mimeType": "text/plain"
            },
            {
                "uri": "vulnmcp://docs/admin/internal",
                "name": " Internal Docs",
                "description": "Restricted - Admin access only",
                "mimeType": "text/plain"
            }
    
        ]
    
    async def handle_tool_call(
        self, 
        name: str, 
        arguments: Dict[str, Any]
    ) -> List[Any]:
        """Handle tool calls"""
        
        if name == "submit_flag":
            return await self._submit_flag(arguments.get("flag", ""))
        
        return [{"type": "text", "text": f"Unknown tool: {name}"}]
    
    async def handle_resource_read(self, uri: str) -> str:
        """
        VULNERABLE: Doesn't properly validate URI paths
        
        This allows access to admin resources by manipulating the URI
        """
        self.attempts += 1
        
        logger.warning(f" [LEVEL 2] Resource requested: {uri}")
        
        # Parse the URI
        parsed = urlparse(uri)
        path_parts = parsed.path.strip('/').split('/')
        
        logger.info(f"Path parts: {path_parts}")
        
        if len(path_parts) < 2:
            return " Invalid resource URI. Format: vulnmcp://docs/category/document"
        
        category = path_parts[0]
        document = path_parts[1]
        
        # VULNERABILITY: Weak access control - only checks if category exists
        # Doesn't verify the user should have access!
        if category not in self.resources_db:
            return f" Unknown category: {category}\n\nAvailable: public"
        
        if document not in self.resources_db[category]:
            return f" Document '{document}' not found in category '{category}'"
        
        content = self.resources_db[category][document]
        
        # Check if flag was accessed
        if "FLAG{" in content and category == "admin":
            logger.warning("🚨 [LEVEL 2] ADMIN RESOURCE ACCESSED - FLAG LEAKED!")
            return (
                f" ACCESS GRANTED TO ADMIN RESOURCE!\n\n"
                f"Category: {category}\n"
                f"Document: {document}\n\n"
                f"{'='*50}\n"
                f"{content}\n"
                f"{'='*50}\n\n"
                f"You successfully manipulated the MCP resource URI!\n"
                f"Now submit this flag using the 'submit_flag' tool."
            )
        
        return f" {category}/{document}\n\n{content}"
    
    async def _submit_flag(self, flag: str) -> List[Dict[str, Any]]:
        """Submit and validate flag"""
        
        if self.check_flag(flag):
            score = self.calculate_score(self.info.points)
            return [{
                "type": "text",
                "text": (
                    f" LEVEL 2 COMPLETED! \n\n"
                    f" Flag Correct: {flag}\n"
                    f" Points Earned: {score}/{self.info.points}\n"
                    f" Hints Used: {self.hints_used}\n"
                    f" Attempts: {self.attempts}\n\n"
                    f"═══════════════════════════════════════\n"
                    f"WHAT YOU LEARNED:\n"
                    f"═══════════════════════════════════════\n\n"
                    f"1. MCP resources use URI-based access control\n"
                    f"2. URI paths must be validated, not just parsed\n"
                    f"3. Access control should verify permissions, not just existence\n"
                    f"4. Resource URIs are attack vectors like any URL\n\n"
                    f"SECURE IMPLEMENTATION:\n"
                    f"   Whitelist allowed resources per user\n"
                    f"   Validate user has permission before serving\n"
                    f"   Never expose admin URIs in resource list\n"
                    f"   Use role-based access control\n\n"
                    f"Level 3 awaits - it gets harder! "
                )
            }]
        else:
            return [{
                "type": "text",
                "text": " Incorrect flag! Keep exploring resources..."
            }]
    
    def check_flag(self, submitted_flag: str) -> bool:
        return submitted_flag.strip() == self.info.flag
