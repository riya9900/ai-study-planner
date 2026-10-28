import streamlit as st
import datetime

from agent import generate_study_plan
from syllabus_parser import extract_text_from_upload

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
# Comprehensive Dark-First CSS Styling
# ---------------------------------------------------------
st.markdown("""
    <style>
        /* Base typography & headers */
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #38BDF8;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #94A3B8;
            margin-bottom: 1.2rem;
        }
        
        /* Dark theme cards (ensures NO white/blank boxes) */
        .dark-card {
            background-color: #1E293B !important;
            border: 1px solid #334155 !important;
            border-radius: 10px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            color: #F8FAFC !important;
        }
        
        .milestone-dark-card {
            background-color: #1E293B !important;
            border: 1px solid #334155 !important;
            border-left: 5px solid #38BDF8 !important;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            color: #F8FAFC !important;
        }
        
        .phase-dark-card {
            background-color: #1E293B !important;
            border: 1px solid #334155 !important;
            border-radius: 8px;
            padding: 1.1rem;
            margin-bottom: 0.85rem;
            color: #F8FAFC !important;
        }
        
        .phase-title {
            color: #38BDF8 !important;
            font-size: 1.15rem;
            font-weight: 600;
            margin-bottom: 0.4rem;
        }
        
        .phase-meta {
            color: #94A3B8 !important;
            font-size: 0.95rem;
            margin: 0.2rem 0;
        }
        
        /* Visual Timeline Progress Bar */
        .timeline-bar-container {
            display: flex;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            background-color: #0F172A;
            border: 1px solid #334155;
            margin: 1rem 0 1.5rem 0;
        }
        
        /* Countdown Banners */
        .countdown-banner {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%) !important;
            border: 1px solid #38BDF8 !important;
            border-radius: 10px;
            padding: 1.2rem;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        
        .emergency-banner {
            background: linear-gradient(135deg, #450A0A 0%, #7F1D1D 100%) !important;
            border: 2px solid #EF4444 !important;
            border-radius: 10px;
            padding: 1.2rem;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        
        .badge-success {
            background-color: #064E3B;
            color: #6EE7B7;
            padding: 0.35rem 0.6rem;
            border-radius: 6px;
            font-size: 0.85rem;
            border: 1px solid #059669;
            display: inline-block;
            margin-top: 0.3rem;
        }
        
        .badge-emergency {
            background-color: #7F1D1D;
            color: #FCA5A5;
            padding: 0.35rem 0.6rem;
            border-radius: 6px;
            font-size: 0.85rem;
            border: 1px solid #DC2626;
            display: inline-block;
            margin-top: 0.3rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Application Header
# ---------------------------------------------------------
st.markdown('<div class="main-header">📚 AI Study Planner Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Deadline-driven, syllabus-grounded curriculum engine powered by intelligent AI Agent reasoning.</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Sidebar: Configuration & Inputs
# ---------------------------------------------------------
with st.sidebar:
    st.header("🎯 Study Configuration")

    # 1. Subject or Exam Name
    subject = st.text_input(
        "Subject / Topic or Exam Name",
        value=st.session_state.get("prev_subject", ""),
        placeholder="e.g., Python Programming, Operating Systems, AWS Cloud",
        help="What subject or exam are you preparing for?"
    )

    # 2. Syllabus File Upload Section
    st.markdown("### 📚 Upload Your Syllabus")
    uploaded_file = st.file_uploader(
        "Upload Syllabus (PDF, PPTX, DOCX, TXT)",
        type=["pdf", "pptx", "ppt", "docx", "doc", "txt"],
        help="Upload your university syllabus or lecture slides. The AI will extract actual units and topics."
    )

    syllabus_text = ""
    syllabus_meta = None

    if uploaded_file is not None:
        with st.spinner("Extracting syllabus content..."):
            extracted_txt, meta = extract_text_from_upload(uploaded_file)
            if meta["status"] == "success":
                syllabus_text = extracted_txt
                syllabus_meta = meta
                st.markdown(
                    f'<div class="badge-success">✅ Syllabus ready: {meta["filename"]} '
                    f'({meta["page_or_slide_count"]} items, {meta["word_count"]} words)</div>',
                    unsafe_allow_html=True
                )
            else:
                st.error(f"❌ File read error: {meta['error']}")
    else:
        st.caption("ℹ️ *No file uploaded. Manual topic mode active.*")

    st.divider()

    # 3. Exam Deadline Date Picker
    today = datetime.date.today()
    default_exam_date = today + datetime.timedelta(days=14)
    
    exam_date = st.date_input(
        "🎯 Exam Date / Deadline",
        value=default_exam_date,
        min_value=today,
        max_value=today + datetime.timedelta(days=365),
        help="The planner will strictly schedule within the days remaining until this date."
    )

    # Calculate actual available days (inclusive of today)
    raw_days_left = (exam_date - today).days
    total_days = max(1, raw_days_left + 1)
    is_emergency = total_days <= 3

    if is_emergency:
        st.markdown(
            f'<div class="badge-emergency">🚨 <strong>{total_days} Day(s) Left!</strong> Emergency Countdown Mode will activate.</div>',
            unsafe_allow_html=True
        )
    else:
        st.caption(f"🗓️ **{total_days} days** available until your exam on {exam_date.strftime('%b %d, %Y')}.")

    # 4. Daily Hours & Knowledge Level
    col_hrs, col_lvl = st.columns(2)
    with col_hrs:
        daily_hours = st.number_input(
            "Daily Hours",
            min_value=0.5,
            max_value=14.0,
            value=2.5 if is_emergency else 2.0,
            step=0.5,
            help="How many hours can you study each day?"
        )
    with col_lvl:
        current_level = st.selectbox(
            "Knowledge Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=0
        )

    # 5. Preferred Learning Style
    learning_style = st.selectbox(
        "Learning Style",
        [
            "Balanced (Theory + Practice + MCQs)",
            "Hands-on / Practical & Problem Solving",
            "Concept First & High-Yield Definitions"
        ],
        index=0
    )

    # 6. Specific Focus or Weaknesses
    specific_goals = st.text_area(
        "Priority Topics / Weaknesses (Optional)",
        placeholder="e.g., Focus heavily on Unit 3; skip basic installation.",
        help="Any topics you find especially difficult or want to prioritize?"
    )

    generate_btn = st.button("🚀 Generate Study Plan", type="primary", use_container_width=True)

# ---------------------------------------------------------
# Session State Management
# ---------------------------------------------------------
if "study_plan_result" not in st.session_state:
    st.session_state["study_plan_result"] = None

# Handle Plan Generation
if generate_btn:
    effective_subject = subject.strip()
    if not effective_subject and syllabus_meta:
        # Auto-derive subject from syllabus filename if omitted
        effective_subject = syllabus_meta["filename"].rsplit(".", 1)[0].replace("_", " ").title()

    if not effective_subject:
        st.warning("⚠️ Please provide a **Subject / Exam Name** or upload a syllabus file to begin.")
    else:
        st.session_state["prev_subject"] = effective_subject
        spinnerText = (
            "🚨 **Agent running in Emergency Crunch Mode**..."
            if is_emergency else
            "🤖 **Agent at work**: Reading syllabus, calculating milestones, and building daily schedule..."
        )
        with st.spinner(spinnerText):
            try:
                result = generate_study_plan(
                    subject=effective_subject,
                    total_days=total_days,
                    daily_hours=float(daily_hours),
                    current_level=current_level,
                    learning_style=learning_style,
                    specific_goals=specific_goals.strip(),
                    exam_date_str=exam_date.strftime("%Y-%m-%d"),
                    syllabus_text=syllabus_text,
                    syllabus_filename=syllabus_meta["filename"] if syllabus_meta else ""
                )
                st.session_state["study_plan_result"] = result
                st.session_state["generated_subject"] = effective_subject
                st.session_state["generated_exam_date"] = exam_date
                st.success("✅ Personalized Study Plan generated successfully!")
            except Exception as e:
                st.error(f"❌ Generation error: {e}")
                st.info("💡 Make sure your `GEMINI_API_KEY` is set in `.env`.")

# ---------------------------------------------------------
# Display Generated Plan
# ---------------------------------------------------------
plan_result = st.session_state.get("study_plan_result")

if plan_result:
    schedule_data = plan_result.get("schedule_data", {})
    summary = schedule_data.get("summary", {})
    plan_markdown = plan_result.get("plan_markdown", "")
    is_emg = plan_result.get("is_emergency", False)
    has_syl = plan_result.get("has_syllabus", False)
    gen_subj = st.session_state.get("generated_subject", subject)

    # 1. Prominent Exam Countdown Banner
    days_left = summary.get("days_left", 0)
    target_dt_str = summary.get("exam_date", str(exam_date))
    
    if is_emg:
        st.markdown(f"""
        <div class="emergency-banner">
            <h2 style="margin: 0; color: #FEE2E2; font-size: 1.8rem;">🚨 EXAM COUNTDOWN: {days_left + 1} DAY{'S' if (days_left + 1) != 1 else ''} REMAINING</h2>
            <p style="margin: 0.4rem 0 0 0; color: #FECACA; font-size: 1.05rem;">
                Exam Date: <strong>{target_dt_str}</strong> — <strong>Emergency Mode Active</strong> (High-yield focus, core triage, and rapid drills)
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="countdown-banner">
            <h2 style="margin: 0; color: #38BDF8; font-size: 1.8rem;">🎯 EXAM COUNTDOWN: {days_left} DAYS LEFT</h2>
            <p style="margin: 0.4rem 0 0 0; color: #94A3B8; font-size: 1.05rem;">
                Target Exam Date: <strong>{target_dt_str}</strong> &nbsp;|&nbsp; Start: <strong>{summary.get('start_date')}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 2. Metric Overview Cards
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Total Days", f"{summary.get('total_days', total_days)} Days")
    with m2:
        st.metric("Active Study Days", f"{summary.get('active_study_days', '-')} Days")
    with m3:
        st.metric("Buffer / Rest Days", f"{summary.get('buffer_days', 0)} Days")
    with m4:
        st.metric("Total Study Hours", f"{summary.get('total_study_hours', '-')} hrs")
    with m5:
        st.metric("Daily Pace", f"{summary.get('daily_hours', daily_hours)} hrs/day")

    st.divider()

    # 3. Main Content Tabs
    tab_roadmap, tab_timeline, tab_pomodoro, tab_source = st.tabs([
        "📅 Day-by-Day Study Roadmap",
        "🏁 Milestone & Phase Breakdown",
        "⏱️ Daily Pace & Pomodoro",
        "📚 Syllabus Source Details"
    ])

    # TAB 1: Complete Roadmap
    with tab_roadmap:
        st.markdown(plan_markdown)
        
        # Download Button
        clean_name = f"study_plan_{gen_subj.lower().replace(' ', '_')}.md"
        st.download_button(
            label="📥 Download Study Plan (.md)",
            data=plan_markdown,
            file_name=clean_name,
            mime="text/markdown",
            use_container_width=True
        )

    # TAB 2: Phase Distribution Breakdown (Pure CSS/HTML, zero pandas/altair)
    with tab_timeline:
        st.markdown("### 📊 Phase Distribution Breakdown")
        phases = schedule_data.get("phases", [])
        
        if phases:
            total_phase_days = sum(p.get("days", 1) for p in phases) or 1
            phase_colors = ["#38BDF8", "#818CF8", "#F43F5E"]

            # Visual Multi-Segment Timeline Bar
            segments_html = []
            for i, p in enumerate(phases):
                color = phase_colors[i % len(phase_colors)]
                p_days = p.get("days", 1)
                p_name = p.get("name", f"Phase {i+1}")
                p_pct = round((p_days / total_phase_days) * 100, 1)
                segments_html.append(
                    f'<div style="width: {p_pct}%; background-color: {color};" '
                    f'title="{p_name}: {p_days} days ({p_pct}%)"></div>'
                )

            st.markdown(f"""
            <div class="timeline-bar-container">
                {''.join(segments_html)}
            </div>
            """, unsafe_allow_html=True)

            # Render Dark Phase Cards with Individual Progress Bars
            for i, p in enumerate(phases):
                color = phase_colors[i % len(phase_colors)]
                p_days = p.get("days", 1)
                p_pct = round((p_days / total_phase_days) * 100, 1)
                
                st.markdown(f"""
                <div class="phase-dark-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                        <span class="phase-title">{p.get('name')}</span>
                        <span style="background: #0F172A; padding: 2px 8px; border-radius: 4px; font-size: 0.85rem; border: 1px solid #334155; color: {color}; font-weight: 600;">
                            {p_pct}% of timeline ({p_days} days)
                        </span>
                    </div>
                    <div style="background: #0F172A; border-radius: 4px; height: 7px; margin: 0.4rem 0 0.8rem 0; overflow: hidden; border: 1px solid #334155;">
                        <div style="width: {p_pct}%; height: 100%; background: {color}; border-radius: 4px;"></div>
                    </div>
                    <div class="phase-meta">📅 <strong>Timeline:</strong> {p.get('start_date')} to {p.get('target_date')} ({p.get('days')} days)</div>
                    <div class="phase-meta">⏰ <strong>Allocated Hours:</strong> {p.get('allocated_hours')} study hours</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("### 🎯 Key Milestone Deadlines")
        milestones = schedule_data.get("milestones", [])
        for m in milestones:
            st.markdown(f"""
            <div class="milestone-dark-card">
                <span style="font-size: 1.1rem; color: #38BDF8;">🗓️ <strong>{m.get('date')}</strong></span> &nbsp;—&nbsp;
                <span style="color: #F8FAFC;">{m.get('milestone')}</span>
            </div>
            """, unsafe_allow_html=True)

    # TAB 3: Daily Pace & Productivity
    with tab_pomodoro:
        st.markdown("### ⏱️ Recommended Daily Study Rhythm")
        pomo_blocks = summary.get("daily_pomodoro_sessions", 4)
        
        st.markdown(f"""
        <div class="dark-card">
            <h4>🍅 Pomodoro Session Schedule</h4>
            <p>For your <strong>{summary.get('daily_hours')} daily hours</strong>, complete <strong>{pomo_blocks} focus intervals</strong>:</p>
            <ul>
                <li><strong>25 Minutes:</strong> Deep focus (active note-taking, problem solving, or MCQ drills).</li>
                <li><strong>5 Minutes:</strong> Physical break (stand up, drink water, rest your eyes).</li>
                <li><strong>After 4 intervals:</strong> Take a 20-30 minute long rest.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🧠 High-Retention Revision Strategies")
        st.markdown("""
        1. **Active Recall:** Cover your syllabus notes and write down key concepts from memory before re-reading.
        2. **Spaced Repetition:** Re-test key definitions and formulas at the start of each new phase.
        3. **Feynman Technique:** Explain complex syllabus topics out loud in simple, beginner terms.
        """)

    # TAB 4: Syllabus Source Details
    with tab_source:
        st.markdown("### 📚 Syllabus Source & Processing")
        if has_syl and syllabus_meta:
            st.markdown(f"""
            <div class="dark-card">
                <h4>📄 File: {syllabus_meta.get('filename')}</h4>
                <p><strong>Type:</strong> {syllabus_meta.get('extension').upper()} &nbsp;|&nbsp; 
                   <strong>Items (Pages/Slides):</strong> {syllabus_meta.get('page_or_slide_count')} &nbsp;|&nbsp; 
                   <strong>Extracted Words:</strong> {syllabus_meta.get('word_count')}</p>
                <p style="color: #6EE7B7;">✅ The AI Agent strictly used this document as the primary syllabus foundation.</p>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("🔍 View Extracted Syllabus Text"):
                st.text(syllabus_text[:5000] + ("\n... [Truncated for preview]" if len(syllabus_text) > 5000 else ""))
        else:
            st.info("ℹ️ No external syllabus file was uploaded. The plan was constructed using standard subject curriculum.")

else:
    # Initial Empty State / Welcome Screen
    st.info("👈 **To get started:** Enter your exam date and subject in the sidebar, or upload your syllabus, then click **'Generate Study Plan'**.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="dark-card">
            <h4 style="color: #38BDF8;">📚 Real Syllabus Grounding</h4>
            <p>Upload lecture slides (PPTX), PDF syllabi, or Word documents. The agent directly extracts actual units and topics instead of inventing generic curricula.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="dark-card">
            <h4 style="color: #38BDF8;">🎯 Exact Exam Countdown</h4>
            <p>Calculates remaining days until your deadline. Automatically triggers <strong>Emergency Mode</strong> for tight deadlines (<= 3 days).</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="dark-card">
            <h4 style="color: #38BDF8;">🔥 Prioritized Day-by-Day</h4>
            <p>Outputs clean, beginner-friendly daily cards with explicit <em>Learn</em>, <em>Practice</em>, and <em>Today's Goal</em> checkpoints.</p>
        </div>
        """, unsafe_allow_html=True)
