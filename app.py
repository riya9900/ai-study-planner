import streamlit as st
import datetime
from agent import generate_study_plan

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Study Planner Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Styling (CSS)
# ---------------------------------------------------------
st.markdown("""
    <style>
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #4B5563;
            margin-bottom: 1.2rem;
        }
        .stat-box {
            background-color: #F8FAFC;
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid #E2E8F0;
            text-align: center;
        }
        .milestone-card {
            background-color: #EFF6FF;
            border-left: 4px solid #3B82F6;
            padding: 0.9rem;
            border-radius: 6px;
            margin-bottom: 0.75rem;
        }
        .phase-card {
            background-color: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Header Section
# ---------------------------------------------------------
st.markdown('<div class="main-header">📚 AI Study Planner Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Personalized, realistic study curriculum powered by AI reasoning and intelligent scheduling tools.</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Sidebar: User Inputs
# ---------------------------------------------------------
with st.sidebar:
    st.header("🎯 Study Parameters")
    
    subject = st.text_input(
        "Subject / Topic or Exam",
        value=st.session_state.get("prev_subject", ""),
        placeholder="e.g., Python for Data Science, AWS Cloud Practitioner, Calculus II",
        help="What specific subject, exam, or skill are you studying for?"
    )
    
    current_level = st.selectbox(
        "Current Knowledge Level",
        ["Complete Beginner", "Some Basics / Intermediate", "Advanced (Revision & Practice)"],
        index=0,
        help="Select your starting experience level so the agent calibrates topic difficulty."
    )
    
    col_days, col_hours = st.columns(2)
    with col_days:
        total_days = st.number_input(
            "Days Available",
            min_value=3,
            max_value=365,
            value=30,
            step=1,
            help="Total days until your target completion date or exam"
        )
    with col_hours:
        daily_hours = st.number_input(
            "Daily Hours",
            min_value=0.5,
            max_value=12.0,
            value=2.0,
            step=0.5,
            help="Number of hours you can realistically study each day"
        )
        
    learning_style = st.selectbox(
        "Preferred Learning Style",
        [
            "Hands-on / Practical & Projects",
            "Theory & Deep Concept Building",
            "Balanced (Theory + Practice + Quizzes)"
        ],
        index=2,
        help="How do you learn best?"
    )
    
    specific_goals = st.text_area(
        "Focus Areas or Weaknesses (Optional)",
        placeholder="e.g., Prioritize recursion and dynamic programming; skip environment installation.",
        help="Mention any specific chapters, topics, or pain points to customize your curriculum."
    )
    
    generate_btn = st.button("🚀 Generate Study Plan", type="primary", use_container_width=True)

# ---------------------------------------------------------
# Session State: Ensure generated plans persist across clicks
# ---------------------------------------------------------
if "study_plan_result" not in st.session_state:
    st.session_state["study_plan_result"] = None

# Handle Plan Generation
if generate_btn:
    if not subject.strip():
        st.warning("⚠️ Please provide a **Subject / Topic or Exam** in the sidebar to generate your plan.")
    else:
        st.session_state["prev_subject"] = subject
        with st.spinner("🤖 **Agent at work**: Calling scheduling tools, calculating milestone dates, and creating your plan..."):
            try:
                result = generate_study_plan(
                    subject=subject.strip(),
                    total_days=int(total_days),
                    daily_hours=float(daily_hours),
                    current_level=current_level,
                    learning_style=learning_style,
                    specific_goals=specific_goals.strip()
                )
                st.session_state["study_plan_result"] = result
                st.success("✅ Personalized Study Plan generated successfully!")
            except Exception as e:
                st.error(f"❌ Failed to generate study plan: {e}")
                st.info("💡 **Troubleshooting Tip**: Verify your `GEMINI_API_KEY` is properly configured in `.env`.")

# ---------------------------------------------------------
# Display Results (if plan exists in session state)
# ---------------------------------------------------------
plan_result = st.session_state.get("study_plan_result")

if plan_result:
    schedule_data = plan_result.get("schedule_data", {})
    summary = schedule_data.get("summary", {})
    plan_markdown = plan_result.get("plan_markdown", "")
    
    # 1. Metric Summary Cards
    st.subheader(f"📋 Study Roadmap: {subject.strip()}")
    
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    with m_col1:
        st.metric("Total Duration", f"{summary.get('total_days', total_days)} Days")
    with m_col2:
        st.metric("Active Study Days", f"{summary.get('active_study_days', '-')} Days")
    with m_col3:
        st.metric("Buffer / Rest Days", f"{summary.get('buffer_days', '-')} Days")
    with m_col4:
        st.metric("Total Study Budget", f"{summary.get('total_study_hours', '-')} Hours")
    with m_col5:
        st.metric("Daily Pace", f"{summary.get('daily_hours', daily_hours)} hrs/day")
        
    st.divider()
    
    # 2. Main Content Tabs
    tab_plan, tab_timeline, tab_pomodoro = st.tabs([
        "📖 Complete Curriculum",
        "🏁 Milestone & Phase Timeline",
        "⏱️ Daily Pace & Pomodoro"
    ])
    
    # Tab 1: AI Agent Generated Plan (Markdown)
    with tab_plan:
        st.markdown(plan_markdown)
        
        # Download Button
        clean_filename = f"study_plan_{subject.strip().lower().replace(' ', '_')}.md"
        st.download_button(
            label="📥 Download Study Plan as Markdown (.md)",
            data=plan_markdown,
            file_name=clean_filename,
            mime="text/markdown",
            use_container_width=True
        )
        
    # Tab 2: Structured Milestone and Phase Timeline
    with tab_timeline:
        st.markdown("### 🎯 Key Milestone Deadlines")
        st.caption("Calculated by the Agent Tool using precise calendar offsets.")
        
        milestones = schedule_data.get("milestones", [])
        for m in milestones:
            st.markdown(f"""
            <div class="milestone-card">
                <strong>🗓️ {m.get('date')}</strong> — {m.get('milestone')}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("### 📊 Phase Distribution Breakdown")
        phases = schedule_data.get("phases", [])
        for phase in phases:
            st.markdown(f"""
            <div class="phase-card">
                <h4>{phase.get('name')}</h4>
                <p><strong>Timeline:</strong> {phase.get('start_date')} to {phase.get('target_date')} ({phase.get('days')} days)</p>
                <p><strong>Hours Allocated:</strong> {phase.get('allocated_hours')} study hours</p>
            </div>
            """, unsafe_allow_html=True)
            
    # Tab 3: Daily Pace & Productivity Tips
    with tab_pomodoro:
        st.markdown("### ⏱️ Recommended Daily Study Rhythm")
        pomodoro_count = summary.get("daily_pomodoro_sessions", 4)
        
        st.write(f"- **Recommended Daily Sessions:** {pomodoro_count} $\\times$ 25-minute Pomodoro focus blocks.")
        st.write(f"- **Daily Rest Budget:** Take 5 minutes after each block, with a longer 20-minute break after every 4 blocks.")
        st.write(f"- **Buffer Days:** You have **{summary.get('buffer_days', 1)} reserved buffer days** throughout this schedule to catch up or take restful breaks.")
        
        st.markdown("### 🧠 Retention Strategies")
        st.markdown("""
        1. **Active Recall:** Close your notes and write down key concepts from memory before re-reading.
        2. **Spaced Repetition:** Revisit previous topics at the start of each new phase.
        3. **Feynman Technique:** Explain complex concepts in plain language as if teaching a beginner.
        """)

else:
    # Initial Empty State / Welcome Screen
    st.info("👈 **Ready to begin?** Enter your study goal in the sidebar and click **'Generate Study Plan'**.")
    
    col_feature1, col_feature2, col_feature3 = st.columns(3)
    with col_feature1:
        st.markdown("""
        #### 🤖 AI-Powered Agent
        Crafts personalized curricula matching your exact skill level, learning style, and target deadlines.
        """)
    with col_feature2:
        st.markdown("""
        #### 🧮 Built-in Scheduling Tools
        Accurately calculates study hours, phases, and reserves buffer days to protect you from burnout.
        """)
    with col_feature3:
        st.markdown("""
        #### 📥 Download & Track
        Export your complete curriculum as a Markdown document ready for Notion, Obsidian, or printing.
        """)
