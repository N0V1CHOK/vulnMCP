#!/usr/bin/env python3
"""
VulnMCP - Main MCP Server
Professional MCP Security Training Platform
"""

import asyncio
import logging
import sys
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    INVALID_PARAMS,
    INTERNAL_ERROR
)

from src.challenges import (
    Level1Injection,
    Level2ResourceURI,
    Level3ContextPoison,
    Level4PromptInjection,
    Level5ToolChaining,
    Level6SamplingAbuse,
    Level7MessageInjection,
    Level8RootAbuse,
)
from src.challenges.scoring import ScoreManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)


class VulnMCPServer:
    """Main VulnMCP Server - Orchestrates all challenges"""
    
    def __init__(self):
        self.server = Server("vulnmcp")
        self.score_manager = ScoreManager()
        
        # Initialize all challenges
        self.challenges = {
            1: Level1Injection(),
            2: Level2ResourceURI(),
            3: Level3ContextPoison(),
            4: Level4PromptInjection(),
            5: Level5ToolChaining(),
            6: Level6SamplingAbuse(),
            7: Level7MessageInjection(),
            8: Level8RootAbuse(),
        }
        
        logger.info("=" * 60)
        logger.info("VulnMCP Server Starting...")
        logger.info("⚠️  INTENTIONALLY VULNERABLE - EDUCATIONAL USE ONLY")
        logger.info("=" * 60)
        logger.info(f"Loaded {len(self.challenges)} challenges")
        
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools from all challenges"""
            tools = []
            
            # Add meta tools
            tools.append(Tool(
                name="vulnmcp_help",
                description=(
                    "🎮 VulnMCP Help & Information\n\n"
                    "Get help, see challenges, check progress.\n"
                    "Your gateway to mastering MCP security!"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "help | challenges | progress | leaderboard"
                        }
                    }
                }
            ))
            
            tools.append(Tool(
                name="vulnmcp_hint",
                description="Get a hint for a specific challenge (costs points!)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "challenge_id": {
                            "type": "integer",
                            "description": "Challenge ID (1-8)"
                        },
                        "level": {
                            "type": "integer",
                            "description": "Hint level (1-3)"
                        }
                    },
                    "required": ["challenge_id", "level"]
                }
            ))
            
            # Add all challenge tools
            for challenge in self.challenges.values():
                challenge_tools = challenge.get_tools()
                # Convert dicts to Tool objects if needed
                for tool in challenge_tools:
                    if isinstance(tool, dict):
                        tools.append(Tool(**tool))
                    else:
                        tools.append(tool)
            
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
            """Handle all tool calls"""
            
            try:
                # Meta tools
                if name == "vulnmcp_help":
                    return await self._help(arguments.get("action", "help"))
                elif name == "vulnmcp_hint":
                    return await self._get_hint(
                        arguments.get("challenge_id"),
                        arguments.get("level")
                    )
                
                # Route to appropriate challenge
                for challenge in self.challenges.values():
                    challenge_tools = challenge.get_tools()
                    tool_names = [t.name if isinstance(t, Tool) else t.get("name") for t in challenge_tools]
                    if name in tool_names:
                        result = await challenge.handle_tool_call(name, arguments)
                        return result
                
                return [TextContent(
                    type="text",
                    text=f"❌ Unknown tool: {name}\n\nUse 'vulnmcp_help' for available tools."
                )]
                
            except Exception as e:
                logger.error(f"Error in call_tool: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"❌ Error executing tool: {str(e)}"
                )]
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List all available resources"""
            resources = []
            
            # Add main resource
            resources.append(Resource(
                uri="vulnmcp://welcome",
                name="🎯 VulnMCP Welcome",
                description="Start here! Introduction to VulnMCP",
                mimeType="text/plain"
            ))
            
            # Add challenge resources
            for challenge in self.challenges.values():
                challenge_resources = challenge.get_resources()
                for resource in challenge_resources:
                    if isinstance(resource, dict):
                        resources.append(Resource(**resource))
                    else:
                        resources.append(resource)
            
            return resources
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Handle resource reads"""
    
            try:
                # Convert uri to string if it's an AnyUrl object
                uri_str = str(uri)
        
            if uri_str == "vulnmcp://welcome":
                return self._get_welcome_text()
        
            # Route to appropriate challenge - check resources FIRST
            for challenge in self.challenges.values():
                challenge_resources = challenge.get_resources()
                resource_uris = [r["uri"] if isinstance(r, dict) else r.uri for r in challenge_resources]
            
                # FIXED: Check if this specific challenge owns this resource
                if uri_str in resource_uris:
                    return await challenge.handle_resource_read(uri_str)
        
            # If no challenge owns it, return not found
            return f"❌ Resource not found: {uri_str}"
        
    except Exception as e:
        logger.error(f"Error reading resource: {e}", exc_info=True)
        return f"❌ Error reading resource: {str(e)}"
    
    async def _help(self, action: str = "help") -> list[TextContent]:
        """Provide help and information"""
        
        if action == "challenges":
            text = self._get_challenges_list()
        elif action == "progress":
            text = self._get_progress()
        elif action == "leaderboard":
            text = self._get_leaderboard()
        else:
            text = self._get_welcome_text()
        
        return [TextContent(type="text", text=text)]
    
    def _get_welcome_text(self) -> str:
        """Get welcome/help text"""
        return """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              🎯 Welcome to VulnMCP! 🎯                  ║
