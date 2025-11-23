"""Coding interview session service."""
import random
import json
from typing import List, Dict, Any, Optional

from services.feedback_service import generate_coding_feedback
from utils.coding_constraints import sanitize_coding_response, create_coding_prompt_constraint


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

    def generate_guidance_question(self, candidate_answer: str) -> Optional[str]:
        """
        Generate a Socratic/guiding question for the candidate without giving away the solution.
        
        Args:
            candidate_answer: Candidate's approach or answer
            
        Returns:
            Guided question or None
        """
        from config import llm
        from langchain_core.messages import SystemMessage, HumanMessage
        
        if not self.history:
            return None
        
        current_problem = self.history[-1]["problem"]
        problem_title = current_problem.get("title", "Problem")
        problem_desc = current_problem.get("description", "")
        
        guidance_prompt = f"""Based on the candidate's approach to this coding problem, generate ONE Socratic question to guide them deeper WITHOUT giving away the solution.

Problem: {problem_title}
Description: {problem_desc}

Candidate said: "{candidate_answer}"

Generate a single thought-provoking question that:
- Helps them think deeper about the problem
- Makes them reconsider edge cases or constraints
- Guides them to discover patterns themselves
- Never reveals the solution, algorithm, or data structure to use

Keep it short (1-2 sentences) and Socratic in nature."""

        response = llm.invoke([
            SystemMessage(content=create_coding_prompt_constraint()),
            HumanMessage(content=guidance_prompt)
        ]).content
        
        # Sanitize to ensure no hints slipped through
        sanitized_response, has_violation = sanitize_coding_response(response)
        
        if has_violation:
            # Fallback to generic Socratic questions if LLM violated constraints
            generic_questions = [
                "Let's break this down further. What's the smallest example of this problem?",
                "Good thinking. Now, what information do you need to track to solve this?",
                "That's a valid start. What happens with edge cases or larger inputs?",
                "I like where you're going. What would you need to compare or evaluate?",
                "Keep exploring. What pattern do you see if you walk through a few examples?",
                "Interesting approach. What would be the most challenging part to implement?",
            ]
            import random
            return random.choice(generic_questions)
        
        return sanitized_response