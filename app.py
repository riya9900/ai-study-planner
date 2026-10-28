import streamlit as st
import datetime

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
            font-size: 2.3rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #4B5563;
            margin-bottom: 1.5rem;
        }
        .card {
            background-color: #F8FAFC;
            border-radius: 10px;
            padding: 1.2rem;
            border: 1px solid #E2E8F0;
            margin-bottom: 1rem;
        }
        .highlight {
            color: #2563EB;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Header Section
# ---------------------------------------------------------
st.markdown('<div class="main-header">📚 AI Study Planner Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Create a realistic, customized study curriculum powered by AI reasoning and scheduling tools.</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Sidebar: User Inputs
# ---------------------------------------------------------
with st.sidebar:
    st.header("🎯 Your Study Goals")
    
    subject = st.text_input(
        "Subject / Topic or Exam",
        placeholder="e.g., Python for Beginners, AWS Cloud Practitioner, Calculus I",
        help="What do you want to learn or prepare for?"
    )
    
    current_level = st.selectbox(
        "Current Knowledge Level",
        ["Complete Beginner", "Some Basics / Intermediate", "Advanced (Revision & Practice)"],
        index=0
    )
    
    col_days, col_hours = st.columns(2)
    with col_days:
        total_days = st.number_input(
            "Days Available",
            min_value=3,
            max_value=365,
            value=30,
            step=1,
            help="Total number of days until your exam or goal"
        )
    with col_hours:
        daily_hours = st.number_input(
            "Daily Hours",
            min_value=0.5,
            max_value=12.0,
            value=2.0,
            step=0.5,
            help="How many hours can you commit each day?"
        )
        
    learning_style = st.selectbox(
        "Preferred Learning Style",
        [
            "Hands-on / Practical & Projects",
            "Theory & Deep Concept Building",
            "Balanced (Theory + Practice + Quizzes)"
        ],
        index=2
    )
    
    specific_goals = st.text_area(
        "Specific Topics or Focus Areas (Optional)",
        placeholder="e.g., Focus on OOP and data structures, skip setup basics.",
        help="Any topics you struggle with or want to prioritize?"
    )
    
    generate_btn = st.button("🚀 Generate Study Plan", type="primary", use_container_width=True)

# ---------------------------------------------------------
# Main Page: Results & Preview
# ---------------------------------------------------------
if generate_btn:
    if not subject.strip():
        st.warning("⚠️ Please enter a Subject or Exam name in the sidebar to begin!")
    else:
        # Temporary UI confirmation for Step 2
        st.success(f"🎯 Inputs received! Ready to build plan for: **{subject}**")
        
        # Stat cards showing quick summary of study parameters
        total_study_hours = total_days * daily_hours
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        with stat_col1:
            st.metric("Total Duration", f"{total_days} Days")
        with stat_col2:
            st.metric("Daily Commitment", f"{daily_hours} hrs/day")
        with stat_col3:
            st.metric("Total Study Budget", f"{total_study_hours:.0f} Hours")
        with stat_col4:
            st.metric("Level", current_level.split()[0])
            
        st.divider()
        
        # Tabs for previewing how the final plan will be presented
        tab_plan, tab_milestones, tab_tips = st.tabs(["📅 Study Schedule", "🏁 Milestone Timeline", "💡 Study Strategies"])
        
        with tab_plan:
            st.info("🤖 **Step 2 UI Preview**: In Step 3 & 4, the AI Agent will populate your comprehensive weekly breakdown here.")
            st.markdown(f"""
            ### Sample Plan Preview for *{subject}*
            - **Phase 1: Foundations** (~{int(total_days * 0.4)} days)
            - **Phase 2: Core Mastery & Problem Solving** (~{int(total_days * 0.4)} days)
            - **Phase 3: Review, Practice Tests & Buffer** (~{int(total_days * 0.2)} days)
            """)
            
        with tab_milestones:
            st.markdown("### 🎯 Key Milestone Deadlines")
            st.write(f"- **Day 1**: Orientation & foundational principles.")
            st.write(f"- **Day {int(total_days * 0.5)}**: Mid-point assessment and mini-project.")
            st.write(f"- **Day {int(total_days * 0.85)}**: Final mock exam and review.")
            st.write(f"- **Day {total_days}**: Goal Completion!")
            
        with tab_tips:
            st.markdown("### 🧠 Agent Recommendations")
            st.write(f"- Tailored for **{learning_style}**.")
            st.write(f"- Break your {daily_hours} daily hours into 25-minute Pomodoro sessions.")
            st.write("- Allocate 1 day each week as a buffer catch-up day.")

else:
    # Default Welcome Screen before clicking Generate
    st.info("👈 **Get Started**: Fill in your study goals in the sidebar and click **'Generate Study Plan'**.")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("""
        ### Why Use the AI Study Planner?
        - **Realistic Pacing:** Calculates exact hours so you never burn out.
        - **Built-in Buffer Days:** Protects your schedule against unexpected delays.
        - **Tailored to You:** Adjusts depth based on your starting skill level.
        """)
    with col_info2:
        st.markdown("""
        ### How It Works
        1. **Input Your Target:** Share the topic, timeline, and available hours.
        2. **Agent Reasoning:** The AI Agent uses scheduling tools to divide the curriculum.
        3. **Structured Plan:** Receive an actionable, day-by-day roadmap.
        """)

