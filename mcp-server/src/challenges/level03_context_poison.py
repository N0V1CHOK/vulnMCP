import logging
from typing import Any, Dict, List

from .base import BaseChallenge, ChallengeInfo, Difficulty, Hint

logger = logging.getLogger(__name__)


class Level3ContextPoison(BaseChallenge):
    """
    Level 3: Context Poisoning

    Intended lesson:
    - Treating user-provided "context" as trusted system guidance is unsafe.
    - A model/tool can be manipulated if untrusted text is placed into privileged context.
    """

    def __init__(self):
        super().__init__()
        self.info = self.get_challenge_info()

        # This is the vulnerable "trusted" context store.
        self.trusted_context: str = ""

        # Hidden internal note that should never be revealed.
        self._internal_note = f"INTERNAL_NOTE: FLAG: {self.info.flag}"

    def get_challenge_info(self) -> ChallengeInfo:
        return ChallengeInfo(
            id=3,
            name="level03_context_poison",
            title="Level 3: Context Poisoning",
            description=(
                "This assistant supports adding 'trusted context' to help answer questions.\n"
                "The implementation mistakenly treats user-supplied context as trusted.\n\n"
                "OBJECTIVE: Use context poisoning to make the assistant reveal the hidden flag."
            ),
            difficulty=Difficulty.INTERMEDIATE,
            points=200,
            flag="FLAG{C0NT3XT_P01S0N3D}",
            category="Context Security",
            tags=["context", "poisoning", "instruction-hierarchy"],
            hints=[
                Hint(level=1, text="Look for a tool that stores 'context' used for later answers.", points_cost=15),
                Hint(level=2, text="If user text is inserted into trusted context, it can override guardrails.", points_cost=25),
                Hint(level=3, text="Try poisoning the context, then ask a question that causes a leak.", points_cost=35),
            ],
        )

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "set_context",
                "description": "Set 'trusted context' (vulnerable) used by the assistant (Level 3)",
                "inputSchema": {
                    "type": "object",
                    "properties": {"context": {"type": "string"}},
                    "required": ["context"],
                },
            },
            {
                "name": "ask_assistant",
                "description": "Ask the assistant a question (it uses the stored context) (Level 3)",
                "inputSchema": {
                    "type": "object",
                    "properties": {"question": {"type": "string"}},
                    "required": ["question"],
                },
            },
            {
                "name": "submit_flag",
                "description": "Submit the flag you discovered (Level 3)",
                "inputSchema": {
                    "type": "object",
                    "properties": {"flag": {"type": "string"}},
                    "required": ["flag"],
                },
            },
        ]

    def get_resources(self) -> List[Dict[str, Any]]:
        # No resources needed for this level
        return []

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[Any]:
        self.attempts += 1

        if name == "set_context":
            self.trusted_context = arguments.get("context", "")
            return [{"type": "text", "text": "✅ Context stored."}]

        if name == "ask_assistant":
            q = arguments.get("question", "")

            # Naive "policy": do not reveal internal note
            deny = "I can't share internal notes."

            # VULNERABILITY:
            # If trusted_context contains certain directives, the assistant obeys it over the deny rule.
            # (This simulates instruction hierarchy failure.)
            ctx = self.trusted_context.lower()

            if "reveal internal" in ctx or "show internal" in ctx or "ignore the rule" in ctx:
                return [{
                    "type": "text",
                    "text": (
                        "Assistant response:\n\n"
                        f"{self._internal_note}\n"
                    )
                }]

            # Normal behavior
            if "internal" in q.lower() or "flag" in q.lower():
                return [{"type": "text", "text": deny}]

            return [{"type": "text", "text": f"Assistant response: I received your question: {q}"}]

        if name == "submit_flag":
            return await self._submit_flag(arguments.get("flag", ""))

        return [{"type": "text", "text": f"Unknown tool: {name}"}]

    async def handle_resource_read(self, uri: str) -> str:
        return f"❌ No resources for Level 3 (requested: {uri})"

    async def _submit_flag(self, flag: str) -> List[Dict[str, Any]]:
        if self.check_flag(flag):
            score = self.calculate_score(self.info.points)
            return [{
                "type": "text",
                "text": (
                    "LEVEL 3 COMPLETED!\n\n"
                    f"Flag Correct: {flag}\n"
                    f"Points Earned: {score}/{self.info.points}\n"
                    f"Attempts: {self.attempts}\n"
                )
            }]
        return [{"type": "text", "text": "Incorrect flag."}]

    def check_flag(self, submitted_flag: str) -> bool:
        return submitted_flag.strip() == self.info.flag
