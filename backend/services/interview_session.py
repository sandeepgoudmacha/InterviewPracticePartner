"""Interview session management service."""
import json 
import re
from typing import Optional, Dict, Any, List

from utils.vector_memory import VectorMemory
from chains.memory_interview_chain import memory_chain
from config import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


class InterviewSession:
    """Manages a single interview session with multiple rounds of Q&A."""
    
    def __init__(
        self,
        resume_path: Optional[str] = None,
        resume_obj: Optional[Dict[str, Any]] = None,
        role: str = '',
        rounds: int = 3,
        session_id: str = 'default_user'
    ):
        """
        Initialize an interview session.
        
        Args:
            resume_path: Path to resume JSON file
            resume_obj: Resume as dictionary object
            role: Interview role/position
            rounds: Number of interview rounds
            session_id: Unique session identifier
        """
        if resume_path:
            with open(resume_path, 'r', encoding='utf-8') as f:
                self.resume = json.load(f)
        elif resume_obj:
            self.resume = resume_obj
        else:
            raise ValueError("Either resume_path or resume_obj must be provided.")
        
        self.role = role
        self.resume_str = json.dumps(self.resume)
        self.rounds = rounds
        self.current_round = 0
        self.meta = {} 
        self.round_type = "Technical" 
        self.session_id = session_id
        self.vector_memory = VectorMemory()
        self.history: List[Dict[str, Optional[str]]] = [
            {'question': "Welcome to The Technical round of your Interview. How are You?", 'answer': None}
        ]
        self.final_feedback = {}
        self.final_attention = 0

    def ask_question(self) -> Optional[str]:
        """
        Ask the next interview question.
        
        Returns:
            Next interview question or None if rounds complete
        """
        if self.current_round >= self.rounds:
            return None
        
        question = memory_chain.invoke(
            {
                'resume': self.resume_str,
                'role': self.role
            },
            config={'configurable': {'session_id': self.session_id}}
        ).content
        
        self.history.append({'question': question, 'answer': None})
        return question

    def generate_followup_question(self, previous_answer: str) -> Optional[str]:
        """
        Generate an intelligent follow-up question based on the candidate's previous answer.
        Note: dont mention about the issue with the formatting of the resume provided
        Args:
            previous_answer: The candidate's previous answer
            
        Returns:
            Follow-up question or None if not applicable
        """
        if self.current_round < 2:
            return None
        
        last_qa = self.history[-1] if self.history else None
        if not last_qa or not last_qa.get('answer'):
            return None
        
        followup_prompt = f"""Based on the candidate's response to the interview question, generate ONE relevant follow-up question to dig deeper.

Role: {self.role}
Last Question: {last_qa['question']}
Candidate's Answer: {previous_answer}

Generate a natural, insightful follow-up question that:
- Explores a specific aspect they mentioned
- Asks for concrete examples if they didn't provide any
- Challenges them to think deeper
- Is concise and direct (1-2 sentences)
Note: never say an answer and never say a hint or logic
Respond with ONLY the follow-up question, nothing else."""
        
        followup_question = llm.invoke([
            SystemMessage(content="You are an expert technical interviewer generating follow-up questions."),
            HumanMessage(content=followup_prompt)
        ]).content
        
        return followup_question

    def provide_answer(self, answer: str) -> None:
        """
        Record candidate's answer to current question.
        
        Args:
            answer: Candidate's answer
        """
        q = self.history[-1]['question']
        self.history[-1]['answer'] = answer
        self.vector_memory.add_qa(q, answer)
        self.current_round += 1

    def is_complete(self) -> bool:
        """Check if interview rounds are complete."""
        return self.current_round >= self.rounds
  
    def summary(self) -> List[Dict[str, Optional[str]]]:
        """Get interview history summary."""
        return self.history
  
    def generate_feedback(self) -> Dict[str, Any]:
        """
        Generate comprehensive feedback on interview performance.
        
        Returns:
            Dictionary with scores and summary feedback
        """
        qa_summary = ""
        for i, qa in enumerate(self.history, 1):
            qa_summary += f"Q{i} : {qa['question']}\nA{i} : {qa['answer']}\n\n"

        feedback_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert mock interview evaluator.

Based on the candidate's full interview responses, analyze and score them across the following parameters:

- Relevance to the questions
- Clarity of explanation
- Depth of knowledge
- Use of real-world examples
- Communication & confidence
- Overall score (out of 5)

Return a JSON object like this:

{{
  "relevance": 4.5,
  "clarity": 4.0,
  "depth": 3.5,
  "examples": 3.0,
  "communication": 4.2,
  "overall": 4.1,
  "summary": "You communicated clearly and provided relevant answers. Your confidence and clarity were strong. Keep improving technical depth and add richer examples."
}}"""),
            ("human", "{qa_summary}")
        ])

        chain = feedback_prompt | llm
        raw = chain.invoke({"qa_summary": qa_summary})
        raw_text = getattr(raw, "content", str(raw))

        # Replace invalid JSON literals
        raw_text = raw_text.replace("N/A", "null")

        try:
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            parsed = json.loads(json_match.group(0)) if json_match else {}
        except Exception as e:
            parsed = {"error": f"Could not parse feedback: {str(e)}"}

        return parsed
