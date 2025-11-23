"""Coding interview session service."""
import random
import json
from typing import List, Dict, Any, Optional

from services.feedback_service import generate_coding_feedback


class CodingSession:
    """Manages a coding interview session with multiple problem rounds."""
    
    def __init__(self, role: str, rounds: int = 2):
        """
        Initialize a coding session.
        
        Args:
            role: Position/role being interviewed for
            rounds: Number of coding problems to present
        """
        self.role = role
        self.current_round = 0
        self.rounds = rounds
        self.history: List[Dict[str, Any]] = []
        self.explanation_history: List[str] = []
        self.meta = {} 
        self.round_type = "Coding" 

        # Load problems from JSON file
        try:
            with open("problems.json", "r") as f:
                self.all_problems = json.load(f)
            # Shuffle to randomize order and avoid repeats
            self.randomized_problems = random.sample(self.all_problems, len(self.all_problems))
        except FileNotFoundError:
            print("Warning: problems.json not found")
            self.all_problems = []
            self.randomized_problems = []

    def get_next_problem(self) -> Optional[Dict[str, Any]]:
        """
        Get the next coding problem.
        
        Returns:
            Next problem or None if rounds complete
        """
        print(f"[DEBUG] CodingSession: round {self.current_round} / {self.rounds}")
        
        # Check if rounds are finished or we ran out of problems
        if self.current_round >= self.rounds or self.current_round >= len(self.randomized_problems):
            return None

        # 1. Get the raw problem data
        problem = self.randomized_problems[self.current_round]
        
        # 2. 🔥 ADDED: Generate the Spoken Introduction (The "Explanation")
        # This text is sent to the frontend to be spoken by the AI.
        # It reads the question and asks for approach, strictly avoiding solutions.
        q_num = self.current_round + 1
        title = problem.get('title', 'Coding Challenge')
        description = problem.get('description', 'No description available.')

        intro_text = (
            f"Okay, let's move on to question number {q_num}. "
            f"The problem is titled: {title}. "
            f"Here is the problem statement: {description} "
            "Take a moment to process that. "
            "Before you start typing any code, please explain your approach to me verbally. "
            "I want to hear your logic first."
        )

        # 3. Create a response copy to attach the intro without mutating original data
        problem_response = problem.copy()
        problem_response['spoken_intro'] = intro_text

        # 4. Update state
        self.current_round += 1
        self.history.append({"problem": problem, "code": ""})
        
        return problem_response

    def submit_solution(self, code: str) -> None:
        """
        Submit solution code for current problem.
        
        Args:
            code: Solution code submitted by candidate
        """
        if self.history:
            self.history[-1]["code"] = code

    def generate_feedback(self) -> Dict[str, Any]:
        """
        Generate feedback on coding solutions.
        
        Returns:
            Dictionary with feedback scores and comments
        """
        return generate_coding_feedback(self.history)