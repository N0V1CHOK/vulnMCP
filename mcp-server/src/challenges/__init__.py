"""VulnMCP Challenge Modules"""

from .base import BaseChallenge, ChallengeInfo, Difficulty, Hint
from .level01_tool_injection import Level1Injection
from .level02_resource_uri import Level2ResourceURI
from .level03_context_poison import Level3ContextPoison
from .level04_prompt_injection import Level4PromptInjection
from .level05_tool_chaining import Level5ToolChaining
from .level06_sampling_abuse import Level6SamplingAbuse
from .level07_message_injection import Level7MessageInjection
from .level08_root_abuse import Level8RootAbuse

__all__ = [
    "BaseChallenge",
    "ChallengeInfo",
    "Difficulty",
    "Hint",
    "Level1Injection",
    "Level2ResourceURI",
    "Level3ContextPoison",
    "Level4PromptInjection",
    "Level5ToolChaining",
    "Level6SamplingAbuse",
    "Level7MessageInjection",
    "Level8RootAbuse",
]