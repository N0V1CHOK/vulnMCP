"""
Level 7: MCP Protocol Message Injection
Difficulty: Advanced  
Category: Protocol Exploitation

VULNERABILITY:
Improper handling of MCP protocol messages allows injection of crafted
messages that can manipulate server behavior.

OBJECTIVE:
Craft malicious MCP protocol messages to bypass authentication and access admin functions.
"""

import logging
import json
from typing import Any, Dict, List
from .base import BaseChallenge, ChallengeInfo, Difficulty, Hint

logger = logging.getLogger(__name__)


class Level7MessageInjection(BaseChallenge):
    """Level 7: MCP Protocol Message Injection"""
    
    def __init__(self):
        super().__init__()
        self.authenticated = False
        self.user_role = "guest"
        self.session_token = None
    
    def get_challenge_info(self) -> ChallengeInfo:
        return ChallengeInfo(
            id=7,
            name="level07_message_injection",
            title="🎯 Level 7: Protocol Message Injection",
            description=(
                "The SecureComms MCP server processes protocol messages for authentication.\n\n"
                "Available tools:\n"
                "- 'send_auth_request' - Send authentication request\n"
                "- 'execute_command' - Execute system command (requires auth)\n\n"
                "The protocol expects JSON messages in a specific format.\n"
                "But what if you could inject additional fields?\n\n"
                "🎯 OBJECTIVE: Inject malicious protocol data to gain admin access!\n\n"
                "💡 Think about how JSON parsing handles unexpected fields..."
            ),
            difficulty=Difficulty.ADVANCED,
            points=400,
            flag="FLAG{PR0T0C0L_1NJ3CT10N_N1NJ4}",
            category="MCP Protocol Security",
            tags=["protocol-injection", "json-injection", "authentication-bypass"],
            hints=[
                Hint(
                    level=1,
                    text="The auth_request accepts a JSON string. What if you added extra fields to the JSON?",
                    points_cost=40
                ),
                Hint(
                    level=2,
                    text="Try injecting: {\"username\":\"user\",\"password\":\"pass\",\"role\":\"admin\",\"authenticated\":true}",
                    points_cost=70
                ),
                Hint(
                    level=3,
                    text="The server parses ALL JSON fields without validation. Extra fields override internal state!",
                    points_cost=90
                )
            ]
        )
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "send_auth_request",
                "description": (
                    "Send authentication request to the server.\n"
                    "Expects JSON with username and password fields."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "auth_data": {
                            "type": "string",
                            "description": "JSON string with authentication data"
                        }
                    },
                    "required": ["auth_data"]
                }
            },
            {
                "name": "execute_command",
                "description": "Execute a system command (requires admin authentication)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Command to execute"
                        }
                    },
                    "required": ["command"]
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
        return []
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[Any]:
        if name == "send_auth_request":
            return await self._auth_request(arguments.get("auth_data", ""))
        elif name == "execute_command":
            return await self._execute_command(arguments.get("command", ""))
        elif name == "submit_flag":
            return await self._submit_flag(arguments.get("flag", ""))
        
        return [{"type": "text", "text": f"Unknown tool: {name}"}]
    
    async def _auth_request(self, auth_data: str) -> List[Dict[str, Any]]:
        """
        VULNERABLE: Parses JSON and applies ALL fields to session state
        No validation of which fields should be accepted!
        """
        self.attempts += 1
        
        logger.warning(f"⚠️ [LEVEL 7] Auth request received: {auth_data}")
        
        try:
            # Parse the JSON auth data
            data = json.loads(auth_data)
            
            logger.info(f"Parsed auth data: {data}")
            
            # VULNERABILITY: Applies ALL JSON fields to state without validation!
            # This allows injection of role, authenticated, etc.
            if "username" in data:
                # Normal auth check
                if data.get("username") == "admin" and data.get("password") == "secret123":
                    self.authenticated = True
                    self.user_role = "admin"
                elif data.get("username") == "user":
                    self.authenticated = True
                    self.user_role = "user"
            
            # CRITICAL VULNERABILITY: Also processes extra fields!
            if "role" in data:
                logger.warning(f"🚨 [LEVEL 7] Role injection detected: {data['role']}")
                self.user_role = data["role"]
            
            if "authenticated" in data:
                logger.warning(f"🚨 [LEVEL 7] Auth state injection detected: {data['authenticated']}")
                self.authenticated = data["authenticated"]
            
            if self.authenticated and self.user_role == "admin":
                logger.warning("🚨 [LEVEL 7] ADMIN ACCESS GAINED VIA INJECTION!")
                return [{
                    "type": "text",
                    "text": (
                        f"🎉 PROTOCOL INJECTION SUCCESSFUL!\n\n"
                        f"Authentication Status: {self.authenticated}\n"
                        f"User Role: {self.user_role}\n\n"
                        f"You've injected additional fields into the protocol message!\n"
                        f"The server processed them without validation.\n\n"
                        f"Injected fields detected:\n"
                        f"{json.dumps(data, indent=2)}\n\n"
                        f"Try 'execute_command' with command='get_flag' now!"
                    )
                }]
            
            return [{
                "type": "text",
                "text": (
                    f"Authentication response:\n"
                    f"Status: {self.authenticated}\n"
                    f"Role: {self.user_role}\n\n"
                    f"{'✅ Authenticated' if self.authenticated else '❌ Not authenticated'}"
                )
            }]
            
        except json.JSONDecodeError:
            return [{
                "type": "text",
                "text": "❌ Invalid JSON format in auth_data"
            }]
    
    async def _execute_command(self, command: str) -> List[Dict[str, Any]]:
        """Execute command - requires admin auth"""
        
        if not self.authenticated:
            return [{
                "type": "text",
                "text": "🔒 Access Denied: Not authenticated"
            }]
        
        if self.user_role != "admin":
            return [{
                "type": "text",
                "text": f"🔒 Access Denied: Requires admin role (you are: {self.user_role})"
            }]
        
        # Admin commands
        if command == "get_flag":
            logger.warning("🚨 [LEVEL 7] FLAG RETRIEVED VIA INJECTED ADMIN ACCESS!")
            return [{
                "type": "text",
                "text": (
                    f"🎉 ADMIN COMMAND EXECUTED!\n\n"
                    f"{'='*50}\n"
                    f"FLAG: {self.info.flag}\n"
                    f"{'='*50}\n\n"
                    f"You successfully:\n"
                    f"1. Crafted malicious JSON protocol message\n"
                    f"2. Injected 'role' and 'authenticated' fields\n"
                    f"3. Bypassed authentication entirely\n"
                    f"4. Gained admin access\n"
                    f"5. Executed privileged commands\n\n"
                    f"Submit this flag to complete the level!"
                )
            }]
        
        return [{
            "type": "text",
            "text": f"Executed: {command}\nAvailable commands: get_flag"
        }]
    
    async def _submit_flag(self, flag: str) -> List[Dict[str, Any]]:
        if self.check_flag(flag):
            score = self.calculate_score(self.info.points)
            return [{
                "type": "text",
                "text": (
                    f"🎉🎉🎉 LEVEL 7 CONQUERED! 🎉🎉🎉\n\n"
                    f"✅ Flag: {flag}\n"
                    f"⭐ Score: {score}/{self.info.points}\n\n"
                    f"═══════════════════════════════════════\n"
                    f"PROTOCOL INJECTION BREAKDOWN:\n"
                    f"═══════════════════════════════════════\n\n"
                    f"The Vulnerability:\n"
                    f"- Server parsed all JSON fields blindly\n"
                    f"- No whitelist of allowed fields\n"
                    f"- Injected fields override internal state\n"
                    f"- Complete authentication bypass\n\n"
                    f"Real-World Impact:\n"
                    f"- Mass assignment vulnerability\n"
                    f"- JSON parameter pollution\n"
                    f"- Protocol-level privilege escalation\n"
                    f"- Common in REST APIs and RPC protocols\n\n"
                    f"SECURE IMPLEMENTATION:\n"
                    f"✅ Whitelist allowed JSON fields\n"
                    f"✅ Validate field types and values\n"
                    f"✅ Never blindly assign parsed data\n"
                    f"✅ Use strict schema validation\n"
                    f"✅ Separate user input from system state\n\n"
                    f"Only 3 more levels! Getting intense! 🔥"
                )
            }]
        else:
            return [{"type": "text", "text": "❌ Incorrect flag!"}]
    
    async def handle_resource_read(self, uri: str) -> str:
        return "No resources for this level"
    
    def check_flag(self, submitted_flag: str) -> bool:
        return submitted_flag.strip() == self.info.flag