import datetime
from typing import Dict, Any

def calculate_study_schedule(total_days: int, daily_hours: float, current_level: str = "Beginner") -> Dict[str, Any]:
    """Calculates a realistic study pace, phase distribution, buffer days, and milestone deadlines.

    Args:
        total_days: Total number of days available until the exam or target completion.
        daily_hours: Number of study hours dedicated per day.
        current_level: The student's current proficiency: 'Beginner', 'Intermediate', or 'Advanced'.

    Returns:
        A dictionary containing total hours, active study days, buffer days,
        phase breakdown with hour budgets, and concrete milestone calendar dates.
    """
    total_days = max(1, int(total_days))
    daily_hours = max(0.5, float(daily_hours))
    level_lower = current_level.lower()

    # Calculate buffer / rest days (approx 1 buffer day per week to prevent burnout)
    buffer_days = max(1, total_days // 7) if total_days >= 7 else 0
    active_days = max(1, total_days - buffer_days)
    
    total_study_hours = round(total_days * daily_hours, 1)
    active_study_hours = round(active_days * daily_hours, 1)
    buffer_hours = round(buffer_days * daily_hours, 1)

    # Determine phase weightings based on starting knowledge level
    if "advanced" in level_lower:
        p1_pct, p2_pct, p3_pct = 0.15, 0.50, 0.35
        p1_name = "Phase 1: Knowledge Audit & High-Yield Fundamentals"
        p2_name = "Phase 2: Complex Problem Sets & Intensive Practice"
        p3_name = "Phase 3: Simulated Timed Mocks & Mastery Polish"
    elif "intermediate" in level_lower:
        p1_pct, p2_pct, p3_pct = 0.25, 0.50, 0.25
        p1_name = "Phase 1: Core Principles & Gap Filling"
        p2_name = "Phase 2: Advanced Topics & Hands-on Implementation"
        p3_name = "Phase 3: Project Building, Mock Tests & Review"
    else:  # Beginner default
        p1_pct, p2_pct, p3_pct = 0.45, 0.35, 0.20
        p1_name = "Phase 1: Foundational Principles & Core Concepts"
        p2_name = "Phase 2: Guided Practice & Practical Application"
        p3_name = "Phase 3: Review, Quizzes, & Confidence Building"

    # Allocate active days across phases
    p1_days = max(1, round(active_days * p1_pct))
    p2_days = max(1, round(active_days * p2_pct))
    p3_days = max(1, active_days - (p1_days + p2_days))

    # Calculate calendar milestone dates
    start_date = datetime.date.today()
    p1_end = start_date + datetime.timedelta(days=p1_days)
    p2_end = p1_end + datetime.timedelta(days=p2_days)
    final_date = start_date + datetime.timedelta(days=total_days)

    # Pomodoro session guidance (25 min study + 5 min rest per 30-min block)
    daily_pomodoro_sessions = int((daily_hours * 60) // 30)

    return {
        "summary": {
            "total_days": total_days,
            "daily_hours": daily_hours,
            "total_study_hours": total_study_hours,
            "active_study_days": active_days,
            "active_study_hours": active_study_hours,
            "buffer_days": buffer_days,
            "buffer_hours": buffer_hours,
            "daily_pomodoro_sessions": daily_pomodoro_sessions
        },
        "phases": [
            {
                "phase_number": 1,
                "name": p1_name,
                "days": p1_days,
                "allocated_hours": round(p1_days * daily_hours, 1),
                "start_date": start_date.strftime("%Y-%m-%d"),
                "target_date": p1_end.strftime("%Y-%m-%d")
            },
            {
                "phase_number": 2,
                "name": p2_name,
                "days": p2_days,
                "allocated_hours": round(p2_days * daily_hours, 1),
                "start_date": (p1_end + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                "target_date": p2_end.strftime("%Y-%m-%d")
            },
            {
                "phase_number": 3,
                "name": p3_name,
                "days": p3_days,
                "allocated_hours": round(p3_days * daily_hours, 1),
                "start_date": (p2_end + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                "target_date": final_date.strftime("%Y-%m-%d")
            }
        ],
        "milestones": [
            {"milestone": "Start & Foundation Completed", "date": p1_end.strftime("%b %d, %Y")},
            {"milestone": "Core Mastery & Mid-Point Check", "date": p2_end.strftime("%b %d, %Y")},
            {"milestone": "Final Review & Target Goal Achieved", "date": final_date.strftime("%b %d, %Y")}
        ]
    }

if __name__ == "__main__":
    # Quick self-test when running directly
    import json
    sample_result = calculate_study_schedule(total_days=30, daily_hours=2.0, current_level="Beginner")
    print("--- Tool Self-Test Result ---")
    print(json.dumps(sample_result, indent=2))
