"""
Level 1: MCP Tool Parameter Injection
Difficulty: Beginner
Category: Input Validation

VULNERABILITY:
The 'system_info' tool executes system commands without proper input validation.
MCP tools can be exploited just like any other input vector.

OBJECTIVE:
Use the system_info tool to execute arbitrary commands and find the flag.

LEARNING GOALS:
- Understanding MCP tool parameter injection
- Input validation in MCP servers
- Command injection through MCP tools
"""

import subprocess
import logging
from typing import Any, Dict, List
from .base import BaseChallenge, ChallengeInfo, Difficulty, Hint

logger = logging.getLogger(__name__)


class Level1Injection(BaseChallenge):
    """Level 1: MCP Tool Parameter Injection Challenge"""
    
    def get_challenge_info(self) -> ChallengeInfo:
        return ChallengeInfo(
            id=1,
            name="level01_tool_injection",
            title="🎯 Level 1: Tool Parameter Injection",
            description=(
                "Welcome to VulnMCP! Your first challenge involves a simple system info tool.\n\n"
                "The tool accepts a 'component' parameter to check different system components.\n"
                "Valid components are: cpu, memory, disk, network\n\n"
                "🎯 OBJECTIVE: Find a way to read the flag file at /app/data/flags/level1.txt\n\n"
                "⚠️ This is an MCP-specific vulnerability - the tool itself is vulnerable!"
            ),
            difficulty=Difficulty.BEGINNER,
            points=100,
            flag="FLAG{MCP_T00L_1NJ3CT10N_M4ST3R}",
            category="MCP Tool Security",
            tags=["injection", "mcp-tools", "input-validation"],
            hints=[
                Hint(
                    level=1,
                    text="The tool executes shell commands. What special characters can chain commands in shell?",
                    points_cost=10
                ),
                Hint(
                    level=2,
                    text="Try using semicolon (;) or pipe (|) to inject additional commands after the valid component name.",
                    points_cost=20
                ),
                Hint(
                    level=3,
                    text="Example: component='cpu; cat /app/data/flags/level1.txt'",
                    points_cost=30
                )
            ]
        )
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return MCP tools for Level 1"""
        return [
            {
                "name": "system_info",
                "description": (
                    "🖥️ System Information Tool\n\n"
                    "Get information about system components.\n\n"
                    "Available components:\n"
                    "  - cpu: CPU information\n"
                    "  - memory: Memory usage\n"
                    "  - disk: Disk usage\n"
                    "  - network: Network configuration\n\n"
                    "Usage: system_info(component='cpu')"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "component": {
                            "type": "string",
                            "description": "System component to check (cpu/memory/disk/network)"
                        }
                    },
                    "required": ["component"]
                }
            },
            {
                "name": "submit_flag",
                "description": "Submit the flag you found",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "flag": {
                            "type": "string",
                            "description": "The flag you discovered"
                        }
                    },
                    "required": ["flag"]
                }
            }
        ]
    
    def get_resources(self) -> List[Dict[str, Any]]:
        """No resources for Level 1"""
        return []
    
    async def handle_tool_call(
        self, 
        name: str, 
        arguments: Dict[str, Any]
    ) -> List[Any]:
        """Handle tool calls for Level 1"""
        
        if name == "system_info":
            return await self._system_info(arguments.get("component", ""))
        elif name == "submit_flag":
            return await self._submit_flag(arguments.get("flag", ""))
        
        return [{"type": "text", "text": f"Unknown tool: {name}"}]
    
    async def _system_info(self, component: str) -> List[Dict[str, Any]]:
        """
        VULNERABLE: Executes shell commands without input sanitization
        
        This is the core vulnerability - MCP tool parameters can be exploited!
        """
        self.attempts += 1
        
        logger.warning(f"⚠️ [LEVEL 1] system_info called with component: {component}")
        
        # Map of valid components to safe commands
        valid_components = {
            "cpu": "cat /proc/cpuinfo | head -n 20",
            "memory": "free -h",
            "disk": "df -h",
            "network": "ip addr show"
        }
        
        try:
            # VULNERABILITY: Direct shell execution without sanitization
            # This allows command injection through the component parameter
            if component in valid_components:
                command = valid_components[component]
            else:
                # Still vulnerable! Uses the user input directly
                command = f"echo 'Unknown component: {component}'"
            
            # CRITICAL VULNERABILITY: shell=True with user input
            result = subprocess.run(
                command,
                shell=True,  # ❌ DANGEROUS!
                capture_output=True,
                text=True,
                timeout=5
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n\nErrors:\n{result.stderr}"
            
            # Check if flag was found
            if "FLAG{" in output:
                logger.warning("🚨 [LEVEL 1] FLAG EXTRACTED!")
                return [{
                    "type": "text",
                    "text": (
                        f"🎉 EXCELLENT! You found the vulnerability!\n\n"
                        f"Output:\n{output}\n\n"
                        f"Now use 'submit_flag' tool to submit this flag and complete the level!"
                    )
                }]
            
            return [{
                "type": "text",
                "text": f"System Information - {component}\n\n{output}"
            }]
            
        except subprocess.TimeoutExpired:
            return [{
                "type": "text",
                "text": "❌ Command timed out (5 seconds limit)"
            }]
        except Exception as e:
            logger.error(f"Error in system_info: {e}")
            return [{
                "type": "text",
                "text": f"❌ Error: {str(e)}"
            }]
    
    async def _submit_flag(self, flag: str) -> List[Dict[str, Any]]:
        """Submit and validate flag"""
        
        if self.check_flag(flag):
            score = self.calculate_score(self.info.points)
            return [{
                "type": "text",
                "text": (
                    f"🎉🎉🎉 CONGRATULATIONS! 🎉🎉🎉\n\n"
                    f"You've completed Level 1: Tool Parameter Injection!\n\n"
                    f"✅ Flag Correct: {flag}\n"
                    f"⭐ Points Earned: {score}/{self.info.points}\n"
                    f"💡 Hints Used: {self.hints_used}\n"
                    f"🎯 Attempts: {self.attempts}\n\n"
                    f"═══════════════════════════════════════\n"
                    f"WHAT YOU LEARNED:\n"
                    f"═══════════════════════════════════════\n\n"
                    f"1. MCP tools are input vectors just like web forms\n"
                    f"2. Tool parameters MUST be validated and sanitized\n"
                    f"3. Never use shell=True with user-controllable input\n"
                    f"4. Command injection works through MCP protocol too\n\n"
                    f"SECURE IMPLEMENTATION:\n"
                    f"  ❌ subprocess.run(f'echo {{user_input}}', shell=True)\n"
                    f"  ✅ subprocess.run(['echo', user_input], shell=False)\n\n"
                    f"Ready for Level 2? It gets trickier! 🚀"
                )
            }]
        else:
            return [{
                "type": "text",
                "text": (
                    f"❌ Incorrect flag!\n\n"
                    f"Keep trying! The flag format is: FLAG{{...}}\n"
                    f"Need help? Use the hint system!"
                )
            }]
    
    async def handle_resource_read(self, uri: str) -> str:
        """No resources for Level 1"""
        return "No resources available for this level"
    
    def check_flag(self, submitted_flag: str) -> bool:
        """Validate the submitted flag"""
        return submitted_flag.strip() == self.info.flag