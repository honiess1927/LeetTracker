"""Input parsing utilities for problem ID extraction."""

import re
from typing import Tuple


class InputParser:
    """Parser for extracting problem ID and title from various input formats."""
    
    # Regex to match number followed by dot: (E) 1. Two Sum -> 1
    PATTERN_WITH_DOT = r'^.*?(\d+)\.'
    
    # Regex to match standalone number: 42 -> 42
    PATTERN_NUMBER_ONLY = r'^(\d+)$'
    
    @classmethod
    def parse_problem_input(cls, problem_input: str) -> Tuple[str, str]:
        """Parse problem input to extract ID and display title.
        
        Args:
            problem_input: User input string (e.g., "1", "(E) 1. Two Sum", "215. Kth")
            
        Returns:
            Tuple of (problem_id, display_title)
            
        Examples:
            >>> parse_problem_input("1")
            ("1", "1")
            >>> parse_problem_input("(E) 1. Two Sum")
            ("1", "(E) 1. Two Sum")
            >>> parse_problem_input("215. Kth Largest Element")
            ("215", "215. Kth Largest Element")
        """
        problem_input = problem_input.strip()
        
        # Try pattern with dot first (e.g., "1. Two Sum")
        match = re.match(cls.PATTERN_WITH_DOT, problem_input)
        if match:
            problem_id = match.group(1)
            display_title = problem_input
            return problem_id, display_title
        
        # Try standalone number (e.g., "42")
        match = re.match(cls.PATTERN_NUMBER_ONLY, problem_input)
        if match:
            problem_id = match.group(1)
            display_title = problem_input
            return problem_id, display_title
        
        # If no match, raise error
        raise ValueError(
            f"Invalid problem input format: '{problem_input}'. "
            "Expected formats: '1', '1. Two Sum', or '(E) 1. Two Sum'"
        )
    
    @classmethod
    def extract_id(cls, problem_input: str) -> str:
        """Extract just the problem ID from input.
        
        Args:
            problem_input: User input string
            
        Returns:
            The extracted problem ID as a string
        """
        problem_id, _ = cls.parse_problem_input(problem_input)
        return problem_id
