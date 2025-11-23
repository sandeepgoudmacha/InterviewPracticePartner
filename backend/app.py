from fastapi import FastAPI, File, UploadFile, Form , Depends, HTTPException , Request , APIRouter
from config import users_collection , interviews_collection
from datetime import datetime
from pydantic import BaseModel
from auth import hash_password, verify_password, create_access_token, get_current_user
from fastapi.middleware.cors import CORSMiddleware
from services.interview_session import InterviewSession
from services.coding_session import CodingSession
from services.feedback_service import generate_hr_feedback, generate_sales_feedback, generate_coding_feedback
from services.hr_session import HRInterviewSession
from services.sales_session import SalesInterviewSession
from utils import transcribe, get_confidence_score, sanitize_for_json
from uuid import uuid4
from typing import Optional, Dict, Any
from bson import ObjectId

import json
import numpy as np
from routes.user import router as user_router

import os
import uvicorn

app = FastAPI()
user_sessions = {}

router = APIRouter()
app.include_router(user_router)


def _response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize response to ensure JSON compatibility."""
    return sanitize_for_json(data)


# CORS setup so frontend can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserAuth(BaseModel):
    email: str
    password: str

class CodeSubmission(BaseModel):
    code: str







@app.post("/api/setup")
def setup_session(
    role: str = Form(...),
    interview_type: str = Form(...),
    custom_round: str = Form(''),
    user: str = Depends(get_current_user)
):
    session_id = str(uuid4())

    # 🔁 Load parsed resume text from DB
    user_data = users_collection.find_one({"email": user})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    resume = {
        "name": user_data.get("name"),
        "email": user_data.get("email"),
        "phone": user_data.get("phone"),
        "skills": user_data.get("skills", []),
        "projects": user_data.get("projects", []),
        "experience": user_data.get("experience", [])
    }

    # Convert to structured text
    resume_text = "\n".join([
    f"Name: {resume.get('name')}",
    f"Email: {resume.get('email')}",
    f"Phone: {resume.get('phone')}",
    "Skills: " + ", ".join(resume.get('skills', [])),
    "Projects: " + ", ".join(resume.get("projects", [])),  # no .get() here
    "Experience: " + ", ".join(resume.get("experience", []))  # no .get() here
])



    if interview_type == "full":
        # Special handling for Sales Representative role
        if "sales" in role.lower():
            session_data = {
                "mode": "full",
                "sales_round_1": SalesInterviewSession(role=role, session_id=session_id, round_type="hiring_manager", rounds=3),
                "sales_round_2": SalesInterviewSession(role=role, session_id=session_id + "_sr2", round_type="senior_leadership", rounds=3),
                "current": "sales_round_1",
                "role": role
            }
        else:
            session_data = {
                "mode": "full",
                "tech": InterviewSession(role=role, resume_obj=resume_text, rounds=5, session_id=session_id),
                "hr": HRInterviewSession(role=role, rounds=3, session_id=session_id + "_hr"),
                "current": "tech",
                "role": role
            }

            # ⛔ Skip coding round for frontend, backend, and data scientist roles
            if role.lower() not in ["frontend developer", "backend developer", "data scientist"]:
                session_data["code"] = CodingSession(role=role, rounds=3)

        user_sessions[user] = session_data
    elif custom_round == "technical":
        user_sessions[user] = InterviewSession(role=role, resume_obj=resume_text, rounds=5, session_id=session_id)
    elif custom_round == "behavioral":
        # Check if it's for Sales Rep role (Senior Leadership) or regular HR
        if "sales" in role.lower():
            user_sessions[user] = SalesInterviewSession(role=role, session_id=session_id, round_type="senior_leadership", rounds=5)
        else:
            user_sessions[user] = HRInterviewSession(role=role, rounds=5, session_id=session_id)
    elif custom_round == "coding":
        user_sessions[user] = CodingSession(role=role, rounds=3)
    elif custom_round == "sales":
        user_sessions[user] = SalesInterviewSession(role=role, session_id=session_id, round_type="hiring_manager", rounds=5)
    else:
        raise HTTPException(status_code=400, detail="Invalid round type")
    
    return {"session_id": session_id}



@app.post("/api/signup")
def signup(user: UserAuth):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = hash_password(user.password)

    users_collection.insert_one({
        "email": user.email,
        "password": hashed_pw,
        "createdAt": datetime.utcnow()
    })

    return {"msg": "User registered successfully"}


@app.post("/api/login")
def login(user: UserAuth):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token}

# backend/app.py

@app.post("/api/parse-resume")
async def parse_resume_endpoint(
    resume: UploadFile = File(...), 
    user: str = Depends(get_current_user)
):
    
    import tempfile
    import os
    from utils import parse_resume_with_llm
    print("🔄 Received resume for parsing:")
    # 1. Save uploaded file to temp path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        contents = await resume.read()
        tmp.write(contents)
        tmp_path = tmp.name

    # 2. Parse the resume using LLM
    try:
        result = parse_resume_with_llm(tmp_path)
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # 3. Handle Parsing Errors
    if "error" in result:
        raise HTTPException(status_code=400, detail="Resume parsing failed. Please try a clearer PDF.")

    # 4. 🔥 CRITICAL FIX: Update the User in MongoDB
    # This ensures the new skills/projects are used in the next interview.
    update_data = {
        "skills": result.get("skills", []),
        "experience": result.get("experience", []),
        "projects": result.get("projects", []),
        "education": result.get("education", []),
        "resume_parsed": True  # Flag to show parsing is done
    }

    # Only update name/phone if they were found in the resume
    if result.get("name"):
        update_data["name"] = result["name"]
    if result.get("phone"):
        update_data["phone"] = result["phone"]

    users_collection.update_one(
        {"email": user},
        {"$set": update_data}
    )

    return {"message": "Resume parsed and profile updated successfully", "data": result}




import os
@app.post("/api/audio")
async def handle_audio(audio: UploadFile = File(...), focus_score: Optional[float] = Form(1.0), user: str = Depends(get_current_user)):
    session_info = user_sessions.get(user)

    if not session_info:
        raise HTTPException(status_code=404, detail="No active session")

    # Save audio
    contents = await audio.read()
    tmp_path = f"temp_{uuid4().hex}.wav"
    with open(tmp_path, "wb") as f:
        f.write(contents)

    answer = transcribe(tmp_path)
    confidence = get_confidence_score(tmp_path)
    os.remove(tmp_path)
    # Get the current session object
    if isinstance(session_info, dict):
        session = session_info.get(session_info.get("current"))
    else:
        session = session_info

    # Ensure session.meta exists
    if not hasattr(session, "meta") or session.meta is None:
        session.meta = {}

    # Add metrics
    session.meta.setdefault("confidence_scores", []).append(confidence)
    session.meta.setdefault("focus_scores", []).append(focus_score)

    # FULL INTERVIEW MODE
    if isinstance(session_info, dict):
        current_round = session_info["current"]
        
        # Check if in final Q&A stage
        if session_info.get("in_final_qa"):
            # Handle final Q&A responses
            user_answer_lower = answer.strip().lower()
            
            # Check if user wants to end
            if any(word in user_answer_lower for word in ["end", "no", "nothing", "that's all", "done", "no questions", "no thank you"]):
                return _response({
                    "text": "Thank you so much for your time and great responses! We'll review everything and share a feedback. Have a wonderful day!",
                    "answer": answer,
                    "confidence": confidence,
                    "interview_ended": True
                })
            
            # User has a question - guide them as interviewer
            if answer.strip():
                # Use LLM to guide user's questions professionally
                from config import llm
                from langchain_core.messages import SystemMessage, HumanMessage
                
                guidance_system = f"""You are a professional interviewer responding to a candidate's question during the closing Q&A stage.

