import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import calculate_study_schedule

# Load environment variables securely from .env
load_dotenv()

SYSTEM_INSTRUCTION = """
You are an expert AI Study Planner Agent and academic coach.
Your mission is to craft realistic, actionable, and easy-to-read study plans.

### CORE OPERATING RULES:
1. **Syllabus Grounding**:
   - If a syllabus is provided: You MUST treat it as the primary authority. Extract the actual units, modules, and topics directly from it. Do NOT replace them with generic topics.
   - If NO syllabus is provided: Clearly note that you are designing a standardized curriculum based on the requested subject.
   - NEVER pretend you read a syllabus if none was provided.

2. **Exam vs. Self-Paced Mode**:
   - IF NO EXAM DATE IS PROVIDED:
     - The student is in Self-Paced Learning Mode.
     - Do NOT mention an exam date, exam countdown, or emergency mode.
     - Structure the plan for thorough, stress-free mastery across the planned days.
   - IF AN EXAM DATE IS PROVIDED:
     - The student has a firm deadline. Strictly ensure all study ends on or before the exam date.
     - If in Emergency Mode (3 or fewer days): Prioritize high-yield core topics, quick formulas, and rapid-fire MCQs.

3. **Topic Prioritization**:
   - Tag topics with clear priority markers:
     - 🔥 HIGH PRIORITY: Core, foundational, and high-frequency topics.
     - ⚡ MEDIUM PRIORITY: Supporting topics and secondary modules.
     - 💡 LOW PRIORITY: Nuanced details or optional exploration.
   - NEVER drop syllabus topics silently.

4. **Beginner-Friendly, Highly Structured Formatting**:
   For every study day, you MUST use the following exact visual template:

   ### 📍 DAY [X] — [Day Focus Title]
   - **📅 Date:** [e.g. 29 Oct]
   - **⏰ Study time:** [e.g. 2 hours]
   - **Priority:** [🔥 High / ⚡ Medium / 💡 Low]

   📖 **Learn:**
   • **[Topic 1]**: [Clear, simple 1-2 sentence explanation suitable for a beginner]
   • **[Topic 2]**: [Clear, simple 1-2 sentence explanation suitable for a beginner]

   📝 **Practice:**
   • [e.g. Solve 5 MCQs on Topic 1]
   • [e.g. Write down the definition of Concept 2 from memory]

   🎯 **Today's Goal:**
   [One crisp sentence summarizing what the student should understand before going to sleep]

Keep your tone motivating, straightforward, and practical.
"""

def get_gemini_client() -> genai.Client:
    """Initializes and returns a Google GenAI client using GEMINI_API_KEY from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is not set or is still the placeholder. "
            "Please ensure your valid API key is placed in the .env file."
        )
    return genai.Client(api_key=api_key)


def generate_study_plan(
    subject: str,
    total_days: int,
    daily_hours: float,
    current_level: str = "Beginner",
    learning_style: str = "Balanced",
    specific_goals: str = "",
    exam_date_str: Optional[str] = None,
    syllabus_text: str = "",
    syllabus_filename: str = ""
) -> Dict[str, Any]:
    """Generates a complete study plan grounded in the uploaded syllabus and optional exam deadline.

    Args:
        subject: The subject or exam title.
        total_days: Total days available for the plan.
        daily_hours: Dedicated hours per day.
        current_level: Experience level.
        learning_style: Preferred learning approach.
        specific_goals: Optional extra focus areas.
        exam_date_str: Optional ISO string of exam date ('YYYY-MM-DD').
        syllabus_text: Extracted text from uploaded syllabus document.
        syllabus_filename: Name of the uploaded syllabus file.

    Returns:
        Dict with 'plan_markdown', 'schedule_data', 'is_emergency', and 'has_deadline'.
    """
    # 1. Run deterministic schedule calculation
    schedule_data = calculate_study_schedule(
        total_days=total_days,
        daily_hours=daily_hours,
        current_level=current_level,
        exam_date_str=exam_date_str
    )

    summary = schedule_data["summary"]
    has_deadline = summary["has_deadline"]
    is_emergency = summary["is_emergency"]
    daily_cal = schedule_data.get("daily_calendar", [])

    # Format calendar hints for the model
    cal_hints = "\n".join([
        f"- Day {d['day_number']} ({d['formatted_date']}): {d['hours']} hrs allocated "
        f"{'[BUFFER/REST]' if d['is_buffer'] else ''} "
        f"{'[EXAM DAY]' if d['is_exam_day'] else ''}"
        for d in daily_cal
    ])

    # 2. Build syllabus context prompt
    has_syllabus = bool(syllabus_text and syllabus_text.strip())
    if has_syllabus:
        syllabus_context = f"""
