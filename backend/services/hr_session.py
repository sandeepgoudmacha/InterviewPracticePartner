"""HR interview session service."""
from typing import Dict, Any, List, Optional

from chains.hr_interview_chain import hr_memory_chain
from services.feedback_service import generate_hr_feedback
from config import llm
from langchain_core.messages import SystemMessage, HumanMessage


class HRInterviewSession:
    """Manages an HR/behavioral interview session."""
    
    def __init__(self, role: str, session_id: str, rounds: int = 3):
        """
        Initialize HR interview session.
        
        Args:
            role: Position being interviewed for
            session_id: Unique session identifier
            rounds: Number of HR questions to ask
        """
        self.role = role
        self.session_id = session_id
        self.current_round = 0
        self.rounds = rounds
        self.meta = {} 
        self.round_type = "HR"
        self.history: List[Dict[str, Optional[str]]] = [
            {"question": "Welcome to the HR round of your interview. Tell me about your strengths and weaknesses.", "answer": None}
        ]

    def ask_question(self) -> Optional[str]:
        """
        Ask next HR interview question.
        
        Returns:
            Next question or None if rounds complete
        """
        if self.current_round >= self.rounds:
            return None

        question = hr_memory_chain.invoke(
            {"role": self.role},
            config={"configurable": {"session_id": self.session_id}}
        ).content

        self.history.append({"question": question, "answer": None})
        self.current_round += 1
        return question

    def provide_answer(self, answer: str) -> None:
        """
        Record candidate's answer.
        
        Args:
            answer: Candidate's response
        """
        if self.history:
            self.history[-1]["answer"] = answer

    def generate_followup_question(self, previous_answer: str) -> Optional[str]:
        """
        Generate an intelligent follow-up question based on the candidate's HR answer.
        
        Args:
            previous_answer: The candidate's previous answer
            
        Returns:
            Follow-up question or None
        """
        if len(self.history) < 2:
            return None
        
        last_qa = self.history[-1] if self.history else None
        if not last_qa or not last_qa.get('answer'):
            return None
        
        followup_prompt = f"""Based on the candidate's response to the HR/behavioral interview question, generate ONE relevant follow-up question.

Role: {self.role}
Last Question: {last_qa['question']}
Candidate's Answer: {previous_answer}

Generate a natural follow-up question that:
- Explores deeper into their experience or motivation
- Asks for specific examples if they didn't provide any
- Investigates their problem-solving or teamwork approach
- Is conversational and direct (1-2 sentences)

Respond with ONLY the follow-up question, nothing else."""
        
        followup_question = llm.invoke([
            SystemMessage(content="You are an experienced HR interviewer generating follow-up questions to understand candidate behavior and soft skills better."),
            HumanMessage(content=followup_prompt)
        ]).content
        
        return followup_question

    def generate_feedback(self) -> Dict[str, Any]:
        """Generate HR interview feedback."""
        return generate_hr_feedback(self.history)
