"""
Level 8: MCP Root Resource Listing Abuse
Difficulty: Advanced
Category: Information Disclosure

VULNERABILITY:
The MCP server's root resource listing exposes internal resources
that shouldn't be publicly accessible, leaking sensitive information.

OBJECTIVE:
Abuse the root listing feature to discover and access hidden resources.
"""

import logging
from typing import Any, Dict, List
from .base import BaseChallenge, ChallengeInfo, Difficulty, Hint

logger = logging.getLogger(__name__)


class Level8RootAbuse(BaseChallenge):
    """Level 8: Root Resource Listing Information Disclosure"""
    
    def __init__(self):
        super().__init__()
        self.all_resources = {
            # Public resources
            "vulnmcp://public/welcome": "Welcome to VulnMCP Level 8!",
            "vulnmcp://public/docs": "Public documentation...",
            
            # Internal resources (should be hidden!)
            "vulnmcp://internal/config": f"Internal config - Flag: {self.get_challenge_info().flag}",
            "vulnmcp://internal/secrets": "Database: postgres://admin:secret@localhost",
            "vulnmcp://internal/keys": "API_KEY=sk-secret-key-12345",
            
            # Debug resources (should never be exposed!)
            "vulnmcp://debug/logs": "Error logs and stack traces...",
            "vulnmcp://debug/state": "Application state dump..."
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
                "- 'list_resources' - List available resources\n"
                "- 'read_resource' - Read resource content\n\n"
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
                    text="Try list_resources() with different parameters. What if you requested the root listing?",
                    points_cost=35
                ),
                Hint(
                    level=2,
                    text="Use list_resources(include_internal=true) or list_resources(filter='*')",
                    points_cost=60
                ),
                Hint(
                    level=3,
                    text="The server accepts 'show_all' parameter that exposes internal resources!",
                    points_cost=80
                )
            ]
        )
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "list_resources",
                "description": "List available resources (with optional parameters)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "description": "Filter resources by pattern (optional)"
                        },
                        "show_all": {
                            "type": "boolean",
                            "description": "Show all resources including internal (optional)"
                        }
                    }
                }
            },
            {
                "name": "read_resource",
                "description": "Read a resource by URI",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "uri": {
                            "type": "string",
                            "description": "Resource URI to read"
                        }
                    },
                    "required": ["uri"]
                }
            },
            {
                "name": "submit_flag",
                "description": "Submit the flag",
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
        """Default public resources"""
        return [
            {
                "uri": "vulnmcp://public/welcome",
                "name": "Welcome Page",
                "description": "Public welcome page",
                "mimeType": "text/plain"
            },
            {
                "uri": "vulnmcp://public/docs",
                "name": "Documentation",
                "description": "Public documentation",
                "mimeType": "text/plain"
            }
        ]
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[Any]:
        if name == "list_resources":
            return await self._list_resources(
                arguments.get("filter"),
                arguments.get("show_all", False)
            )
        elif name == "read_resource":
            return await self._read_resource(arguments.get("uri", ""))
        elif name == "submit_flag":
            return await self._submit_flag(arguments.get("flag", ""))
        
        return [{"type": "text", "text": f"Unknown tool: {name}"}]
    
    async def _list_resources(
        self, 
        filter_pattern: str = None, 
        show_all: bool = False
    ) -> List[Dict[str, Any]]:
        """
        VULNERABLE: When show_all=true, exposes internal resources!
        This is an information disclosure vulnerability
        """
        self.attempts += 1
        
        logger.warning(f"⚠️ [LEVEL 8] list_resources called with filter={filter_pattern}, show_all={show_all}")
        
        if show_all:
            # VULNERABILITY: Exposes all resources including internal!
            logger.warning("🚨 [LEVEL 8] INTERNAL RESOURCES EXPOSED!")
            
            result = "📋 ALL RESOURCES (INCLUDING INTERNAL):\n\n"
            result += "⚠️ WARNING: Internal resources exposed!\n\n"
            
            for uri, content in self.all_resources.items():
                category = uri.split("://")[1].split("/")[0]
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
        
        result += "\n💡 Use read_resource to access content"
        
        return [{"type": "text", "text": result}]
    
    async def _read_resource(self, uri: str) -> List[Dict[str, Any]]:
        """Read resource content"""
        
        logger.warning(f"⚠️ [LEVEL 8] read_resource: {uri}")
        
        if uri not in self.all_resources:
            return [{
                "type": "text",
                "text": f"❌ Resource not found: {uri}"
            }]
        
        content = self.all_resources[uri]
        
        # Check if accessing internal resource
        if uri.startswith("vulnmcp://internal/") or uri.startswith("vulnmcp://debug/"):
            logger.warning(f"🚨 [LEVEL 8] INTERNAL RESOURCE ACCESSED: {uri}")
            
            if "FLAG{" in content:
                return [{
                    "type": "text",
                    "text": (
                        f"🎉 INTERNAL RESOURCE ACCESSED!\n\n"
                        f"URI: {uri}\n"
                        f"{'='*50}\n"
                        f"Content:\n"
                        f"{content}\n"
                        f"{'='*50}\n\n"
                        f"You successfully discovered and accessed internal resources!\n"
                        f"Submit this flag to complete the level!"
                    )
                }]
        
        return [{
            "type": "text",
            "text": f"📄 {uri}\n\n{content}"
        }]
    
    async def _submit_flag(self, flag: str) -> List[Dict[str, Any]]:
        if self.check_flag(flag):
            score = self.calculate_score(self.info.points)
            return [{
                "type": "text",
                "text": (
                    f"🎉🎉🎉 LEVEL 8 COMPLETED! 🎉🎉🎉\n\n"
                    f"✅ Flag: {flag}\n"
                    f"⭐ Score: {score}/{self.info.points}\n\n"
                    f"═══════════════════════════════════════\n"
                    f"INFORMATION DISCLOSURE ANALYSIS:\n"
                    f"═══════════════════════════════════════\n\n"
                    f"The Vulnerability:\n"
                    f"- Root resource listing exposed internals\n"
                    f"- show_all parameter not properly restricted\n"
                    f"- No access control on resource enumeration\n"
                    f"- Information leakage through discovery\n\n"
                    f"Real-World Examples:\n"
                    f"- AWS S3 bucket listings\n"
                    f"- Directory listing enabled\n"
                    f"- GraphQL introspection abuse\n"
                    f"- API endpoint enumeration\n\n"
                    f"Impact:\n"
                    f"- Reveals internal structure\n"
                    f"- Exposes hidden endpoints\n"
                    f"- Leaks sensitive URIs\n"
                    f"- Enables further attacks\n\n"
                    f"SECURE IMPLEMENTATION:\n"
                    f"✅ Never expose internal resources in listings\n"
                    f"✅ Implement proper access control\n"
                    f"✅ Whitelist public resources only\n"
                    f"✅ Remove debug parameters in production\n"
                    f"✅ Audit resource exposure\n\n"
                    f"Two more expert levels await! 💪"
                )
            }]
        else:
            return [{"type": "text", "text": "❌ Incorrect flag!"}]
    
    async def handle_resource_read(self, uri: str) -> str:
        return "Use the read_resource tool instead"
    
    def check_flag(self, submitted_flag: str) -> bool:
        return submitted_flag.strip() == self.info.flag