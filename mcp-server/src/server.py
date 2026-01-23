#!/usr/bin/env python3
"""
VulnMCP - Main MCP Server
Professional MCP Security Training Platform
"""

import asyncio
import logging
import sys
from typing import Any, Sequence, Dict, Tuple, Optional
from urllib.parse import urlparse

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource

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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


class VulnMCPServer:
    """Main VulnMCP Server - Orchestrates all challenges"""

    def __init__(self):
        self.server = Server("vulnmcp")
        self.score_manager = ScoreManager()

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

        # Build tool registry (namespaced) to avoid collisions across challenges
        self._tool_registry: Dict[str, Tuple[int, str]] = {}
        self._unique_tool_registry: Dict[str, Tuple[int, str]] = {}
        self._namespaced_tools: list[Tool] = []
        self._build_tool_registry()

        # Build resource owner map for dynamic routing by (scheme, netloc)
        self._resource_owner: Dict[Tuple[str, str], Optional[int]] = {}
        self._build_resource_owner_map()

        self._register_handlers()

    def _build_tool_registry(self) -> None:
        # gather all tools per challenge
        name_counts: Dict[str, int] = {}
        per_challenge_tools: Dict[int, list[Tool]] = {}

        for cid, challenge in self.challenges.items():
            tools: list[Tool] = []
            for t in challenge.get_tools():
                if isinstance(t, dict):
                    tools.append(Tool(**t))
                else:
                    tools.append(t)
            per_challenge_tools[cid] = tools
            for t in tools:
                name_counts[t.name] = name_counts.get(t.name, 0) + 1

        # expose: namespaced tools always
        # expose: original tool name only if globally unique
        for cid, tools in per_challenge_tools.items():
            for t in tools:
                ns_name = f"lvl{cid}__{t.name}"
                self._tool_registry[ns_name] = (cid, t.name)
                self._namespaced_tools.append(
                    Tool(
                        name=ns_name,
                        description=t.description,
                        inputSchema=t.inputSchema,
                    )
                )

                if name_counts.get(t.name, 0) == 1:
                    self._unique_tool_registry[t.name] = (cid, t.name)

    def _build_resource_owner_map(self) -> None:
        # If multiple challenges declare the same (scheme, netloc), mark as ambiguous (None).
        for cid, challenge in self.challenges.items():
            for r in challenge.get_resources():
                uri = r["uri"] if isinstance(r, dict) else r.uri
                p = urlparse(uri)
                key = (p.scheme, p.netloc)
                if key in self._resource_owner and self._resource_owner[key] != cid:
                    self._resource_owner[key] = None
                else:
                    self._resource_owner[key] = cid

        # Ensure Level 2 dynamic routing works for vulnmcp://docs/...
        self._resource_owner[("vulnmcp", "docs")] = 2

    def _register_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            tools: list[Tool] = []

            tools.append(
                Tool(
                    name="vulnmcp_help",
                    description=(
                        "🎮 VulnMCP Help & Information\n\n"
                        "Get help, see challenges, check progress.\n"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "help | challenges | progress | leaderboard",
                            }
                        },
                    },
                )
            )

            tools.append(
                Tool(
                    name="vulnmcp_hint",
                    description="Get a hint for a specific challenge (costs points!)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "challenge_id": {"type": "integer", "description": "Challenge ID (1-8)"},
                            "level": {"type": "integer", "description": "Hint level (1-3)"},
                        },
                        "required": ["challenge_id", "level"],
                    },
                )
            )

            # Namespaced tools (no collisions)
            tools.extend(self._namespaced_tools)

            # Also expose globally-unique original tool names for convenience
            # (no collisions, so safe)
            for name, (cid, orig) in sorted(self._unique_tool_registry.items(), key=lambda x: x[0]):
                # Find original Tool object to preserve its description/schema
                challenge = self.challenges[cid]
                for t in challenge.get_tools():
                    t_obj = Tool(**t) if isinstance(t, dict) else t
                    if t_obj.name == name:
                        tools.append(t_obj)
                        break

            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
            try:
                if name == "vulnmcp_help":
                    return await self._help(arguments.get("action", "help"))
                if name == "vulnmcp_hint":
                    return await self._get_hint(arguments.get("challenge_id"), arguments.get("level"))

                # namespaced
                if name in self._tool_registry:
                    cid, orig_name = self._tool_registry[name]
                    return await self.challenges[cid].handle_tool_call(orig_name, arguments)

                # unique original
                if name in self._unique_tool_registry:
                    cid, orig_name = self._unique_tool_registry[name]
                    return await self.challenges[cid].handle_tool_call(orig_name, arguments)

                return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]

            except Exception as e:
                logger.error(f"Error in call_tool: {e}", exc_info=True)
                return [TextContent(type="text", text=f"❌ Error executing tool: {str(e)}")]

        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            resources: list[Resource] = []

            resources.append(
                Resource(
                    uri="vulnmcp://welcome",
                    name="🎯 VulnMCP Welcome",
                    description="Start here! Introduction to VulnMCP",
                    mimeType="text/plain",
                )
            )

            for challenge in self.challenges.values():
                for r in challenge.get_resources():
                    resources.append(Resource(**r) if isinstance(r, dict) else r)

            return resources

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            try:
                uri_str = str(uri)

                if uri_str == "vulnmcp://welcome":
                    return self._get_welcome_text()

                # Exact-match routing first (safe)
                for challenge in self.challenges.values():
                    resource_uris = [
                        rr["uri"] if isinstance(rr, dict) else rr.uri
                        for rr in challenge.get_resources()
                    ]
                    if uri_str in resource_uris:
                        return await challenge.handle_resource_read(uri_str)

                # Dynamic routing by (scheme, netloc) owner (for challenges that need it)
                p = urlparse(uri_str)
                owner = self._resource_owner.get((p.scheme, p.netloc))
                if owner is not None:
                    return await self.challenges[owner].handle_resource_read(uri_str)

                return f"❌ Resource not found: {uri_str}"

            except Exception as e:
                logger.error(f"Error reading resource: {e}", exc_info=True)
                return f"❌ Error reading resource: {str(e)}"

    async def _help(self, action: str = "help") -> list[TextContent]:
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
        return "Welcome to VulnMCP! Use vulnmcp_help(action='challenges') to start."

    def _get_challenges_list(self) -> str:
        progress = self.score_manager.load_progress("player")
        text = "VULNMCP CHALLENGES\n\n"
        for cid, challenge in self.challenges.items():
            info = challenge.info
            status = "✅" if progress.challenge_progress.get(cid, None) and progress.challenge_progress[cid].completed else "🔒"
            text += f"{status} Level {cid}: {info.title} ({info.points}pts)\n"
        return text

    def _get_progress(self) -> str:
        progress = self.score_manager.load_progress("player")
        return (
            f"Player: {progress.username}\n"
            f"Completed: {progress.challenges_completed}/8\n"
            f"Score: {progress.total_score}\n"
        )

    def _get_leaderboard(self) -> str:
        leaderboard = self.score_manager.get_leaderboard(10)
        if not leaderboard:
            return "No players yet."
        lines = ["Top Players:"]
        for i, e in enumerate(leaderboard, 1):
            lines.append(f"{i}. {e['username']} - {e['total_score']} pts ({e['challenges_completed']}/8)")
        return "\n".join(lines)

    async def _get_hint(self, challenge_id: int, level: int) -> list[TextContent]:
        if challenge_id not in self.challenges:
            return [TextContent(type="text", text=f"❌ Invalid challenge ID: {challenge_id}")]
        challenge = self.challenges[challenge_id]
        hint = challenge.get_hint(level)
        if not hint:
            return [TextContent(type="text", text=f"❌ Invalid hint level: {level}")]
        self.score_manager.use_hint("player", challenge_id, level)
        return [TextContent(type="text", text=f"💡 HINT L{challenge_id}.{level}\n\n{hint.text}")]

    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            logger.info("🚀 VulnMCP Server running on stdio")
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


async def main():
    server = VulnMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
