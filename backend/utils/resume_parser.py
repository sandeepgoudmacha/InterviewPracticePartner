"""Resume parsing utilities using LLM."""
import fitz  # PyMuPDF
import json
import re
from langchain_core.prompts import PromptTemplate
from config.llm import llm


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF using PyMuPDF.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text from PDF
    """
    text = ""
    try:
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


def clean_json_response(response: str) -> str:
    """
    Clean the LLM response to extract valid JSON.
    
    Args:
        response: Raw LLM response
        
    Returns:
        Cleaned JSON string
    """
    # Remove any markdown code blocks
    response = re.sub(r'```json\s*', '', response)
    response = re.sub(r'```\s*', '', response)
    
    # Find JSON-like content
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    return response.strip()


def setup_llm_chain():
    """Setup LLM and prompt chain for resume parsing."""
    try:
        template = """
You are an intelligent resume parser. Extract information from the resume text and return ONLY valid JSON in this exact format:

{{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "phone number",
  "education": [
    {{
      "degree": "degree name",
      "institution": "school name",
      "year": "graduation year"
    }}
  ],
  "skills": ["skill1", "skill2", "skill3"],
  "experience": [
    {{
      "title": "job title",
      "company": "company name",
      "duration": "time period",
      "description": "job description"
    }}
  ],
  "projects": [
    {{
      "title": "project name",
      "tech": ["technology1", "technology2"],
      "description": "project description"
    }}
  ]
}}

Important: Return ONLY the JSON object, no additional text or explanation.

Resume Text:
{text}
"""

        prompt = PromptTemplate(
            input_variables=["text"],
            template=template
        )

        chain = prompt | llm
        return chain
    
    except Exception as e:
        print(f"Error setting up LLM chain: {e}")
        return None


def parse_resume_with_llm(pdf_path: str, max_retries: int = 3) -> dict:
    """
    Parse resume with retry logic and error handling.
    
    Args:
        pdf_path: Path to resume PDF
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dictionary containing parsed resume data or error information
    """
    # Extract text from PDF
    resume_text = extract_text_from_pdf(pdf_path)
    if not resume_text:
        return {"error": "Could not extract text from PDF"}
    
    # Setup LLM chain
    chain = setup_llm_chain()
    if not chain:
        return {"error": "Could not setup LLM chain"}
    
    # Try parsing with retries
    for attempt in range(max_retries):
        try:
            # Get response from LLM
            raw_response = chain.invoke({"text": resume_text[:4000]})  # Limit text length
            
            # ChatModels return an AIMessage object with a .content attribute
            # LLMs return a simple string
            response_text = raw_response.content if hasattr(raw_response, "content") else str(raw_response)
            
            # Clean and parse JSON
            cleaned_response = clean_json_response(response_text)
            parsed_data = json.loads(cleaned_response)
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                return {
                    "error": "Failed to parse JSON after multiple attempts",
                    "raw_response": str(raw_response),
                    "cleaned_response": cleaned_response
                }
        
        except Exception as e:
            print(f"❌ General error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                return {"error": f"Failed to process resume: {str(e)}"}
    
    return {"error": "Unexpected failure"}