The candidate role is: {session_info.get('role', 'Unknown')}

Guidelines for response:
- Be warm, helpful, and informative
- Provide realistic information about: role responsibilities, team culture, growth opportunities, tech stack, work environment
- Keep response concise (2-3 sentences max)
- Sound natural and encouraging
- If asked about salary/benefits, say "That will be discussed in the offer stage"
- If asked about timeline, say "We'll get back to you and share a feedback"
- After your response, ask if they have any other questions or if they're ready to wrap up
- Be professional but friendly

Candidate's question: "{answer}"

Respond naturally as an interviewer would."""
                
                response = llm.invoke([
                    SystemMessage(content=guidance_system),
                    HumanMessage(content=f"Answer this question and ask if they have more or want to wrap up.")
                ]).content
                
                return _response({
                    "text": response,
                    "answer": answer,
                    "confidence": confidence,
                    "still_in_qa": True
                })
            else:
                # Empty response, ask again
                return _response({
                    "text": "Do you have any other questions for us? Or are you ready to wrap up?",
                    "answer": answer,
                    "confidence": confidence,
                    "still_in_qa": True
                })
        
        session = session_info[current_round]
        
        # First-time greeting
        if not session.history and not session.meta.get("greeting_sent"):
            session.meta["greeting_sent"] = True

            # If user already spoke something (i.e., this is not just ping for first question)
            if answer.strip():
                session.provide_answer(answer)
                next_q = session.ask_question()
                return _response({"text": next_q, "answer": answer, "confidence": confidence})
            
            # Otherwise, greet first
            first_question = session.ask_question()
            return _response({"text": first_question, "answer": "", "confidence": confidence})

        # Process answer
        session.provide_answer(answer)
        
        # Check if we should ask a follow-up question
        if session.meta.get("last_followup_asked"):
            # We already asked follow-up for this answer, move to next main question
            session.meta["last_followup_asked"] = False
            next_q = session.ask_question()
        else:
            # Try to generate a follow-up question first
            followup_q = session.generate_followup_question(answer)
            if followup_q:
                # Mark that we asked a follow-up for this answer
                session.meta["last_followup_asked"] = True
                next_q = followup_q
            else:
                # No follow-up generated, get next main question
                next_q = session.ask_question()

        if next_q:
            return _response({"text": next_q, "answer": answer, "confidence": confidence})
        else:
            # Switch rounds
            if current_round == "sales_round_1":
                # Transition from Hiring Manager Round to Senior Leadership Round
                session_info["current"] = "sales_round_2"
                return _response({
                    "text": "Excellent! Now let's move to Round 2: Senior Leadership Interview. This is our final assessment with a VP/Director to confirm your fit with our team and company vision.",
                    "answer": answer,
                    "confidence": confidence
                })
            elif current_round == "sales_round_2":
                # Sales interview complete, move to Q&A
                session_info["in_final_qa"] = True
                return _response({
                    "text": "Thank you for your great responses! Before we wrap up, do you have any questions for me or our team?",
                    "answer": answer,
                    "confidence": confidence,
                    "starting_qa": True
                })
            elif current_round == "tech":
                if "frontend" in session_info["role"].lower():

                    session_info["current"] = "hr"
                    return _response({"text": "Awesome. Now let’s start the behavioral (HR) round.", "answer": answer, "confidence": confidence})
                elif "backend" in session_info["role"].lower():

                    session_info["current"] = "hr"
                    return _response({"text": "Awesome. Now let’s start the behavioral (HR) round.", "answer": answer, "confidence": confidence})
                elif "data" in session_info["role"].lower():

                    session_info["current"] = "hr"
                    return _response({"text": "Awesome. Now let’s start the behavioral (HR) round.", "answer": answer, "confidence": confidence})


                session_info["current"] = "code"
                return _response({"text": "Okay! Now let’s move to the live coding round.", "answer": answer, "confidence": confidence})
            elif current_round == "code":
                session_info["current"] = "hr"
                return _response({"text": "Okay. Now let's start the behavioral (HR) round. Tell me about your Strengths and Weaknesses?", "answer": answer, "confidence": confidence})
            elif current_round == "hr":
                # Move to final Q&A stage
                session_info["in_final_qa"] = True
                return _response({
                    "text": "Thank you for all your responses! Before we wrap up, do you have any questions for me or our team? Or would you like to end the interview?",
                    "answer": answer,
                    "confidence": confidence,
                    "starting_qa": True
                })
            else:
                return _response({"text": "The interview is complete. Thank you!", "answer": answer, "confidence": confidence})

    # SINGLE ROUND MODE
    else:
        session = session_info
        
        # Check if in final Q&A stage
        if session.meta.get("in_final_qa"):
            user_answer_lower = answer.strip().lower()
            
            # Check if user wants to end
            if any(word in user_answer_lower for word in ["end", "no", "nothing", "that's all", "done", "no questions", "no thank you"]):
                return _response({
                    "text": "Thank you so much for your time and great responses! We'll review everything and get back to you and share a feedback. Have a wonderful day!",
                    "answer": answer,
                    "confidence": confidence,
                    "interview_ended": True
                })
            
            # User has a question - guide them as interviewer
            if answer.strip():
                from config import llm
                from langchain_core.messages import SystemMessage, HumanMessage
                
                guidance_system = f"""You are a professional interviewer responding to a candidate's question.

