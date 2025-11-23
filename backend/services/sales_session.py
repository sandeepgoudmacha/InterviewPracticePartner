"""Sales interview session service."""
from typing import Dict, Any, List, Optional

from utils.vector_memory import VectorMemory
from services.feedback_service import generate_sales_feedback
from config import llm
from langchain_core.messages import SystemMessage, HumanMessage


class SalesInterviewSession:
    """Sales Representative interview session with specialized rounds."""
    
    def __init__(self, role: str, session_id: str, round_type: str = "hiring_manager", rounds: int = 3):
        """
        Initialize Sales interview session.
        
        Args:
            role: Sales position being interviewed for
            session_id: Unique session identifier
            round_type: Interview round type ('hiring_manager' or 'senior_leadership')
            rounds: Number of sales questions to ask
        """
        self.role = role
        self.session_id = session_id
        self.round_type = round_type
        self.current_round = 0
        self.rounds = rounds
        self.meta = {}
        self.vector_memory = VectorMemory()
        self.skipped_questions: List[str] = []  # Track skipped questions
        self.skip_count = 0  # Track number of skips
        
        # Set initial greeting based on round type
        if round_type == "hiring_manager":
            greeting = "Welcome to the Sales Interview, Hiring Manager Interview. Ready to begin?"
        else:
            greeting = "Welcome to the Sales Interview,Senior Leadership Interview. Let's get started!"
        
        self.history: List[Dict[str, Optional[str]]] = [{"question": greeting, "answer": None}]

    def ask_question(self) -> Optional[str]:
        """
        Generate specialized sales interview questions based on round type.
        
        Returns:
            Next question or None if rounds complete
        """
        if self.current_round >= self.rounds:
            return None
        
        # Different prompts for each round type
        if self.round_type == "hiring_manager":
            system_prompt = """You are an experienced sales hiring manager conducting a behavioral interview. 
Generate a medium but fair question that evaluates:
- Sales process and methodology
- Past performance and achievements
- How they handle objections and rejection
- Customer relationship management
- Closing techniques
- Experience with different sales stages
NOTE: Ask a small and concise question. very short and to the point.
NOTE: Dont always mention this is an behavioral question, ask a small and concise question.

Ask ONE specific behavioral question that requires a detailed answer. Reference real scenarios they've faced.
Keep it conversational and professional."""
        else:  # senior_leadership
            system_prompt = """You are a VP/Senior Leader conducting the final round of sales interview.
Generate a strategic question that evaluates:
- Leadership and team collaboration
- Vision alignment with company
- Long-term career goals in sales
- Ability to mentor or manage teams
- Strategic thinking about market and competition
- Cultural fit with the organization

NOTE:
    dont always mention this is an senior leadership or strategic question, ask a small and concise question.

Ask ONE strategic question that helps assess their fit at a senior level.
Keep it conversational and forward-looking."""
        
        question = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Generate a sales interview question for {self.role} role. This is question {self.current_round + 1} of {self.rounds}.")
        ]).content
        
        self.history.append({"question": question, "answer": None})
        self.current_round += 1
        return question

    def provide_answer(self, answer: str) -> None:
        """
        Record candidate's answer and store in memory.
        
        Args:
            answer: Candidate's response
        """
        if self.history:
            self.history[-1]["answer"] = answer
            # Store Q&A in vector memory for later analysis
            if len(self.history) > 1:
                last_qa = self.history[-1]
                self.vector_memory.add_qa(last_qa.get("question", ""), answer)

    def generate_followup_question(self, previous_answer: str) -> Optional[str]:
        """
        Generate intelligent follow-up question based on candidate's answer.
        
        Args:
            previous_answer: The candidate's previous answer
            
        Returns:
            Follow-up question or None
        """
        if len(self.history) < 2:
            return None
        
        last_qa = self.history[-1] if self.history else None
        if not last_qa or not last_qa.get("answer"):
            return None
        
        if self.round_type == "hiring_manager":
            followup_prompt = f"""Based on the candidate's response about their sales experience, generate ONE deep-dive follow-up question.

Original Question: {last_qa['question']}
Candidate's Answer: {previous_answer}

Generate a follow-up that:
- Probes deeper into specific tactics or results
- Asks for concrete numbers or metrics if not provided
- Explores how they overcame objections or challenges
- Seeks real examples with outcomes

Keep it conversational (1-2 sentences)."""
        else:
            followup_prompt = f"""Based on the candidate's response about their vision and leadership, generate ONE insightful follow-up question.

Original Question: {last_qa['question']}
Candidate's Answer: {previous_answer}

Generate a follow-up that:
- Explores deeper strategic thinking
- Asks about team or company impact
- Probes their alignment with our values
- Seeks specific examples of leadership or growth

Keep it conversational (1-2 sentences)."""
        
        followup_question = llm.invoke([
            SystemMessage(content="You are an expert sales interviewer generating follow-up questions."),
            HumanMessage(content=followup_prompt)
        ]).content
        
        return followup_question

    def skip_question(self) -> Dict[str, Any]:
        """
        Allow candidate to skip the current question and move to the next one.
        
        Returns:
            Dictionary with skip confirmation and next question
        """
        current_question = self.history[-1]['question']
        
        # Mark as skipped
        self.skipped_questions.append(current_question)
        self.skip_count += 1
        self.history[-1]['answer'] = "[SKIPPED]"
        self.current_round += 1
        
        # Track skip in meta
        if "skipped_questions" not in self.meta:
            self.meta["skipped_questions"] = []
        self.meta["skipped_questions"].append({
            "question": current_question,
            "skipped_at_round": self.current_round
        })
        
        # Get next question
        if self.current_round < self.rounds:
            next_q = self.ask_question()
            return {
                "status": "skipped",
                "skipped_count": self.skip_count,
                "message": f"Question skipped. Moving to next question.",
                "next_question": next_q
            }
        else:
            return {
                "status": "skipped",
                "skipped_count": self.skip_count,
                "message": f"All {self.round_type} questions completed.",
                "next_question": None,
                "round_complete": True
            }


    def is_complete(self) -> bool:
        """Check if this round is complete."""
        return self.current_round >= self.rounds

    def generate_feedback(self) -> Dict[str, Any]:
        """Generate sales interview feedback."""
        return generate_sales_feedback(self.history)
