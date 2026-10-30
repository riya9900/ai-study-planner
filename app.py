import streamlit as st
import datetime

from agent import generate_study_plan
from syllabus_parser import extract_text_from_upload
from progress_tracker import parse_study_plan_tasks, render_study_progress_tracker

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
            padding: 0.4rem 0.65rem;
            border-radius: 6px;
            font-size: 0.85rem;
            border: 1px solid #059669;
            display: block;
            margin-top: 0.4rem;
            line-height: 1.4;
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
    '<div class="sub-header">Syllabus-grounded, adaptive curriculum engine powered by intelligent AI Agent reasoning.</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Sidebar: Configuration & Inputs
# ---------------------------------------------------------
with st.sidebar:
    st.header("🎯 Study Configuration")

    # 1. Subject or Exam Name
    subject = st.text_input(
        "Subject / Topic or Course Name",
        value=st.session_state.get("prev_subject", ""),
        placeholder="e.g., Operating Systems, Python, AWS Cloud",
        help="What subject are you learning? (If left blank with a syllabus uploaded, it will be detected automatically)."
    )

    # 2. Syllabus File Upload
    st.markdown("### 📚 Upload Your Syllabus")
    uploaded_file = st.file_uploader(
        "Upload Syllabus (PDF, PPTX, DOCX, TXT, Images)",
        type=["pdf", "pptx", "ppt", "docx", "doc", "txt", "png", "jpg", "jpeg"],
        help="Upload lecture slides, syllabus PDFs (digital or scanned), Word documents, or photos. Both text and scanned PDFs are supported automatically."
    )

    syllabus_text = ""
    syllabus_meta = None

    if uploaded_file is not None:
        with st.spinner("Processing syllabus (running digital extraction / AI OCR fallback)..."):
            extracted_txt, meta = extract_text_from_upload(uploaded_file)
            if meta["status"] == "success":
                syllabus_text = extracted_txt
                syllabus_meta = meta
                
                method_label = "AI Vision OCR" if "ocr" in meta["extraction_method"] else "Digital Text"
                st.markdown(
                    f'<div class="badge-success">✅ <strong>Syllabus ready</strong>: {meta["filename"]}<br>'
                    f'Method: {method_label} | Words: {meta["word_count"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.error(f"❌ File read error: {meta['error']}")
    else:
        st.caption("ℹ️ *No file uploaded. Manual topic mode active.*")

    st.divider()

    # 3. Optional Exam Deadline Date Picker
    today = datetime.date.today()
    
    exam_date = st.date_input(
        "🎯 Exam Date / Deadline (Optional)",
        value=None,
        min_value=today,
        max_value=today + datetime.timedelta(days=365),
        help="Optional: If you have an upcoming exam, select the date. Leave blank for self-paced study without deadlines."
    )

    # Dynamic pacing: If exam date is provided, calculate exact countdown; else provide self-paced duration
    if exam_date is not None:
        has_deadline = True
        days_left = max(0, (exam_date - today).days)
        total_days = max(1, days_left)
        is_emergency = days_left <= 3

        day_text = "1 Day Left" if days_left == 1 else f"{days_left} Days Left"
        if is_emergency:
            st.markdown(
                f'<div class="badge-emergency">🚨 <strong>{day_text}!</strong> Emergency Countdown Mode will activate.</div>',
                unsafe_allow_html=True
            )
        else:
            st.caption(f"🗓️ **{day_text}** available until your exam on {exam_date.strftime('%b %d, %Y')}.")
    else:
        has_deadline = False
        is_emergency = False
        total_days = st.number_input(
            "Planned Study Duration (Days)",
            min_value=3,
            max_value=365,
            value=30,
            step=1,
            help="How many days would you like to pace this course over? (Default: 30 days)"
        )
        st.caption(f"ℹ️ **Self-Paced Mode**: No exam deadline set. Pacing over {total_days} days.")

    # 4. Daily Hours & Knowledge Level
    col_hrs, col_lvl = st.columns(2)
    with col_hrs:
        daily_hours = st.number_input(
            "Daily Hours",
            min_value=0.5,
            max_value=14.0,
            value=3.0 if is_emergency else 2.0,
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
        placeholder="e.g., Focus heavily on Deadlocks & CPU Scheduling; skip basic history.",
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
    
    # Auto-detect subject if user left it blank
    if not effective_subject and syllabus_text:
        for line in syllabus_text.splitlines()[:15]:
            if any(k in line.lower() for k in ["course title:", "subject:", "course name:", "course:"]):
                candidate = line.split(":", 1)[-1].strip()
                if candidate:
                    effective_subject = candidate
                    break
        if not effective_subject and syllabus_meta:
            effective_subject = syllabus_meta["filename"].rsplit(".", 1)[0].replace("_", " ").title()

    if not effective_subject:
        st.warning("⚠️ Please provide a **Subject / Course Name** or upload a syllabus file to begin.")
    else:
        st.session_state["prev_subject"] = effective_subject
        
        if is_emergency:
            spinnerText = "🚨 **Agent running in Emergency Crunch Mode**..."
        elif has_deadline:
            spinnerText = "🤖 **Agent at work**: Scheduling against exam deadline and building curriculum..."
        else:
            spinnerText = "🤖 **Agent at work**: Reading syllabus and building comprehensive self-paced plan..."
            
        with st.spinner(spinnerText):
            try:
                exam_date_str = exam_date.strftime("%Y-%m-%d") if exam_date else None
                result = generate_study_plan(
                    subject=effective_subject,
                    total_days=int(total_days),
                    daily_hours=float(daily_hours),
                    current_level=current_level,
                    learning_style=learning_style,
                    specific_goals=specific_goals.strip(),
                    exam_date_str=exam_date_str,
                    syllabus_text=syllabus_text,
                    syllabus_filename=syllabus_meta["filename"] if syllabus_meta else ""
                )
                st.session_state["study_plan_result"] = result
                st.session_state["generated_subject"] = effective_subject
                st.session_state["generated_exam_date"] = exam_date

                # Parse and initialize tasks for progress tracking
                tasks = parse_study_plan_tasks(result.get("plan_markdown", ""), result.get("schedule_data", {}))
                st.session_state["study_tasks"] = tasks
                # Clear any previous task completion state
                for k in list(st.session_state.keys()):
                    if k.startswith("task_"):
                        del st.session_state[k]

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
    plan_has_deadline = plan_result.get("has_deadline", False)
    is_emg = plan_result.get("is_emergency", False) and plan_has_deadline
    has_syl = plan_result.get("has_syllabus", False)
    gen_subj = st.session_state.get("generated_subject", subject)

    # 1. Header Banner (Conditional: Countdown Banner if deadline set, else Self-Paced Banner)
    if plan_has_deadline:
        days_left = summary.get("days_left", 0)
        target_dt_str = summary.get("exam_date", str(st.session_state.get("generated_exam_date", "")))
        
        day_str = "1 DAY" if days_left == 1 else f"{days_left} DAYS"
        if is_emg:
            st.markdown(f"""
            <div class="emergency-banner">
                <h2 style="margin: 0; color: #FEE2E2; font-size: 1.8rem;">🚨 EXAM COUNTDOWN: {day_str} REMAINING</h2>
                <p style="margin: 0.4rem 0 0 0; color: #FECACA; font-size: 1.05rem;">
                    Exam Date: <strong>{target_dt_str}</strong> — <strong>Emergency Mode Active</strong> (High-yield focus, core triage, and rapid drills)
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="countdown-banner">
                <h2 style="margin: 0; color: #38BDF8; font-size: 1.8rem;">🎯 EXAM COUNTDOWN: {day_str} LEFT</h2>
                <p style="margin: 0.4rem 0 0 0; color: #94A3B8; font-size: 1.05rem;">
                    Target Exam Date: <strong>{target_dt_str}</strong> &nbsp;|&nbsp; Start: <strong>{summary.get('start_date')}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Clean Self-Paced Banner (No countdown, no days remaining, no exam pressure)
        st.markdown(f"""
        <div class="countdown-banner">
            <h2 style="margin: 0; color: #38BDF8; font-size: 1.7rem;">📚 SELF-PACED STUDY ROADMAP</h2>
            <p style="margin: 0.4rem 0 0 0; color: #94A3B8; font-size: 1.02rem;">
                Structured <strong>{summary.get('total_days', total_days)}-Day Curriculum</strong> &nbsp;|&nbsp; 
                Daily Commitment: <strong>{summary.get('daily_hours', daily_hours)} hrs/day</strong> &nbsp;|&nbsp; 
                Total Budget: <strong>{summary.get('total_study_hours', '-')} Hours</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 2. Metric Overview Cards
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        tot_d = summary.get('total_days', total_days)
        st.metric("Total Days", f"{tot_d} {'Day' if tot_d == 1 else 'Days'}")
    with m2:
        st.metric("Active Study Days", f"{summary.get('active_study_days', '-')} Days")
    with m3:
        st.metric("Buffer / Rest Days", f"{summary.get('buffer_days', 0)} Days")
    with m4:
        st.metric("Total Study Hours", f"{summary.get('total_study_hours', '-')} hrs")
    with m5:
        st.metric("Daily Pace", f"{summary.get('daily_hours', daily_hours)} hrs/day")

    st.divider()

    # Ensure study tasks are loaded if returning to existing session
    if "study_tasks" not in st.session_state or not st.session_state["study_tasks"]:
        st.session_state["study_tasks"] = parse_study_plan_tasks(plan_markdown, schedule_data)

    # 3. 📊 Study Progress Section
    render_study_progress_tracker(st.session_state.get("study_tasks", []))

    st.divider()

    # 4. Main Content Tabs
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

    # TAB 2: Phase Distribution Breakdown
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
            method_desc = (
                "🤖 AI Vision Multimodal OCR (Scanned / Image Document)"
                if "ocr" in syllabus_meta.get("extraction_method", "") else
                "📄 Direct Digital Text Extraction"
            )
            st.markdown(f"""
            <div class="dark-card">
                <h4>📄 File: {syllabus_meta.get('filename')}</h4>
                <p><strong>Extraction Method:</strong> <span style="color: #38BDF8;">{method_desc}</span></p>
                <p><strong>Type:</strong> {syllabus_meta.get('extension').upper()} &nbsp;|&nbsp; 
                   <strong>Items:</strong> {syllabus_meta.get('page_or_slide_count')} &nbsp;|&nbsp; 
                   <strong>Extracted Words:</strong> {syllabus_meta.get('word_count')}</p>
                <p style="color: #6EE7B7;">✅ The AI Agent strictly grounded the study roadmap in the extracted syllabus topics.</p>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("🔍 View Extracted Syllabus Text"):
                st.text(syllabus_text[:6000] + ("\n... [Truncated for preview]" if len(syllabus_text) > 6000 else ""))
        else:
            st.info("ℹ️ No external syllabus file was uploaded. The plan was constructed using standard subject curriculum.")

else:
    # Initial Empty State / Welcome Screen
    st.info("👈 **To get started:** Upload your syllabus or enter your subject in the sidebar, set an optional exam date, and click **'Generate Study Plan'**.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="dark-card">
            <h4 style="color: #38BDF8;">📚 Digital & Scanned PDF OCR</h4>
            <p>Upload digital PDFs, lecture slides (PPTX), or scanned documents. AI OCR extracts actual units and topics directly.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="dark-card">
            <h4 style="color: #38BDF8;">🎯 Optional Exam Deadline</h4>
            <p>Have an exam? Set a deadline for countdowns and emergency mode. No exam? Enjoy a flexible, self-paced curriculum.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="dark-card">
            <h4 style="color: #38BDF8;">🔥 Prioritized Day-by-Day</h4>
            <p>Outputs clean, beginner-friendly daily cards with explicit <em>Learn</em>, <em>Practice</em>, and <em>Today's Goal</em> checkpoints.</p>
        </div>
        """, unsafe_allow_html=True)