SOURCE DOCUMENT: Uploaded Syllabus File '{syllabus_filename}'
------------------------------------------------------------
{syllabus_text[:12000]}
------------------------------------------------------------
CRITICAL INSTRUCTION: Build the plan directly around the units, chapters, and topics in this document.
"""
    else:
        syllabus_context = """
NOTE: No syllabus file was uploaded. Use standard core curriculum for the requested subject.
"""

    # 3. Assemble User Prompt based on deadline presence
    if has_deadline:
        deadline_header = f"""
- Mode: DEADLINE-DRIVEN PREPARATION
- Exam Deadline: {summary.get('exam_date')} ({summary.get('days_left')} days remaining)
- Emergency Mode Active: {'YES 🚨 (CRUNCH MODE)' if is_emergency else 'NO (Standard Pace)'}
"""
    else:
        deadline_header = """
- Mode: SELF-PACED COMPREHENSIVE LEARNING (No exam deadline specified)
- Emergency Mode: INACTIVE (Stress-free, thorough pace)
"""

    user_prompt = f"""
Create a comprehensive study roadmap with the following exact constraints:

📌 STUDENT PROFILE & TIMELINE:
- Target Subject / Course: {subject}
{deadline_header}
- Total Study Budget: {summary.get('total_study_hours')} hours across {summary.get('total_days')} days
- Daily Commitment: {daily_hours} hours/day
- Student Knowledge Level: {current_level}
- Learning Style: {learning_style}
- Specific Student Focus: {specific_goals.strip() if specific_goals.strip() else 'Comprehensive syllabus coverage'}

📅 EXACT CALENDAR DAYS TO SCHEDULE:
{cal_hints}

{syllabus_context}

Please generate:
1. 🎯 Curriculum Overview & Priority Breakdown
2. Day-by-Day Roadmap using the strict DAY [X] format for every single day listed above.
3. Summary of Key Milestones & Review Strategy.
"""

    # 4. Initialize client and execute with model fallback
    # gemini-3-flash-preview prioritized for speed and quota
    client = get_gemini_client()
    models_to_try = ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-flash-latest"]
    last_error: Optional[Exception] = None

    for model_name in models_to_try:
        try:
            chat = client.chats.create(
                model=model_name,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.6,
                )
            )
            response = chat.send_message(user_prompt)
            if response and response.text:
                return {
                    "plan_markdown": response.text,
                    "schedule_data": schedule_data,
                    "is_emergency": is_emergency,
                    "has_deadline": has_deadline,
                    "has_syllabus": has_syllabus
                }
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"Agent failed to generate plan: {last_error}")


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("--- Running Agent Test with Optional (No) Exam Deadline ---")
    try:
        res = generate_study_plan(
            subject="Python Essentials",
            total_days=5,
            daily_hours=1.5,
            current_level="Beginner",
            exam_date_str=None,  # No exam date
            syllabus_text="Unit 1: Syntax & Variables\nUnit 2: Conditionals & Loops"
        )
        print("Success!")
        print("Has deadline:", res["has_deadline"])
        print("Is emergency:", res["is_emergency"])
        print("Plan Preview:\n", res["plan_markdown"][:300])
    except Exception as e:
        print("Test Error:", e)