Guidelines:
- Be warm and helpful
- Provide realistic information about the role and team
- Keep response concise (2-3 sentences)
- After answering, ask if they have more questions or want to wrap up
Note: Never say solution or logic or hint, dont say ever about them , behave as interviewer
Candidate's question: "{answer}"
"""
                
                response = llm.invoke([
                    SystemMessage(content=guidance_system),
                    HumanMessage(content="Answer and ask if they have more questions or want to end.")
                ]).content
                
                return _response({
                    "text": response,
                    "answer": answer,
                    "confidence": confidence,
                    "still_in_qa": True
                })
            else:
                return _response({
                    "text": "Do you have any other questions? Or are you ready to wrap up?",
                    "answer": answer,
                    "confidence": confidence,
                    "still_in_qa": True
                })

        # First-time greeting
        if not session.history and not session.meta.get("greeting_sent"):
            session.meta["greeting_sent"] = True

            # If user already spoke something (i.e., this is not just ping for first question)
            if answer.strip():
                session.provide_answer(answer)
                next_q = session.ask_question()
                return _response({"text": next_q, "answer": answer, "confidence": confidence})
            
            # Otherwise, greet first
            first_question = session.ask_question()
            return _response({"text": first_question, "answer": "", "confidence": confidence})

        # Process answer
        session.provide_answer(answer)
        
        # Check if we should ask a follow-up question
        if session.meta.get("last_followup_asked"):
            # We already asked follow-up for this answer, move to next main question
            session.meta["last_followup_asked"] = False
            next_q = session.ask_question()
        else:
            # Try to generate a follow-up question first
            followup_q = session.generate_followup_question(answer)
            if followup_q:
                # Mark that we asked a follow-up for this answer
                session.meta["last_followup_asked"] = True
                next_q = followup_q
            else:
                # No follow-up generated, get next main question
                next_q = session.ask_question()

        if next_q:
            return _response({"text": next_q, "answer": answer, "confidence": confidence})
        else:
            # Move to final Q&A for single round too
            if isinstance(session_info, dict):
                session_info["in_final_qa"] = True
            else:
                # For non-dict sessions, store in meta
                session.meta["in_final_qa"] = True
            return _response({
                "text": "Great! Do you have any questions for us? Or would you like to end the interview?",
                "answer": answer,
                "confidence": confidence,
                "starting_qa": True
            })


@app.post("/api/end-interview")
def end_interview(user: str = Depends(get_current_user)):
    """End the interview gracefully and prepare for feedback"""
    session_info = user_sessions.get(user)

    if not session_info:
        raise HTTPException(status_code=404, detail="No active session")
    
    # Mark interview as ended
    if isinstance(session_info, dict):
        session_info["ended"] = True
        session_info["ended_at"] = datetime.utcnow()
    
    return {"status": "success", "message": "Interview ended"}


@app.get("/api/feedback")
def get_feedback(user: str = Depends(get_current_user)):
    session_info = user_sessions.get(user)

    if not session_info:
        raise HTTPException(status_code=404, detail="No active session")

    feedback_data = {}
    transcript_data = ""

    # Get current session for flag tracking
    session = session_info if not isinstance(session_info, dict) else session_info.get(session_info["current"])
    if not hasattr(session, "meta") or session.meta is None:
        session.meta = {}

    if isinstance(session_info, dict) and session_info.get("mode") == "full":
        # Check if it's a Sales interview or Regular interview
        if "sales_round_1" in session_info:
            # Sales Interview Feedback using feedback_utils
            sales_r1_fb = generate_sales_feedback(session_info["sales_round_1"].history, "hiring_manager")
            sales_r2_fb = generate_sales_feedback(session_info["sales_round_2"].history, "senior_leadership")

            feedback_data = {
                "hiring_manager": sales_r1_fb,
                "senior_leadership": sales_r2_fb
            }

            transcript_data = "\n".join([
                f"Q: {q['question']}\nA: {q['answer']}"
                for q in session_info["sales_round_1"].history + session_info["sales_round_2"].history
                if q.get("answer")
            ])
        else:
            # Regular Interview Feedback (Tech, Code, HR)
            tech_fb = generate_hr_feedback(session_info["tech"].history)
            hr_fb = generate_hr_feedback(session_info["hr"].history)

            feedback_data = {
                "technical": tech_fb,
                "behavioral": hr_fb
            }

            if "code" in session_info:
                code_fb = generate_coding_feedback(session_info["code"].history)
                feedback_data["coding"] = code_fb

            transcript_data = "\n".join([
                f"Q: {q['question']}\nA: {q['answer']}"
                for q in session_info["tech"].history + session_info["hr"].history
                if q.get("answer")
            ])

    else:
        # Single round custom interview
        if hasattr(session, "history"):
            summary = generate_hr_feedback(session.history)
        else:
            summary = {"overall": 0, "summary": "No session history found"}
        
        feedback_data = summary if isinstance(summary, dict) else json.loads(summary)

        transcript_data = "\n".join([
            f"Q: {q['question']}\nA: {q['answer']}"
            for q in session.history
            if q.get("answer")
        ])

    # Collect average metrics
    if isinstance(session_info, dict):
        all_conf, all_focus = [], []
        # Check if it's Sales interview or Regular interview
        if "sales_round_1" in session_info:
            keys_to_check = ["sales_round_1", "sales_round_2"]
        else:
            keys_to_check = ["tech", "hr"]
        
        for key in keys_to_check:
            if key in session_info:
                scores = getattr(session_info[key], "meta", {})
                all_conf += scores.get("confidence_scores", [])
                all_focus += scores.get("focus_scores", [])
        
        avg_conf = float(np.mean(all_conf)) if all_conf else 0.0
        avg_focus = float(np.mean(all_focus)) if all_focus else 0.0
        # Ensure no NaN values
        avg_conf = 0.0 if (np.isnan(avg_conf) or avg_conf is None) else avg_conf
        avg_focus = 0.0 if (np.isnan(avg_focus) or avg_focus is None) else avg_focus
    else:
        conf_scores = session.meta.get("confidence_scores", [])
        focus_scores = session.meta.get("focus_scores", [])
        avg_conf = float(np.mean(conf_scores)) if conf_scores else 0.0
        avg_focus = float(np.mean(focus_scores)) if focus_scores else 0.0
        # Ensure no NaN values
        avg_conf = 0.0 if (np.isnan(avg_conf) or avg_conf is None) else avg_conf
        avg_focus = 0.0 if (np.isnan(avg_focus) or avg_focus is None) else avg_focus

    # ✅ PREVENT DUPLICATE SAVES
    if not session.meta.get("feedback_saved"):
        # Determine role based on interview type
        if isinstance(session_info, dict):
            if "sales_round_1" in session_info:
                role = session_info["sales_round_1"].role
            else:
                role = session_info["tech"].role
        else:
            role = session.role
        
        interviews_collection.insert_one({
            "userId": user,
            "role": role,
            "date": datetime.now().isoformat(),
            "mode": session_info["mode"] if isinstance(session_info, dict) else getattr(session_info, "round_type", "custom"),
            "transcript": transcript_data,
            "feedback": feedback_data,
            "average_confidence": avg_conf,
            "average_focus": avg_focus
        })
        session.meta["feedback_saved"] = True  # 🟢 Mark as saved
    else:
        print("🛑 Feedback already saved. Skipping DB insert.")

    return _response({
        **feedback_data,
        "average_confidence": avg_conf,
        "average_focus": avg_focus,
    })




@app.get("/api/coding-problem")
def get_coding_problem(user: str = Depends(get_current_user)):
    session_info = user_sessions.get(user)

    if not session_info:
        raise HTTPException(status_code=404, detail="No active session found.")
    

    # Full interview mode
    if isinstance(session_info, dict) and session_info.get("mode") == "full":
        # ❌ prevent accessing coding round too early
        if session_info.get("current") != "code":
            raise HTTPException(status_code=400, detail="Not in coding round yet.")

        # ✅ lazy init if not already created
        if "code" not in session_info:
            session_info["code"] = CodingSession(role=session_info["tech"].role, rounds=3)

        session = session_info["code"]

    elif isinstance(session_info, CodingSession):
        session = session_info

    else:
        raise HTTPException(status_code=400, detail="No coding session active.")
    print("Coding round index:", session.current_round, "/", session.rounds)

    problem = session.get_next_problem()
    if not problem:
        raise HTTPException(status_code=204, detail="No more coding problems.")

    return problem






@app.post("/api/submit-code")
async def submit_code(request: Request, user: str = Depends(get_current_user)):
    data = await request.json()
    code = data.get("code")

    session_info = user_sessions.get(user)
    if not session_info:
        raise HTTPException(status_code=404, detail="No active session")

    if isinstance(session_info, dict) and session_info.get("mode") == "full":
        session = session_info.get("code")
        session.submit_solution(code)

        # Fetch next problem
        next_problem = session.get_next_problem()
        if next_problem:
            return { "next": True, "problem": next_problem }

        # No more problems, switch to HR
        session_info["current"] = "hr"
        return {
            "next": False,
            "message": "Coding round complete. Moving to HR."
        }

    elif isinstance(session_info, CodingSession):
        session_info.submit_solution(code)
        return { "next": False, "message": "Thanks for your submission." }

    else:
        raise HTTPException(status_code=400, detail="Invalid coding session")


def get_average(scores: list[float]) -> float:
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 2)

from config import code_llm
@app.post("/api/code-explanation")
async def handle_code_explanation(audio: UploadFile = File(...), user: str = Depends(get_current_user)):
    session_info = user_sessions.get(user)

    if not session_info:
        raise HTTPException(status_code=404, detail="No session")

    # 🎯 Get CodingSession
    if isinstance(session_info, dict) and session_info.get("mode") == "full":
        session = session_info.get("code")
    elif isinstance(session_info, CodingSession):
        session = session_info
    else:
        raise HTTPException(status_code=400, detail="Not in coding session")

    # 🎤 Save and transcribe audio
    contents = await audio.read()
    tmp_path = f"temp_explain_{uuid4().hex}.wav"
    with open(tmp_path, "wb") as f:
        f.write(contents)

    user_text = transcribe(tmp_path)
    os.remove(tmp_path)

    # 🧠 Use LLM to respond to explanation
    session.explanation_history.append({"user": user_text})

    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

    messages = [
        # CHANGE: Updated System Message to handle doubts/clarifications
        SystemMessage(content="""
        You are a supportive technical interviewer. 
        - If the candidate asks a doubt or asks you to explain the question, clarify the problem statement simply without giving away the full solution.
        - If the candidate is explaining their approach, listen and give brief, encouraging feedback or hints if they are stuck.
        - Keep your responses concise and conversational.
        focus on guiding the candidate rather than providing direct answers.
        important note: never and dont give the solution and hint or logic to the candidate.
        important note: dont say about the issue with the formatting of the resume provided
        """),
        HumanMessage(content="Problem:\n" + json.dumps(session.history[-1]["problem"], indent=2)),
        HumanMessage(content="Current Code:\n" + session.history[-1]["code"]),
    ]

    # Add chat history
    for msg in session.explanation_history:
        if "user" in msg:
            messages.append(HumanMessage(content=msg["user"]))
        elif "ai" in msg:
            messages.append(AIMessage(content=msg["ai"]))

    response = code_llm.invoke(messages).content



    # 💾 Save AI response back to explanation history
    session.explanation_history.append({"ai": response})

    return {
        "user_text": user_text,
        "response": response
    }


@app.get("/api/interviews")
def get_user_interviews(user: str = Depends(get_current_user)):
    interviews = list(interviews_collection.find({"userId": user}))
    for i in interviews:
        i["_id"] = str(i["_id"])  # Convert ObjectId to string for frontend
    return _response(interviews)

@app.get("/api/interviews/{interview_id}")
def get_interview(interview_id: str, user: str = Depends(get_current_user)):
    interview = interviews_collection.find_one({"_id": ObjectId(interview_id), "userId": user})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    interview["_id"] = str(interview["_id"])  # convert ObjectId to string
    return _response(interview)


@app.get("/api/history")
def get_history(user: str = Depends(get_current_user)):
    session = user_sessions.get(user)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if isinstance(session, dict):  # full session (tech + hr + coding)
        current_round = session.get(session['current'])
        history = current_round.history if current_round else []
    else:
        history = session.history

    return _response({"history": history})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
