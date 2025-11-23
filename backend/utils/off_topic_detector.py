"""Off-topic detection utility for interviews."""
import re
from typing import Dict, Tuple, List


class OffTopicDetector:
    """Detects and handles off-topic user responses."""
    
    # Keywords that indicate off-topic responses
    OFF_TOPIC_KEYWORDS = {
        'personal': [
            'do you', 'your name', 'how old', 'where are you from', 
            'married', 'kids', 'girlfriend', 'boyfriend', 'family',
            'where do you live', 'tell me about you', 'what do you do',
            'how are things', 'weather', 'weekend', 'vacation'
        ],
        'social': [
            'coffee', 'lunch', 'dinner', 'drinks', 'party',
            'hangout', 'fun', 'joke', 'meme', 'funny',
            'sports', 'games', 'movie', 'music', 'tv show'
        ],
        'unrelated': [
            'salary', 'benefits', 'stock options', 'bonus',
            'remote work', 'work from home', 'vacation days',
            'dress code', 'office location', 'commute',
            'company culture', 'team size', 'management'
        ],
        'inappropriate': [
            'politics', 'religion', 'controversial',
            'complain about company', 'complain about people'
        ]
    }
    
    # Question keywords that are typically on-topic
    ON_TOPIC_KEYWORDS = {
        'technical': [
            'algorithm', 'data structure', 'database', 'api',
            'design', 'architecture', 'scalability', 'performance',
            'optimization', 'complexity', 'code', 'test', 'bug',
            'framework', 'library', 'language', 'system', 'network'
        ],
        'behavioral': [
            'experience', 'project', 'team', 'conflict', 'challenge',
            'problem', 'solution', 'approach', 'learned', 'worked',
            'contributed', 'responsibility', 'achievement', 'timeline'
        ],
        'sales': [
            'deal', 'client', 'customer', 'sale', 'pitch',
            'objection', 'close', 'target', 'quota', 'territory',
            'product', 'competitor', 'strategy', 'commission'
        ]
    }
    
    def __init__(self, interview_type: str = "technical"):
        """
        Initialize detector.
        
        Args:
            interview_type: Type of interview (technical, behavioral, sales, hr)
        """
        self.interview_type = interview_type.lower()
        self.off_topic_count = 0
        self.redirect_count = 0
    
    def detect_off_topic(self, user_answer: str, question: str) -> Tuple[bool, str]:
        """
        Detect if user answer is off-topic from the question.
        
        Args:
            user_answer: User's response text
            question: The interview question asked
            
        Returns:
            Tuple of (is_off_topic: bool, reason: str)
        """
        answer_lower = user_answer.lower().strip()
        question_lower = question.lower().strip()
        
        # Check 1: Empty or very short response (likely off-topic)
        if len(answer_lower) < 10:
            return True, "response_too_short"
        
        # Check 2: Asking counter-questions instead of answering
        if self._is_asking_questions(answer_lower):
            return True, "asking_counter_questions"
        
        # Check 3: Personal/social questions
        if self._contains_personal_questions(answer_lower):
            return True, "personal_questions"
        
        # Check 4: Unrelated company questions (should ask recruiter)
        if self._contains_company_logistics(answer_lower):
            return True, "company_logistics"
        
        # Check 5: Relevant keywords match
        if not self._has_relevant_keywords(answer_lower):
            return True, "lacks_relevant_keywords"
        
        # Check 6: Answer doesn't relate to question context
        if not self._answer_relates_to_question(answer_lower, question_lower):
            return True, "answer_unrelated_to_question"
        
        return False, "on_topic"
    
    def _is_asking_questions(self, text: str) -> bool:
        """Check if response is asking questions instead of answering."""
        question_patterns = [
            r'^\s*do you\s',
            r'^\s*can you\s',
            r'^\s*what\s',
            r'^\s*how\s',
            r'^\s*where\s',
            r'^\s*when\s',
            r'^\s*why\s',
            r'\?\s*$'  # Ends with question mark
        ]
        
        question_count = sum(1 for pattern in question_patterns if re.search(pattern, text, re.IGNORECASE))
        return question_count >= 2
    
    def _contains_personal_questions(self, text: str) -> bool:
        """Check if response contains personal/social questions."""
        for keyword in self.OFF_TOPIC_KEYWORDS['personal'] + self.OFF_TOPIC_KEYWORDS['social']:
            if keyword in text:
                return True
        return False
    
    def _contains_company_logistics(self, text: str) -> bool:
        """Check if response asks about company logistics/benefits."""
        for keyword in self.OFF_TOPIC_KEYWORDS['unrelated']:
            if keyword in text:
                return True
        return False
    
    def _has_relevant_keywords(self, text: str) -> bool:
        """Check if response has keywords relevant to interview type."""
        if self.interview_type == "technical":
            keywords = self.ON_TOPIC_KEYWORDS['technical']
        elif self.interview_type == "sales":
            keywords = self.ON_TOPIC_KEYWORDS['sales']
        elif self.interview_type in ["behavioral", "hr"]:
            keywords = self.ON_TOPIC_KEYWORDS['behavioral']
        else:
            return True  # Allow if unknown type
        
        relevant_count = sum(1 for keyword in keywords if keyword in text)
        return relevant_count >= 1
    
    def _answer_relates_to_question(self, answer: str, question: str) -> bool:
        """Check if answer has common words with question (simple relevance check)."""
        # Extract important words (ignore common words)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'do', 'does', 'did'}
        
        question_words = set(word for word in question.split() 
                           if len(word) > 3 and word.lower() not in stop_words)
        answer_words = set(word for word in answer.split() 
                         if len(word) > 3 and word.lower() not in stop_words)
        
        # Check for word overlap
        overlap = question_words & answer_words
        return len(overlap) >= 1 or len(question_words) == 0  # Allow if no specific words in Q
    
    def get_redirect_message(self, reason: str) -> str:
        """
        Get appropriate redirect message based on off-topic reason.
        
        Args:
            reason: Reason for off-topic detection
            
        Returns:
            Redirect message to send to candidate
        """
        messages = {
            "response_too_short": 
                "I appreciate the brief response. Could you provide more details and examples to help me understand your experience better?",
            
            "asking_counter_questions":
                "Those are interesting questions! I appreciate your curiosity. Let's focus on the interview for now - let me ask you that question again and I'd love to hear your thoughts.",
            
            "personal_questions":
                "Those are nice questions, but they're a bit outside the scope of this technical interview. Let's stay focused on assessing your professional skills. Could we get back to the question?",
            
            "company_logistics":
                "Great questions about the company! Those are definitely important, and I'd recommend discussing those with our recruiter. Right now, let's focus on the technical assessment.",
            
            "lacks_relevant_keywords":
                "I notice your answer doesn't quite address the question I asked. Could you please focus on answering the specific question I posed? Let me rephrase it for clarity.",
            
            "answer_unrelated_to_question":
                "I appreciate your response, but it seems to drift from what I asked. Let me ask you more clearly: [Question]. Can you provide an answer that directly addresses this?"
        }
        
        return messages.get(reason, 
            "Could you please refocus your answer on the question at hand? Let me ask again.")
    
    def should_give_warning(self) -> bool:
        """
        Determine if we should give a stronger redirect warning.
        
        Returns:
            True if multiple off-topic responses detected
        """
        self.off_topic_count += 1
        return self.off_topic_count >= 2  # Warn after 2 off-topic responses
    
    def get_warning_message(self) -> str:
        """Get warning message for repeated off-topic responses."""
        return ("I notice we're getting a bit off track. This is a technical interview, " 
                "so let's please stick to questions about your technical skills, experience, "
                "and problem-solving approach. Let's try the next question.")


def detect_and_respond_to_offtopic(
    user_answer: str,
    question: str,
    interview_type: str = "technical"
) -> Dict[str, any]:
    """
    Main function to detect off-topic and get response.
    
    Args:
        user_answer: User's response
        question: Interview question asked
        interview_type: Type of interview
        
    Returns:
        Dictionary with:
        - is_off_topic: bool
        - reason: str (reason for off-topic)
        - response: str (message to send back to user)
        - should_warn: bool (if warning needed)
    """
    detector = OffTopicDetector(interview_type)
    
    is_off_topic, reason = detector.detect_off_topic(user_answer, question)
    
    if not is_off_topic:
        return {
            "is_off_topic": False,
            "reason": "on_topic",
            "response": None,
            "should_warn": False
        }
    
    response = detector.get_redirect_message(reason)
    should_warn = detector.should_give_warning()
    
    if should_warn:
        response = detector.get_warning_message()
    
    return {
        "is_off_topic": True,
        "reason": reason,
        "response": response,
        "should_warn": should_warn
    }
