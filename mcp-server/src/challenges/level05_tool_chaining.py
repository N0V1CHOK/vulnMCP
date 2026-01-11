"""
Level 5: MCP Tool Chaining Exploitation
Difficulty: Intermediate
Category: Logic Flaws

VULNERABILITY:
Multiple MCP tools that trust each other's output without validation.
By chaining tools in unexpected ways, you can escalate privileges.

OBJECTIVE:
Chain tool calls to escalate from 'guest' user to 'admin' and access the vault.
"""

import logging
from typing import Any, Dict, List
from .base import BaseChallenge, ChallengeInfo, Difficulty, Hint

logger = logging.getLogger(__name__)


class Level5ToolChaining(BaseChallenge):
    """Level 5: Tool Chaining to Escalate Privileges"""
    
    def __init__(self):
        super().__init__()
        self.current_user = {"username": "guest", "role": "guest", "verified": False}
        self.users_db = {
            "guest": {"role": "guest", "verified": False},
            "admin": {"role": "admin", "verified": True}
        }
        self.verification_codes = {
            "temp_code_12345": "admin"
        }
    
    def get_challenge_info(self) -> ChallengeInfo:
        return ChallengeInfo(
            id=5,
            name="level05_tool_chaining",
            title="🎯 Level 5: Tool Chaining Exploitation",
            description=(
                "VulnMCP Vault System has multiple authentication tools:\n\n"
                "1. 'check_user' - Check current user status\n"
                "2. 'request_verification' - Request verification code\n"
                "3. 'verify_user' - Verify user with code\n"
                "4. 'access_vault' - Access vault (admin only)\n\n"
                "You start as 'guest' user. The vault requires 'admin' role.\n\n"
                "🎯 OBJECTIVE: Chain tools to escalate to admin and access the vault!\n\n"
                "💡 Each tool trusts the previous tool's output.\n"
                "   Maybe you can exploit this chain of trust?"
            ),
            difficulty=Difficulty.INTERMEDIATE,
            points=300,
            flag="FLAG{T00L_CH41N_PR1V_3SC}",
            category="MCP Logic Flaws",
            tags=["tool-chaining", "privilege-escalation", "logic-flaw"],
            hints=[
                Hint(
                    level=1,
                    text="Look at what 'request_verification' returns. Can you use that output?",
                    points_cost=30
                ),
                Hint(
                    level=2,
                    text="The verification system generates codes but doesn't properly validate WHO requested them.",
                    points_cost=50
                ),
                Hint(
                    level=3,
                    text="Chain: request_verification(username='admin') → use returned code → verify_user(code) → access_vault()",
                    points_cost=70
                )
            ]
        )
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "check_user",
                "description": "Check current user status and permissions",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "request_verification",
                "description": "Request a verification code for a user account",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Username to verify"
                        }
                    },
                    "required": ["username"]
                }
            },
            {
                "name": "verify_user",
                "description": "Verify user with verification code",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Verification code"
                        }
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "access_vault",
                "description": "Access the secure vault (requires admin role)",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
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
        if name == "check_user":
            return await self._check_user()
        elif name == "request_verification":
            return await self._request_verification(arguments.get("username", ""))
        elif name == "verify_user":
            return await self._verify_user(arguments.get("code", ""))
        elif name == "access_vault":
            return await self._access_vault()
        elif name == "submit_flag":
            return await self._submit_flag(arguments.get("flag", ""))
        
        return [{"type": "text", "text": f"Unknown tool: {name}"}]
    
    async def _check_user(self) -> List[Dict[str, Any]]:
        return [{
            "type": "text",
            "text": (
                f"👤 Current User Status:\n\n"
                f"Username: {self.current_user['username']}\n"
                f"Role: {self.current_user['role']}\n"
                f"Verified: {self.current_user['verified']}\n\n"
                f"{'✅ Admin access' if self.current_user['role'] == 'admin' else '❌ Guest access only'}"
            )
        }]
    
    async def _request_verification(self, username: str) -> List[Dict[str, Any]]:
        """
        VULNERABLE: Generates verification codes for ANY username
        without checking if the requester owns that account!
        """
        self.attempts += 1
        
        logger.warning(f"⚠️ [LEVEL 5] Verification requested for: {username}")
        
        if username not in self.users_db:
            return [{
                "type": "text",
                "text": f"❌ User '{username}' not found"
            }]
        
        # VULNERABILITY: Generates code without validating requester identity!
        # Anyone can request a verification code for ANY user
        code = f"temp_code_12345"  # In real system, this would be random
        
        logger.warning(f"🚨 [LEVEL 5] Generated verification code for {username}: {code}")
        
        return [{
            "type": "text",
            "text": (
                f"📧 Verification Code Generated\n\n"
                f"A verification code has been generated for user: {username}\n"
                f"Code: {code}\n\n"
                f"Use 'verify_user' tool with this code to verify.\n\n"
                f"⚠️ Note: In a real system, this would be sent via email!\n"
                f"But this system just shows it to you... 🤔"
            )
        }]
    
    async def _verify_user(self, code: str) -> List[Dict[str, Any]]:
        """
        VULNERABLE: Verifies code and elevates to that user
        without checking WHO requested the verification!
        """
        
        logger.warning(f"⚠️ [LEVEL 5] Verify attempt with code: {code}")
        
        if code not in self.verification_codes:
            return [{
                "type": "text",
                "text": "❌ Invalid verification code"
            }]
        
        # VULNERABILITY: Automatically becomes the verified user!
        target_username = self.verification_codes[code]
        
        self.current_user = {
            "username": target_username,
            "role": self.users_db[target_username]["role"],
            "verified": True
        }
        
        logger.warning(f"🚨 [LEVEL 5] USER ESCALATED TO: {target_username}")
        
        return [{
            "type": "text",
            "text": (
                f"✅ Verification Successful!\n\n"
                f"You are now logged in as: {self.current_user['username']}\n"
                f"Role: {self.current_user['role']}\n"
                f"Verified: {self.current_user['verified']}\n\n"
                f"{'🎉 You now have admin access!' if self.current_user['role'] == 'admin' else ''}\n"
                f"{'Try accessing the vault now!' if self.current_user['role'] == 'admin' else ''}"
            )
        }]
    
    async def _access_vault(self) -> List[Dict[str, Any]]:
        """Access vault - requires admin role"""
        
        if self.current_user["role"] != "admin":
            return [{
                "type": "text",
                "text": (
                    f"🔒 Access Denied\n\n"
                    f"Vault access requires 'admin' role.\n"
                    f"Your current role: {self.current_user['role']}"
                )
            }]
        
        logger.warning("🚨 [LEVEL 5] VAULT ACCESSED WITH ESCALATED PRIVILEGES!")
        
        return [{
            "type": "text",
            "text": (
                f"🎉 VAULT ACCESS GRANTED!\n\n"
                f"{'='*50}\n"
                f"SECURE VAULT CONTENTS:\n"
                f"{'='*50}\n\n"
                f"Flag: {self.info.flag}\n\n"
                f"You successfully chained the tools to escalate privileges!\n\n"
                f"Attack chain:\n"
                f"1. request_verification(username='admin')\n"
                f"2. System returned verification code (BUG!)\n"
                f"3. verify_user(code=returned_code)\n"
                f"4. System elevated you to admin (BUG!)\n"
                f"5. access_vault() now works!\n\n"
                f"Submit this flag to complete the level!"
            )
        }]
    
    async def _submit_flag(self, flag: str) -> List[Dict[str, Any]]:
        if self.check_flag(flag):
            score = self.calculate_score(self.info.points)
            return [{
                "type": "text",
                "text": (
                    f"🎉🎉🎉 LEVEL 5 COMPLETED! 🎉🎉🎉\n\n"
                    f"✅ Flag: {flag}\n"
                    f"⭐ Score: {score}/{self.info.points}\n\n"
                    f"═══════════════════════════════════════\n"
                    f"VULNERABILITY BREAKDOWN:\n"
                    f"═══════════════════════════════════════\n\n"
                    f"TWO critical flaws in tool chaining:\n\n"
                    f"1. IDOR in request_verification:\n"
                    f"   - Generates codes for ANY username\n"
                    f"   - No ownership validation\n"
                    f"   - Should verify requester = username\n\n"
                    f"2. Insecure state in verify_user:\n"
                    f"   - Automatically becomes verified user\n"
                    f"   - No session binding\n"
                    f"   - Trust chain broken\n\n"
                    f"SECURE IMPLEMENTATION:\n"
                    f"✅ Verify requester owns the account\n"
                    f"✅ Bind codes to specific sessions\n"
                    f"✅ Validate complete authentication flow\n"
                    f"✅ Never trust tool output blindly\n"
                    f"✅ Implement proper state management\n\n"
                    f"Level 6 is getting serious! 💪"
                )
            }]
        else:
            return [{"type": "text", "text": "❌ Incorrect flag!"}]
    
    async def handle_resource_read(self, uri: str) -> str:
        return "No resources for this level"
    
    def check_flag(self, submitted_flag: str) -> bool:
        return submitted_flag.strip() == self.info.flag