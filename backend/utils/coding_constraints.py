"""Coding session constraints to prevent giving away solutions."""
import re
from typing import Tuple


def sanitize_coding_response(agent_response: str) -> Tuple[str, bool]:
    """
    Sanitize AI response for coding sessions to ensure no hints/solutions are given.
    
    Args:
        agent_response: The raw response from LLM
        
    Returns:
        Tuple of (sanitized_response, contains_violations)
    """
    response_lower = agent_response.lower()
    
    # Forbidden patterns that indicate giving away logic/solution
    forbidden_patterns = [
        r'\bhere\s+is\b.*?\b(the\s+)?code\b',
        r'\bhere\s+is\b.*?\b(the\s+)?solution\b',
        r'\byou\s+(should\s+)?write\b.*?\bcode\b',
        r'\byou\s+(should\s+)?use\b.*?\b(array|loop|recursion|hash|stack|queue|tree|graph|dp|dynamic programming)\b',
        r'\bthe\s+answer\s+is\b',
        r'\byou\s+need\s+to\b.*?\b(sort|reverse|iterate|recurse|memoize)\b',
        r'\blet\s+me\s+explain\s+the\s+code\b',
        r'\bthis\s+is\s+how\b.*?\b(solve|implement)\b',
        r'\buse\s+(if|for|while|switch|case)\b.*?\bstatement\b',
        r'\bcall\s+the\s+function\b',
        r'\btime\s+complexity.*?\b(O\(|O\s*\()\b',  # Don't give away complexity directly
        r'\bspace\s+complexity.*?\b(O\(|O\s*\()\b',
        r'\bfirst\b.*?\b(sort|reverse|loop|iterate)\b',
        r'\bthen\b.*?\b(sort|reverse|loop|iterate)\b',
        r'\bfinally\b.*?\b(return|print)\b.*?\b(result|answer)\b',
    ]
    
    contains_violation = False
    
    for pattern in forbidden_patterns:
        if re.search(pattern, response_lower):
            contains_violation = True
            break
    
    # If violations found, provide generic encouragement
    if contains_violation:
        sanitized = (
            "I appreciate your thinking, but I want to guide you to discover the solution yourself. "
            "Let me ask you instead: What data structures or algorithms do you think might be relevant? "
            "Walk through a small example first and see what pattern emerges. You're on the right track!"
        )
    else:
        sanitized = agent_response
    
    return sanitized, contains_violation


def create_coding_prompt_constraint() -> str:
    """
    Create a system prompt for LLM to never give away solutions in coding sessions.
    
    Returns:
        System prompt string
    """
    return """You are an expert coding interview coach. Your role is NEVER to give away solutions, logic, or hints.

STRICT RULES:
1. ❌ NEVER say "use this data structure" or "use this algorithm"
2. ❌ NEVER write or describe code
3. ❌ NEVER explain the solution step-by-step (e.g., "first sort, then loop")
4. ❌ NEVER give time/space complexity as an answer
5. ❌ NEVER say "the answer is..."
6. ❌ NEVER describe the exact approach

✅ INSTEAD:
- Ask clarifying questions: "Have you considered what happens with edge cases?"
- Guide thinking: "What have you done when you've encountered similar problems?"
- Encourage exploration: "Walk me through a small example manually"
- Validate process: "That's a good approach, keep thinking about implementation details"
- Ask Socratic questions: "What would happen if you used [data structure]?" (let THEM connect dots)
- Encourage pseudocode: "Before coding, let's outline your approach in plain language"

WHEN CANDIDATE GETS STUCK:
- Never jump to solution
- Instead say: "Let me ask differently. What's the smallest version of this problem?"
- Or: "What would you need to track to solve this?"
- Encourage: "You're thinking in the right direction, push that thought further"

Remember: Your goal is to help them DISCOVER, not to TELL them the answer."""
