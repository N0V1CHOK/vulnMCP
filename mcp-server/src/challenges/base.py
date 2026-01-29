"""
Base Challenge Class for VulnMCP
All challenges inherit from this
"""

from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class Difficulty(Enum):
    """Challenge difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class Hint:
    """Hint data structure"""
    level: int
    text: str
    points_cost: int


@dataclass
class ChallengeInfo:
    """Challenge metadata"""
    id: int
    name: str
    title: str
    description: str
    difficulty: Difficulty
    points: int
    flag: str
    category: str
    tags: List[str]
    hints: List[Hint]


class BaseChallenge(ABC):
    """Base class for all VulnMCP challenges"""
    
    def __init__(self):
        self.info = self.get_challenge_info()
        self.attempts = 0
        self.hints_used = 0
    
    @abstractmethod
    def get_challenge_info(self) -> ChallengeInfo:
        """Return challenge metadata"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return MCP tools for this challenge"""
        pass
    
    @abstractmethod
    def get_resources(self) -> List[Dict[str, Any]]:
        """Return MCP resources for this challenge"""
        pass
    
    @abstractmethod
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[Any]:
        """Handle tool execution"""
        pass
    
    @abstractmethod
    async def handle_resource_read(self, uri: str) -> str:
        """Handle resource reading"""
        pass
    
    @abstractmethod
    def check_flag(self, submitted_flag: str) -> bool:
        """Validate submitted flag"""
        pass
    
    def get_hint(self, level: int) -> Optional[Hint]:
        """Get hint at specified level"""
        if level <= len(self.info.hints):
            self.hints_used += 1
            return self.info.hints[level - 1]
        return None
    
    def calculate_score(self, base_points: int) -> int:
        """Calculate final score based on attempts and hints used"""
        penalty = (self.attempts * 5) + (self.hints_used * 10)
        return max(base_points - penalty, base_points // 4)