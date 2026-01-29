"""
Score and Progress Management System
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ChallengeProgress:
    """Track progress for a single challenge"""
    challenge_id: int
    completed: bool
    score: int
    attempts: int
    hints_used: int
    time_started: Optional[str]
    time_completed: Optional[str]
    best_score: int


@dataclass
class UserProgress:
    """Complete user progress"""
    username: str
    total_score: int
    challenges_completed: int
    total_attempts: int
    badges: List[str]
    challenge_progress: Dict[int, ChallengeProgress]
    started_at: str
    last_activity: str


class ScoreManager:
    """Manage scoring and progress tracking"""
    
    def __init__(self, data_dir: str = "data/progress"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_user = "player"  # Default user
        
    def get_progress_file(self, username: str) -> Path:
        """Get progress file path for user"""
        return self.data_dir / f"{username}_progress.json"
    
    def load_progress(self, username: str) -> UserProgress:
        """Load user progress from file"""
        progress_file = self.get_progress_file(username)
        
        if not progress_file.exists():
            # Create new progress
            return UserProgress(
                username=username,
                total_score=0,
                challenges_completed=0,
                total_attempts=0,
                badges=[],
                challenge_progress={},
                started_at=datetime.now().isoformat(),
                last_activity=datetime.now().isoformat()
            )
        
        try:
            with open(progress_file, 'r') as f:
                data = json.load(f)
                
            # Convert challenge_progress dict back to ChallengeProgress objects
            challenge_progress = {}
            for cid, cprog in data.get('challenge_progress', {}).items():
                challenge_progress[int(cid)] = ChallengeProgress(**cprog)
            
            data['challenge_progress'] = challenge_progress
            return UserProgress(**data)
            
        except Exception as e:
            logger.error(f"Error loading progress: {e}")
            return self.load_progress(username)  # Return fresh progress
    
    def save_progress(self, progress: UserProgress):
        """Save user progress to file"""
        progress_file = self.get_progress_file(progress.username)
        
        try:
            # Convert to dict
            data = asdict(progress)
            
            # Convert ChallengeProgress objects to dicts
            data['challenge_progress'] = {
                str(k): asdict(v) for k, v in progress.challenge_progress.items()
            }
            
            with open(progress_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Progress saved for {progress.username}")
            
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
    
    def start_challenge(self, username: str, challenge_id: int):
        """Mark challenge as started"""
        progress = self.load_progress(username)
        
        if challenge_id not in progress.challenge_progress:
            progress.challenge_progress[challenge_id] = ChallengeProgress(
                challenge_id=challenge_id,
                completed=False,
                score=0,
                attempts=0,
                hints_used=0,
                time_started=datetime.now().isoformat(),
                time_completed=None,
                best_score=0
            )
        
        progress.last_activity = datetime.now().isoformat()
        self.save_progress(progress)
    
    def record_attempt(self, username: str, challenge_id: int):
        """Record a challenge attempt"""
        progress = self.load_progress(username)
        
        if challenge_id in progress.challenge_progress:
            progress.challenge_progress[challenge_id].attempts += 1
            progress.total_attempts += 1
        
        progress.last_activity = datetime.now().isoformat()
        self.save_progress(progress)
    
    def use_hint(self, username: str, challenge_id: int, hint_level: int):
        """Record hint usage"""
        progress = self.load_progress(username)
        
        if challenge_id in progress.challenge_progress:
            progress.challenge_progress[challenge_id].hints_used += 1
        
        progress.last_activity = datetime.now().isoformat()
        self.save_progress(progress)
        
        return f"Hint {hint_level} revealed! (Cost applied to final score)"
    
    def complete_challenge(
        self, 
        username: str, 
        challenge_id: int, 
        score: int
    ) -> Dict:
        """Mark challenge as completed and update scores"""
        progress = self.load_progress(username)
        
        if challenge_id not in progress.challenge_progress:
            self.start_challenge(username, challenge_id)
        
        cprog = progress.challenge_progress[challenge_id]
        
        # Update if not completed or better score
        if not cprog.completed or score > cprog.best_score:
            if not cprog.completed:
                progress.challenges_completed += 1
                cprog.completed = True
                cprog.time_completed = datetime.now().isoformat()
            
            # Update scores
            old_score = cprog.score
            cprog.score = score
            cprog.best_score = max(cprog.best_score, score)
            
            # Update total
            progress.total_score += (score - old_score)
        
        # Award badges
        new_badges = self._check_badges(progress)
        progress.badges.extend(new_badges)
        progress.badges = list(set(progress.badges))  # Remove duplicates
        
        progress.last_activity = datetime.now().isoformat()
        self.save_progress(progress)
        
        return {
            "score": score,
            "total_score": progress.total_score,
            "new_badges": new_badges,
            "challenges_completed": progress.challenges_completed
        }
    
    def _check_badges(self, progress: UserProgress) -> List[str]:
        """Check for new badge achievements"""
        new_badges = []
        
        # First Blood
        if progress.challenges_completed == 1 and "first_blood" not in progress.badges:
            new_badges.append("first_blood")
        
        # No Hints Hero
        no_hints = all(
            cp.hints_used == 0 
            for cp in progress.challenge_progress.values() 
            if cp.completed
        )
        if no_hints and progress.challenges_completed >= 3:
            if "no_hints_hero" not in progress.badges:
                new_badges.append("no_hints_hero")
        
        # Speed Demon (completed in under 5 attempts)
        speed_demon = any(
            cp.completed and cp.attempts <= 5
            for cp in progress.challenge_progress.values()
        )
        if speed_demon and "speed_demon" not in progress.badges:
            new_badges.append("speed_demon")
        
        # Half Way There
        if progress.challenges_completed >= 4 and "halfway" not in progress.badges:
            new_badges.append("halfway")
        
        # Champion
        if progress.challenges_completed == 8 and "champion" not in progress.badges:
            new_badges.append("champion")
        
        # Perfect Score
        perfect = all(
            cp.score == cp.best_score
            for cp in progress.challenge_progress.values()
            if cp.completed
        )
        if perfect and progress.challenges_completed >= 5:
            if "perfect_score" not in progress.badges:
                new_badges.append("perfect_score")
        
        return new_badges
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top players leaderboard"""
        leaderboard = []
        
        for progress_file in self.data_dir.glob("*_progress.json"):
            try:
                with open(progress_file, 'r') as f:
                    data = json.load(f)
                    leaderboard.append({
                        "username": data["username"],
                        "total_score": data["total_score"],
                        "challenges_completed": data["challenges_completed"],
                        "badges": len(data.get("badges", []))
                    })
            except Exception as e:
                logger.error(f"Error reading {progress_file}: {e}")
        
        # Sort by score
        leaderboard.sort(key=lambda x: x["total_score"], reverse=True)
        return leaderboard[:limit]