"""Utility for parsing problem titles to extract difficulty and clean title."""

import re
from typing import Tuple, Optional


class TitleParser:
    """Parser for extracting difficulty and clean title from problem title strings."""
    
    # Pattern to match difficulty: (E), (M), (H) at the beginning
    DIFFICULTY_PATTERN = r'^\(([EMH])\)\s*'
    
    # Pattern to match "ID. Title" format
    ID_TITLE_PATTERN = r'^\d+\.\s*'
    
    @classmethod
    def parse_title(cls, title: str) -> Tuple[Optional[str], str]:
        """Parse title to extract difficulty and clean title.
        
        Args:
            title: Full title string (e.g., "(E) 1. Two Sum", "215. Kth", "42")
            
        Returns:
            Tuple of (difficulty, clean_title)
            - difficulty: "E", "M", "H", or None
            - clean_title: Title without difficulty tag or ID prefix
            
        Examples:
            >>> parse_title("(E) 1. Two Sum")
            ("E", "Two Sum")
            >>> parse_title("215. Kth Largest Element")
            (None, "Kth Largest Element")
            >>> parse_title("42")
            (None, "42")
        """
        if not title:
            return None, "N/A"
        
        clean_title = title.strip()
        difficulty = None
        
        # Extract difficulty if present
        match = re.match(cls.DIFFICULTY_PATTERN, clean_title)
        if match:
            difficulty = match.group(1)
            # Remove difficulty tag from title
            clean_title = re.sub(cls.DIFFICULTY_PATTERN, '', clean_title)
        
        # Remove "ID. " prefix if present
        clean_title = re.sub(cls.ID_TITLE_PATTERN, '', clean_title)
        
        # If after cleaning we're left with nothing, use original
        if not clean_title.strip():
            clean_title = title
        
        return difficulty, clean_title.strip()
    
    @classmethod
    def format_difficulty(cls, difficulty: Optional[str]) -> str:
        """Format difficulty for display.
        
        Args:
            difficulty: "E", "M", "H", or None
            
        Returns:
            Formatted string with color coding
        """
        if difficulty == "E":
            return "[green]E[/green]"
        elif difficulty == "M":
            return "[yellow]M[/yellow]"
        elif difficulty == "H":
            return "[red]H[/red]"
        else:
            return "[dim]-[/dim]"
    
    @staticmethod
    def difficulty_to_letter(difficulty: Optional[str]) -> Optional[str]:
        """Convert full difficulty name to single letter.
        
        Args:
            difficulty: Full difficulty name ("Easy", "Medium", "Hard") or letter ("E", "M", "H")
            
        Returns:
            Single letter: "E", "M", "H", or None
            
        Examples:
            >>> difficulty_to_letter("Easy")
            "E"
            >>> difficulty_to_letter("M")
            "M"
            >>> difficulty_to_letter(None)
            None
        """
        if not difficulty:
            return None
        
        # If already a letter, return as-is
        if difficulty in ("E", "M", "H"):
            return difficulty
        
        # Convert full name to letter
        mapping = {
            "Easy": "E",
            "Medium": "M",
            "Hard": "H"
        }
        return mapping.get(difficulty)
