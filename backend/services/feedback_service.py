"""Feedback generation service for interviews."""
import json
import re
from typing import List, Dict, Any

from langchain_core.prompts import PromptTemplate
from config import llm, code_llm

# 🔥 HELPER: Robust JSON Cleaner
def clean_json_text(text: str) -> str:
    """
    Removes Markdown code blocks and extra text to extract valid JSON.
    """
    try:
        # 1. Remove ```json and ``` wrappers
        if "```" in text:
            text = re.sub(r"```json\s*", "", text)
            text = re.sub(r"```\s*", "", text)
        
        # 2. Find the content between the first '{' and the last '}'
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start != -1 and end != -1:
            return text[start:end]
        
        return text.strip()
    except Exception:
        return text


def generate_hr_feedback(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate feedback for HR/behavioral interview.
    
    Args:
        history: List of Q&A dictionaries with 'question' and 'answer' keys
        
    Returns:
        Dictionary with feedback scores and summary
    """
    transcript = "\n".join(
        [f"Q: {item['question']}\nA: {item['answer']}" for item in history if item.get('answer')]
    )

    prompt = PromptTemplate(
        input_variables=["transcript"],
        template="""
You are an expert HR recruiter. Evaluate the following behavioral interview transcript:

{transcript}

Based on the candidate's responses, score them across:

- Relevance to the questions
- Clarity of explanation
- Depth of knowledge
- Use of real-world examples
- Communication & confidence
- Overall impression

Respond **only** with a well-formatted JSON object like this:

{{
  "relevance": 4.5,
  "clarity": 4.0,
  "depth": 3.5,
  "examples": 3.0,
  "communication": 4.2,
  "overall": 4.1,
  "summary": "Your answers were clear and relevant, with good communication. You could deepen your examples for impact."
}}
"""
    )

    chain = prompt | llm
    raw_output = chain.invoke({"transcript": transcript}).content

    try:
        # 🔥 FIX: Clean before parsing
        cleaned_output = clean_json_text(raw_output)
        feedback = json.loads(cleaned_output)
    except Exception as e:
        print(f"HR Feedback Error: {e}")
        feedback = {
            "relevance": 0,
            "clarity": 0,
            "depth": 0,
            "examples": 0,
            "communication": 0,
            "overall": 0,
            "summary": "Feedback generation failed. Please retry or check LLM response."
        }

    return feedback


def generate_sales_feedback(
    history: List[Dict[str, Any]],
    round_type: str = "hiring_manager"
) -> Dict[str, Any]:
    """
    Generate feedback for Sales Representative interview.
    
    Args:
        history: List of Q&A dictionaries
        round_type: Either "hiring_manager" or "senior_leadership"
        
    Returns:
        Dictionary with sales-specific feedback scores
    """
    transcript = "\n".join(
        [f"Q: {item['question']}\nA: {item['answer']}" for item in history if item.get('answer')]
    )

    round_label = "Hiring Manager Round" if round_type == "hiring_manager" else "Senior Leadership Round"

    prompt = PromptTemplate(
        input_variables=["transcript", "round_label"],
        template="""
You are an expert sales manager and interviewer. Evaluate the following {round_label} sales interview transcript:

{transcript}

Based on the candidate's responses, score them across:

- Sales Acumen: Knowledge of sales processes, techniques, and industry
- Communication: Clarity, persuasiveness, and articulation
- Problem Solving: Ability to handle objections and challenges
- Examples & Metrics: Use of concrete examples and quantifiable results
- Overall impression

Respond **only** with a well-formatted JSON object like this:

{{
  "sales_acumen": 4.5,
  "communication": 4.0,
  "problem_solving": 3.5,
  "examples": 3.0,
  "overall": 4.1,
  "summary": "Strong sales background with clear communication. You demonstrated good problem-solving skills."
}}
"""
    )

    chain = prompt | llm
    raw_output = chain.invoke({"transcript": transcript, "round_label": round_label}).content

    try:
        # 🔥 FIX: Clean before parsing
        cleaned_output = clean_json_text(raw_output)
        feedback = json.loads(cleaned_output)
    except Exception as e:
        print(f"Sales Feedback Error: {e}")
        feedback = {
            "sales_acumen": 0,
            "communication": 0,
            "problem_solving": 0,
            "examples": 0,
            "overall": 0,
            "summary": "Feedback generation failed. Please retry or check LLM response."
        }

    return feedback


def generate_coding_feedback(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate feedback for coding interview solutions.
    
    Args:
        history: List of coding problem submissions
        
    Returns:
        Dictionary with code quality feedback
    """
    latest = history[-1] if history else {}

    problem = latest.get("problem", {})
    code = latest.get("code", "")

    # Fallback if no code
    if not code or code.strip() == "":
        print("⚠️ No code submitted")
        return {
            "correctness": 0, "clarity": 0, "edge_cases": 0, 
            "efficiency": 0, "overall": 0, 
            "summary": "No code submitted."
        }

    # Debug logging
    print(f"📝 Generating feedback for: {problem.get('title', 'Unknown')}")
    print(f"📝 Code length: {len(code)} chars")
    print(f"📝 Problem keys: {list(problem.keys())}")

    prompt = PromptTemplate(
        input_variables=["description", "function_signature", "code"],
        template="""
You are a senior software engineer evaluating a candidate's coding submission.

Problem:
{description}

Function Signature:
{function_signature}

Candidate's Code:
{code}

Evaluate the solution on:

- Correctness
- Code clarity
- Edge case handling
- Time & space complexity
- Overall quality (0 to 5)

Respond only with a JSON object like:

{{
  "correctness": 4.5,
  "clarity": 4.2,
  "edge_cases": 3.8,
  "efficiency": 4.0,
  "overall": 4.1,
  "summary": "The code solves the problem and is mostly clean. Could improve edge case handling and comments."
}}
"""
    )

    chain = prompt | code_llm
    try:
        raw_output = chain.invoke({
            "description": problem.get("description", ""),
            "function_signature": problem.get("function_signature", ""),
            "code": code
        }).content
        
        print(f"🤖 LLM Response: {raw_output[:200]}...")
        
        # 🔥 FIX: Clean before parsing
        cleaned_output = clean_json_text(raw_output)
        feedback = json.loads(cleaned_output)
        
        print(f"✅ Feedback generated: {feedback}")
        return feedback
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        print(f"Raw output: {raw_output}")
        return {
            "correctness": 0,
            "clarity": 0,
            "edge_cases": 0,
            "efficiency": 0,
            "overall": 0,
            "summary": f"Feedback generation failed: Invalid JSON response from LLM."
        }
    except Exception as e:
        print(f"❌ Coding Feedback Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "correctness": 0,
            "clarity": 0,
            "edge_cases": 0,
            "efficiency": 0,
            "overall": 0,
            "summary": f"Feedback generation failed. Please retry or check the submitted code."
        }