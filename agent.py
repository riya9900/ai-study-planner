import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import calculate_study_schedule

# Load environment variables from .env file
load_dotenv()

SYSTEM_INSTRUCTION = """
You are an expert AI Study Planner Agent and academic coach.
Your mission is to craft realistic, highly actionable, and motivating study plans for students and professionals.

When given a student's study request:
1. Always call the `calculate_study_schedule` tool first to compute the exact hour allocation, phase distribution, buffer days, and milestone dates.
2. Use the mathematical parameters returned by the tool to anchor your curriculum — do NOT invent conflicting dates or hour totals.
3. Structure your response cleanly using GitHub-flavored Markdown with the following sections:
   - 📊 **Executive Overview**: Total hours, active days, buffer days, and key milestone completion dates.
   - 🗺️ **Phase-by-Phase Roadmap**: For each phase, provide a clear breakdown of topics, practical exercises, and checkpoints.
   - 🎯 **Tailored Focus & Practice Strategy**: Specific tips based on the user's preferred learning style and weak areas.
   - ⏱️ **Daily Routine & Pomodoro Guide**: How to structure daily study blocks and use buffer days effectively without burnout.

Maintain an encouraging, practical, and structured tone.
"""

def get_gemini_client() -> genai.Client:
    """Initializes and returns a Google GenAI client using the GEMINI_API_KEY from environment variables."""
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
    specific_goals: str = ""
) -> Dict[str, Any]:
    """Generates a complete study plan using the AI Agent and the calculate_study_schedule tool.

    Args:
        subject: The subject, exam, or topic to learn.
        total_days: Total days available.
        daily_hours: Hours committed per day.
        current_level: Current knowledge level.
        learning_style: Preferred learning format.
        specific_goals: Optional specific focus areas or weaknesses.

    Returns:
        A dictionary containing:
        - 'plan_markdown': The complete markdown response from the AI Agent.
        - 'schedule_data': The raw structured data from calculate_study_schedule.
    """
    # 1. Run the deterministic tool first to get accurate schedule numbers for the UI
    schedule_data = calculate_study_schedule(
        total_days=total_days,
        daily_hours=daily_hours,
        current_level=current_level
    )

    # 2. Initialize the Gemini Client securely
    client = get_gemini_client()

    # 3. Formulate the user prompt with all inputs
    user_prompt = f"""
I need a personalized study plan with the following requirements:
- Subject/Goal: {subject}
- Total Days Available: {total_days} days
- Daily Time Commitment: {daily_hours} hours/day
- Current Skill Level: {current_level}
- Learning Style Preference: {learning_style}
- Specific Topics / Focus Areas: {specific_goals if specific_goals.strip() else 'Comprehensive coverage of standard syllabus'}

Please call calculate_study_schedule to calculate the phase breakdown, buffer days, and milestone dates, and then generate the complete, detailed study curriculum.
"""

    # 4. Attempt generation with model fallback for high availability
    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest"]
    last_error: Optional[Exception] = None

    for model_name in models_to_try:
        try:
            # We create a chat session with Automatic Function Calling (AFC) enabled
            chat = client.chats.create(
                model=model_name,
                config=types.GenerateContentConfig(
                    tools=[calculate_study_schedule],
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.7,
                )
            )
            response = chat.send_message(user_prompt)
            
            if response and response.text:
                return {
                    "plan_markdown": response.text,
                    "schedule_data": schedule_data
                }
        except Exception as e:
            last_error = e
            continue

    # If all models failed, raise the last recorded error
    raise RuntimeError(f"Failed to generate study plan with Gemini Agent: {last_error}")


if __name__ == "__main__":
    # Standalone self-test for the agent
    import sys
    # Ensure Windows console handles UTF-8 emojis smoothly
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("--- Running Agent Self-Test ---")
    try:
        result = generate_study_plan(
            subject="Git and GitHub Mastery",
            total_days=7,
            daily_hours=1.5,
            current_level="Beginner",
            learning_style="Hands-on / Practical & Projects",
            specific_goals="Branching, merge conflicts, pull requests"
        )
        print("\n[SUCCESS] Plan Generated! Output Preview:\n")
        print(result["plan_markdown"][:600])
        print("\n... [Output truncated for preview]")
    except Exception as err:
        print(f"\n[ERROR] Test failed: {err}")
