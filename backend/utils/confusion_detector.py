"""Confusion detection and adaptive guidance system."""
import re
from typing import Dict, Any, Tuple


class ConfusionDetector:
    """Detects and handles confused candidates during interviews."""
    
    # Patterns indicating confusion
    CONFUSION_PATTERNS = {
        'uncertainty': [
            r"i'm not sure", r"i don't know", r"not certain", r"unsure",
            r"confused", r"what do you mean", r"can you clarify", r"could you explain",
            r"don't understand", r"lost", r"not familiar", r"never heard",
            r"hmm", r"um", r"uh", r"err", r"i'm lost"
        ],
        'clarification_request': [
            r"could you|can you|would you.*clarif", r"what.*mean", r"what.*asking",
            r"are you asking", r"do you mean", r"specifically", r"exactly",
            r"give me an example", r"break it down", r"simpler"
        ],
        'rambling': [
            r".*\.{3}.*", r"anyway|but like|sort of|kind of|i guess",
            r"maybe|perhaps|possibly|might", r"multiple sentences without structure"
        ],
        'lack_of_specifics': [
            r"something|stuff|things|whatever", r"i think|probably|maybe",
            r"not sure if", r"vague|general|roughly"
        ]
    }
    
    @staticmethod
    def detect_confusion(answer: str, question: str) -> Tuple[bool, str, float]:
        """
        Detect if candidate is confused.
        
        Args:
            answer: Candidate's answer
            question: The question asked
            
        Returns:
            Tuple of (is_confused, confusion_type, confidence_score)
        """
        if not answer or len(answer.strip()) < 5:
            return True, "empty_answer", 0.95
        
        answer_lower = answer.lower()
        confusion_score = 0.0
        confusion_type = "not_confused"
        
        # Check for uncertainty patterns
        for pattern in ConfusionDetector.CONFUSION_PATTERNS['uncertainty']:
            if re.search(pattern, answer_lower):
                confusion_score += 0.3
                confusion_type = "uncertain"
        
        # Check for clarification requests
        for pattern in ConfusionDetector.CONFUSION_PATTERNS['clarification_request']:
            if re.search(pattern, answer_lower):
                confusion_score += 0.25
                confusion_type = "needs_clarification"
        
        # Check for rambling/lack of structure
        for pattern in ConfusionDetector.CONFUSION_PATTERNS['rambling']:
            if re.search(pattern, answer_lower):
                confusion_score += 0.2
                confusion_type = "rambling"
        
        # Check for lack of specifics
        for pattern in ConfusionDetector.CONFUSION_PATTERNS['lack_of_specifics']:
            if re.search(pattern, answer_lower):
                confusion_score += 0.15
                confusion_type = "lacks_specifics"
        
        # Length check - very short answers might indicate confusion
        words = len(answer.split())
        if words < 10:
            confusion_score += 0.1
        
        is_confused = confusion_score >= 0.4
        
        return is_confused, confusion_type, min(confusion_score, 1.0)
    
    @staticmethod
    def generate_guidance(
        confusion_type: str,
        question: str,
        previous_answer: str = ""
    ) -> str:
        """
        Generate adaptive guidance based on confusion type.
        
        Args:
            confusion_type: Type of confusion detected
            question: The original question
            previous_answer: Candidate's previous answer
            
        Returns:
            Guidance message to help the candidate
        """
        guidance_map = {
            "empty_answer": f"""I notice you didn't provide much detail. Let me help you think through this:

The question was: "{question}"

To give a strong answer, try to include:
1. A specific situation or example from your experience
2. What the challenge or problem was
3. What action you took
4. What the result was (ideally with metrics)

Can you try again with more details?""",
            
            "uncertain": f"""I see you're uncertain about this. That's okay! Let me clarify the question for you:

Original question: "{question}"

Let me break it down:
- Think about your past experience
- Focus on what YOU did specifically
- Talk about the approach or methodology
- Mention the outcome or what you learned

There's no single "right" answer here - I want to understand your thinking process and approach.""",
            
            "needs_clarification": f"""Great question! Let me clarify what I'm asking:

"{question}"

When I ask this, I'm looking for:
1. A real example from your background (work, projects, or learning)
2. Your specific role and contribution
3. The challenge you faced
4. Your solution or approach
5. The results or what you took away from it

Does that help? What's a specific instance you can think of?""",
            
            "rambling": f"""I notice your answer is a bit scattered. Let me help you structure it better:

For the question "{question}", try this structure:
1. Start with the situation/problem
2. Explain what YOU specifically did
3. Share the result or outcome
4. Keep it concise (30-60 seconds)

Can you give me a more focused answer following this structure?""",
            
            "lacks_specifics": f"""Your answer is a bit general. Let me help you add specifics:

Instead of general statements, try to include:
- Actual numbers/metrics (e.g., "improved performance by 40%")
- Specific technology names (e.g., "used Redis caching" vs "used a cache")
- Concrete examples (e.g., name of project or company)
- Measurable outcomes

For "{question}", can you share specific details about what you did?""",
            
            "not_confused": "Great! Your answer shows good understanding. Let me dig deeper..."
        }
        
        return guidance_map.get(confusion_type, guidance_map["uncertain"])
    
    @staticmethod
    def generate_followup_guidance(
        question: str,
        confusion_history: list = None
    ) -> str:
        """
        Generate follow-up guidance if candidate is still confused.
        
        Args:
            question: The current question
            confusion_history: List of previous confusion detections
            
        Returns:
            Progressively simplified guidance
        """
        if not confusion_history:
            confusion_history = []
        
        confusion_count = len(confusion_history)
        
        if confusion_count == 0:
            return "Let me rephrase that question to make it clearer for you."
        elif confusion_count == 1:
            return f"""I understand this is a tricky question. Let me simplify it:

Instead of thinking about the whole question, focus on just ONE specific example 
from your experience. What's something you've worked on recently that's relevant?"""
        else:
            return f"""Let me approach this differently. Instead of asking about 
your approach in general, can you walk me through a specific project or problem 
you solved? Just tell me: What was the problem, what did you do, and what happened?

That's all I need - a simple story from your experience."""

    @staticmethod
    def should_provide_example(confusion_type: str, confusion_score: float) -> bool:
        """
        Determine if AI should provide an example to help.
        
        Args:
            confusion_type: Type of confusion
            confusion_score: Confidence score of confusion
            
        Returns:
            Whether to provide an example
        """
        return confusion_score >= 0.6 or confusion_type in [
            "needs_clarification",
            "rambling",
            "lacks_specifics"
        ]

    @staticmethod
    def generate_example(question: str, role: str) -> str:
        """
        Generate a sanitized example to help confused candidate.
        
        Args:
            question: The interview question
            role: The role being interviewed for
            
        Returns:
            Example answer (WITHOUT solution if technical question)
        """
        examples = {
            "SDE": {
                "design": """Here's how I'd structure my answer:
"I designed a notification system that needed to handle 50K+ concurrent users.
First, I understood requirements: low latency, high availability, multiple channels.
Then I chose a tech stack: Redis for messaging, PostgreSQL for storage, WebSockets for delivery.
I made trade-offs between consistency and performance, and the result was 99.9% uptime."

Notice: I explained the PROCESS, not just the outcome.""",
                
                "optimization": """Example structure:
"I found a slow database query taking 2 seconds. I analyzed the query plan,
identified missing indexes, and added one. Testing showed 10x improvement.
I also set up monitoring to catch similar issues early."

See how I: identified the problem, explained my thinking, showed metrics.""",
                
                "problem": """Example structure:
"We had a production incident where user updates weren't syncing. 
I debugged by checking logs, found the issue was a race condition in the queue,
fixed it by adding proper locking, and prevented future issues with unit tests."

Structure: Problem → Investigation → Solution → Prevention"""
            },
            "Sales": {
                "deal": """Example structure:
"A prospect was hesitant about pricing. I listened to their concerns first,
understood their actual needs, showed how we saved similar companies money,
and offered a pilot program. They signed a $50K contract within 2 weeks."

Notice: I focused on THEIR needs first, not pushing the sale.""",
                
                "objection": """Example structure:
"When told 'Your competitor is cheaper', I acknowledged it's true,
then shifted to value: 'Yes, but we include X, Y, Z which saves you 100 hours/year.'
They appreciated the honest answer and signed on."

Structure: Acknowledge → Reframe → Show Value"""
            }
        }
        
        # Return a generic example if role-specific not found
        return examples.get(role, {}).get(
            "general",
            "Think of a real situation where you had to solve a problem. Just walk through what happened."
        )

