import datetime
from typing import Dict, Any, List, Optional

def calculate_study_schedule(
    total_days: int,
    daily_hours: float,
    current_level: str = "Beginner",
    exam_date_str: Optional[str] = None
) -> Dict[str, Any]:
    """Calculates a realistic, deadline-driven study pace, phase distribution, buffer days, and daily dates.

    Args:
        total_days: Total number of days available until the exam (inclusive of today).
        daily_hours: Number of study hours dedicated per day.
        current_level: The student's current proficiency: 'Beginner', 'Intermediate', or 'Advanced'.
        exam_date_str: Optional ISO format string of exam date ('YYYY-MM-DD').

    Returns:
        A dictionary containing total hours, active study days, buffer days,
        phase breakdown with hour budgets, concrete milestone calendar dates,
        and an explicit list of day-by-day dates ending strictly on or before the exam.
    """
    total_days = max(1, int(total_days))
    daily_hours = max(0.5, float(daily_hours))
    level_lower = current_level.lower()
    start_date = datetime.date.today()

    if exam_date_str:
        try:
            target_exam_date = datetime.date.fromisoformat(exam_date_str)
        except ValueError:
            target_exam_date = start_date + datetime.timedelta(days=total_days - 1)
    else:
        target_exam_date = start_date + datetime.timedelta(days=total_days - 1)

    is_emergency = total_days <= 3

    # Calculate buffer / rest days (Emergency mode has 0 buffer days to maximize crunch time)
    if is_emergency:
        buffer_days = 0
        active_days = total_days
    else:
        buffer_days = max(1, total_days // 7) if total_days >= 7 else 0
        active_days = max(1, total_days - buffer_days)

    total_study_hours = round(total_days * daily_hours, 1)
    active_study_hours = round(active_days * daily_hours, 1)
    buffer_hours = round(buffer_days * daily_hours, 1)

    # Determine phase weightings based on mode & starting level
    if is_emergency:
        # Rapid triage crunch phases
        p1_pct, p2_pct, p3_pct = 0.50, 0.30, 0.20
        p1_name = "Phase 1: High-Yield Core Concepts (Priority Triage)"
        p2_name = "Phase 2: High-Yield Problem Sets & Top 20 MCQs"
        p3_name = "Phase 3: Final Mock Exam & Key Formula/Definition Recall"
    elif "advanced" in level_lower:
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
    p1_days = max(1, round(active_days * p1_pct)) if active_days >= 3 else 1
    p2_days = max(1, round(active_days * p2_pct)) if active_days >= 3 else 1
    p3_days = max(1, active_days - (p1_days + p2_days)) if active_days >= 3 else 1

    # Adjust sum of phase days to match active_days exactly
    diff = (p1_days + p2_days + p3_days) - active_days
    if diff != 0:
        p2_days = max(1, p2_days - diff)

    # Calculate phase dates
    p1_start = start_date
    p1_end = p1_start + datetime.timedelta(days=max(0, p1_days - 1))
    
    p2_start = p1_end + datetime.timedelta(days=1)
    p2_end = p2_start + datetime.timedelta(days=max(0, p2_days - 1))
    
    p3_start = p2_end + datetime.timedelta(days=1)
    p3_end = target_exam_date

    # Build day-by-day calendar items
    daily_calendar = []
    current_date = start_date
    for day_idx in range(1, total_days + 1):
        # Determine if this day is a buffer day (placed at end of week)
        is_buf = False
        if buffer_days > 0 and not is_emergency:
            if day_idx % 7 == 0:
                is_buf = True

        daily_calendar.append({
            "day_number": day_idx,
            "date": current_date.strftime("%Y-%m-%d"),
            "formatted_date": current_date.strftime("%b %d"),
            "hours": daily_hours if not is_buf else 0,
            "is_buffer": is_buf,
            "is_exam_day": current_date == target_exam_date
        })
        current_date += datetime.timedelta(days=1)

    # Pomodoro calculation
    daily_pomodoro_sessions = max(1, int((daily_hours * 60) // 30))

    return {
        "summary": {
            "total_days": total_days,
            "daily_hours": daily_hours,
            "total_study_hours": total_study_hours,
            "active_study_days": active_days,
            "active_study_hours": active_study_hours,
            "buffer_days": buffer_days,
            "buffer_hours": buffer_hours,
            "daily_pomodoro_sessions": daily_pomodoro_sessions,
            "is_emergency": is_emergency,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "exam_date": target_exam_date.strftime("%Y-%m-%d"),
            "days_left": (target_exam_date - start_date).days
        },
        "phases": [
            {
                "phase_number": 1,
                "name": p1_name,
                "days": p1_days,
                "allocated_hours": round(p1_days * daily_hours, 1),
                "start_date": p1_start.strftime("%Y-%m-%d"),
                "target_date": p1_end.strftime("%Y-%m-%d")
            },
            {
                "phase_number": 2,
                "name": p2_name,
                "days": p2_days,
                "allocated_hours": round(p2_days * daily_hours, 1),
                "start_date": p2_start.strftime("%Y-%m-%d"),
                "target_date": p2_end.strftime("%Y-%m-%d")
            },
            {
                "phase_number": 3,
                "name": p3_name,
                "days": p3_days,
                "allocated_hours": round(p3_days * daily_hours, 1),
                "start_date": p3_start.strftime("%Y-%m-%d"),
                "target_date": p3_end.strftime("%Y-%m-%d")
            }
        ],
        "milestones": [
            {"milestone": "Start & Foundation Review", "date": p1_end.strftime("%b %d, %Y")},
            {"milestone": "Core Mastery & Mid-Point Check", "date": p2_end.strftime("%b %d, %Y")},
            {"milestone": "Final Exam Deadline", "date": target_exam_date.strftime("%b %d, %Y")}
        ],
        "daily_calendar": daily_calendar
    }

if __name__ == "__main__":
    import json
    # Test standard mode
    res_std = calculate_study_schedule(total_days=14, daily_hours=2.0, current_level="Beginner")
    print("Standard Days Left:", res_std["summary"]["days_left"])

    # Test emergency mode
    res_emg = calculate_study_schedule(total_days=2, daily_hours=3.0, current_level="Beginner")
    print("Emergency Mode:", res_emg["summary"]["is_emergency"])
    print("Daily Calendar items:", len(res_emg["daily_calendar"]))