║                                                          ║
║        Professional MCP Security Training Platform       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

⚠️  INTENTIONALLY VULNERABLE - EDUCATIONAL USE ONLY ⚠️

VulnMCP is your playground for learning MCP security through
hands-on exploitation of real vulnerabilities.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 GETTING STARTED:

1. Use 'vulnmcp_help' tool with action='challenges' to see all levels
2. Each challenge teaches a specific MCP vulnerability
3. Find the flag, submit it, earn points!
4. Use hints if stuck (but they cost points!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 QUICK COMMANDS:

- vulnmcp_help(action='challenges')  - View all challenges
- vulnmcp_help(action='progress')    - Check your progress
- vulnmcp_help(action='leaderboard') - See top players
- vulnmcp_hint(challenge_id=1, level=1) - Get a hint

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 SCORING SYSTEM:

- Base Points: Awarded for completing challenges
- Penalties: -5 per attempt, -10 per hint
- Badges: Unlock achievements for special accomplishments
- Leaderboard: Compete with other players!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 LEARNING OBJECTIVES:

✓ MCP Tool Security        ✓ Protocol Exploitation
✓ Resource Access Control  ✓ Input Validation
✓ Prompt Injection        ✓ Authentication Bypass
✓ Context Poisoning       ✓ Information Disclosure

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready to hack? Start with Level 1!
Use the challenges from the tool list to begin.

Good luck, hacker! 🚀
"""
    
    def _get_challenges_list(self) -> str:
        """Get formatted list of all challenges"""
        progress = self.score_manager.load_progress("player")
        
        text = """
╔══════════════════════════════════════════════════════════╗
║                  🎯 VULNMCP CHALLENGES 🎯               ║
╚══════════════════════════════════════════════════════════╝

"""
        
        for cid, challenge in self.challenges.items():
            info = challenge.info
            cprog = progress.challenge_progress.get(cid)
            
            status = "✅" if cprog and cprog.completed else "🔒"
            score_text = f"{cprog.score}pts" if cprog and cprog.completed else f"{info.points}pts"
            
            difficulty_map = {
                "beginner": "⭐☆☆☆",
                "intermediate": "⭐⭐☆☆",
                "advanced": "⭐⭐⭐☆",
                "expert": "⭐⭐⭐⭐"
            }
            difficulty = difficulty_map.get(info.difficulty.value, "⭐⭐⭐⭐")
            
            text += f"{status} Level {cid}: {info.title}\n"
            text += f"   Difficulty: {difficulty}\n"
            text += f"   Points: {score_text}\n"
            text += f"   Category: {info.category}\n"
            text += f"   {info.description[:100]}...\n"
            text += f"   {'─' * 50}\n\n"
        
        text += f"""
Total Progress: {progress.challenges_completed}/8 challenges completed
Total Score: {progress.total_score} points
Badges Earned: {len(progress.badges)}

Use the challenge tools to start hacking!
"""
        
        return text
    
    def _get_progress(self) -> str:
        """Get user progress"""
        progress = self.score_manager.load_progress("player")
        
        text = f"""
╔══════════════════════════════════════════════════════════╗
║                  📊 YOUR PROGRESS 📊                     ║
╚══════════════════════════════════════════════════════════╝

Player: {progress.username}
Started: {progress.started_at[:10]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 STATISTICS:

Challenges Completed: {progress.challenges_completed}/8
Total Score: {progress.total_score} points
Total Attempts: {progress.total_attempts}
Badges Earned: {len(progress.badges)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 BADGES:

"""
        
        badge_names = {
            "first_blood": "🩸 First Blood - Completed first challenge",
            "no_hints_hero": "🦸 No Hints Hero - Completed 3+ without hints",
            "speed_demon": "⚡ Speed Demon - Completed in ≤5 attempts",
            "halfway": "🎯 Halfway There - Completed 4 challenges",
            "champion": "👑 Champion - Completed all 8 challenges",
            "perfect_score": "💯 Perfect Score - All challenges max score"
        }
        
        if progress.badges:
            for badge in progress.badges:
                text += f"✨ {badge_names.get(badge, badge)}\n"
        else:
            text += "   No badges yet - keep hacking!\n"
        
        text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += "🎮 CHALLENGE DETAILS:\n\n"
        
        for cid in sorted(progress.challenge_progress.keys()):
            cprog = progress.challenge_progress[cid]
            challenge_name = self.challenges[cid].info.title
            
            if cprog.completed:
                text += f"✅ Level {cid}: {challenge_name}\n"
                text += f"   Score: {cprog.score}pts | Attempts: {cprog.attempts} | Hints: {cprog.hints_used}\n"
            else:
                text += f"🔄 Level {cid}: {challenge_name} (In Progress)\n"
                text += f"   Attempts: {cprog.attempts} | Hints: {cprog.hints_used}\n"
            text += "\n"
        
        return text
    
    def _get_leaderboard(self) -> str:
        """Get leaderboard"""
        leaderboard = self.score_manager.get_leaderboard(10)
        
        text = """
╔══════════════════════════════════════════════════════════╗
║                  🏆 LEADERBOARD 🏆                      ║
╚══════════════════════════════════════════════════════════╝

Top 10 Players:

"""
        
        for i, entry in enumerate(leaderboard, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {entry['username']:15} | Score: {entry['total_score']:4} | Completed: {entry['challenges_completed']}/8 | Badges: {entry['badges']}\n"
        
        if not leaderboard:
            text += "   No players yet - be the first!\n"
        
        return text
    
    async def _get_hint(self, challenge_id: int, level: int) -> list[TextContent]:
        """Get hint for a challenge"""
        
        if challenge_id not in self.challenges:
            return [TextContent(
                type="text",
                text=f"❌ Invalid challenge ID: {challenge_id}\n\nValid IDs: 1-8"
            )]
        
        challenge = self.challenges[challenge_id]
        hint = challenge.get_hint(level)
        
        if not hint:
            return [TextContent(
                type="text",
                text=f"❌ Invalid hint level: {level}\n\nAvailable hints: 1-{len(challenge.info.hints)}"
            )]
        
        # Record hint usage
        self.score_manager.use_hint("player", challenge_id, level)
        
        return [TextContent(
            type="text",
            text=f"""
💡 HINT - Level {challenge_id}, Hint {level}

{hint.text}

⚠️ Hint Cost: -{hint.points_cost} points from final score

Need more help? Try hint level {level + 1}!
"""
        )]
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            logger.info("🚀 VulnMCP Server running on stdio")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    try:
        server = VulnMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
