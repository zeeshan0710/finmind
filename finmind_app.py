import streamlit as st
import openai
import json

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinMind – Daily Financial Education",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.block-container { max-width: 720px; padding-top: 1.5rem; padding-bottom: 3rem; }

.lesson-card {
    background: linear-gradient(135deg, #0F6E56 0%, #1D9E75 100%);
    border-radius: 20px; padding: 2rem; color: white; margin: 0.75rem 0;
    position: relative; overflow: hidden;
}
.lesson-card::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 150px; height: 150px; border-radius: 50%;
    background: rgba(255,255,255,0.07);
}
.lesson-card h2 { color: white; margin: 0 0 0.5rem; font-size: 1.3rem; }
.lesson-card p  { color: rgba(255,255,255,0.88); margin: 0; line-height: 1.6; font-size: 0.95rem; }
.lesson-card .badge {
    display: inline-block; background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.3); border-radius: 20px;
    padding: 3px 12px; font-size: 12px; color: white; margin-bottom: 0.75rem;
}

.takeaway-card {
    background: #F0FDF8; border: 1.5px solid #9FE1CB;
    border-radius: 14px; padding: 1.1rem 1.25rem; margin: 0.5rem 0;
}
.takeaway-card h4 { color: #085041; margin: 0 0 0.4rem; font-size: 0.9rem;
    text-transform: uppercase; letter-spacing: 0.5px; }
.takeaway-card p  { color: #0F6E56; margin: 0; font-size: 0.93rem; line-height: 1.5; }

.quiz-option        { border: 1.5px solid #e0e0e0; border-radius: 12px;
    padding: 0.75rem 1rem; margin: 0.4rem 0; font-size: 0.94rem; }
.quiz-correct       { border-color: #1D9E75 !important; background: #E1F5EE; color: #085041; }

.stat-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #F0FDF8; border: 1px solid #9FE1CB;
    border-radius: 30px; padding: 6px 14px;
    font-size: 13px; font-weight: 500; color: #085041;
}

.xp-bar-wrap { background: #E1F5EE; border-radius: 10px; height: 10px; margin: 4px 0 12px; }
.xp-bar-fill { background: linear-gradient(90deg, #0F6E56, #1D9E75); border-radius: 10px; height: 10px; }

.persona-chip {
    display: inline-block;
    background: linear-gradient(135deg, #0F6E56, #1D9E75);
    color: white; border-radius: 20px; padding: 4px 14px;
    font-size: 13px; font-weight: 500;
}

.chat-ai   { background: #F0FDF8; border: 1px solid #9FE1CB;
    border-radius: 16px 16px 16px 4px; padding: 0.7rem 1rem;
    margin: 0.35rem 0; font-size: 0.92rem; color: #0a3d2e; }
.chat-user { background: #0F6E56; border-radius: 16px 16px 4px 16px;
    padding: 0.7rem 1rem; margin: 0.35rem 0;
    font-size: 0.92rem; color: white; text-align: right; }

div[data-testid="stButton"] > button { border-radius: 12px; font-weight: 500; }
div[data-testid="stButton"] > button[kind="primary"] {
    background: #0F6E56; border: none; color: white;
}
div[data-testid="stButton"] > button[kind="primary"]:hover { background: #085041; }
</style>
""", unsafe_allow_html=True)

# ── Data ───────────────────────────────────────────────────────────────────────
TOPICS = {
    "Budgeting":      {"emoji": "📊", "color": "#1D9E75"},
    "Saving":         {"emoji": "🏦", "color": "#185FA5"},
    "Investing":      {"emoji": "📈", "color": "#534AB7"},
    "Credit & Debt":  {"emoji": "💳", "color": "#993556"},
    "Taxes":          {"emoji": "🧾", "color": "#BA7517"},
    "Insurance":      {"emoji": "🛡️", "color": "#3B6D11"},
    "Real Estate":    {"emoji": "🏠", "color": "#993C1D"},
    "Retirement":     {"emoji": "🌴", "color": "#0C447C"},
}

PERSONAS = {
    "The Impulse Optimist":   {"emoji": "✨", "focus": ["Budgeting", "Saving"]},
    "The Anxious Planner":    {"emoji": "📋", "focus": ["Investing", "Retirement"]},
    "The Calm Analyst":       {"emoji": "🔍", "focus": ["Investing", "Taxes"]},
    "The Flowing Adventurer": {"emoji": "🌊", "focus": ["Budgeting", "Credit & Debt"]},
}

ONBOARDING_QS = [
    {"q": "When you get paid, what's the first thing you do?",
     "opts": ["Pay bills immediately", "Transfer some to savings", "Treat myself a little", "Check balance and figure it out"]},
    {"q": "How do you feel when you check your bank balance?",
     "opts": ["Anxious — I avoid it", "Calm and in control", "Curious and analytical", "Surprised every time"]},
    {"q": "How would you describe your current financial knowledge?",
     "opts": ["Total beginner", "I know the basics", "Comfortable with most topics", "Pretty advanced"]},
    {"q": "What's your #1 financial goal right now?",
     "opts": ["Stop living paycheck to paycheck", "Build an emergency fund", "Start investing", "Grow existing wealth"]},
    {"q": "How many minutes a day would you spend on financial education?",
     "opts": ["Just 1–2 mins", "About 5 mins", "10–15 mins", "As long as it takes"]},
]

# ── Session state ──────────────────────────────────────────────────────────────
DEFAULTS = {
    "screen": "onboarding",
    "q_index": 0,
    "answers": [],
    "persona": None,
    "xp": 0,
    "streak": 0,
    "completed_topics": [],
    "chat_history": [],
    "current_lesson": None,
    "quiz_state": None,
    "quiz_correct": None,
    "lessons_done": 0,
    "active_topic": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ────────────────────────────────────────────────────────────────────
def go(screen):
    st.session_state.screen = screen
    st.rerun()

def compute_persona(answers):
    names = list(PERSONAS.keys())
    freq = [0, 0, 0, 0]
    for a in answers:
        freq[a % 4] += 1
    return names[freq.index(max(freq))]

def level_info(xp):
    if xp < 50:   return 1, "Beginner",    0,   50
    if xp < 150:  return 2, "Learner",    50,  150
    if xp < 300:  return 3, "Explorer",  150,  300
    if xp < 500:  return 4, "Investor",  300,  500
    return 5, "FinMind Pro", 500, 700

# ── Claude helpers ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return openai.OpenAI(api_key=st.secrets["openai_api_key"])

def generate_lesson(topic, persona_name, lvl_name):
    client = get_client()
    prompt = f"""Generate a bite-sized financial education lesson for a "{persona_name}" at "{lvl_name}" level on topic: "{topic}".

Return ONLY valid JSON (no markdown fences) with exactly this schema:
{{
  "title": "punchy title max 8 words",
  "hook": "one engaging opening sentence max 20 words",
  "body": "core lesson in 3-4 sentences. Concrete, practical, jargon-free with one real example or number.",
  "analogy": "one memorable analogy 1-2 sentences",
  "takeaways": ["takeaway 1", "takeaway 2", "takeaway 3"],
  "emoji": "single emoji",
  "quiz_question": "a clear multiple-choice question testing understanding",
  "quiz_options": ["option A", "option B", "option C", "option D"],
  "quiz_answer_index": 0,
  "quiz_explanation": "2 sentence explanation of correct answer"
}}"""
    r = get_client().chat.completions.create(
        model="gpt-4",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = r.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

def ask_tutor(user_msg, lesson, persona_name, history):
    system = (
        f"You are FinMind, a witty and supportive financial education tutor. "
        f"The student's money persona is '{persona_name}'. "
        f"They just learned about: {lesson['title']}. "
        f"Answer follow-up questions clearly and briefly (2-4 sentences). "
        f"Connect advice to their persona. Use concrete examples. Be warm. No bullet points."
    )
    msgs = list(history) + [{"role": "user", "content": user_msg}]
    r = get_client().chat.completions.create(
        model="gpt-4",
        max_tokens=300,
        messages=[{"role": "system", "content": system}] + msgs,
    )
    return r.choices[0].message.content

# ── Shared header ──────────────────────────────────────────────────────────────
def render_header():
    xp = st.session_state.xp
    lvl, lvl_name, xp_prev, xp_next = level_info(xp)
    streak = st.session_state.streak
    xp_pct = min(100, int((xp - xp_prev) / max(1, xp_next - xp_prev) * 100))

    c1, c2, c3 = st.columns([2.5, 1, 1])
    with c1:
        st.markdown("## 🧠 Fin**Mind**")
    with c2:
        st.markdown(f'<div class="stat-pill">🔥 {streak}d streak</div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-pill">⭐ {xp} XP Lv{lvl}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="xp-bar-wrap"><div class="xp-bar-fill" style="width:{xp_pct}%"></div></div>',
        unsafe_allow_html=True,
    )

    n1, n2, n3, n4 = st.columns(4)
    nav = [("🏠 Home", "home"), ("📚 Learn", "topic_select"), ("💬 Tutor", "chat"), ("📈 Progress", "progress")]
    for col, (label, scr) in zip([n1, n2, n3, n4], nav):
        with col:
            if st.button(label, use_container_width=True, key=f"nav_{scr}"):
                go(scr)
    st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# ONBOARDING
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.screen == "onboarding":
    st.markdown("# 🧠 Fin**Mind**")
    st.markdown("##### Daily bite-sized financial education, powered by AI")
    st.markdown("*5 quick questions to personalize your learning path.*")
    st.divider()

    qi = st.session_state.q_index
    st.progress((qi + 1) / len(ONBOARDING_QS), text=f"Step {qi + 1} of {len(ONBOARDING_QS)}")

    q = ONBOARDING_QS[qi]
    st.markdown(f"### {q['q']}")
    choice = st.radio("", q["opts"], index=None, key=f"ob_{qi}", label_visibility="collapsed")

    _, col = st.columns([3, 1])
    with col:
        if st.button("Next →", disabled=choice is None, type="primary", use_container_width=True):
            st.session_state.answers.append(q["opts"].index(choice))
            if qi + 1 < len(ONBOARDING_QS):
                st.session_state.q_index += 1
                st.rerun()
            else:
                st.session_state.persona = compute_persona(st.session_state.answers)
                st.session_state.xp = 10
                st.session_state.streak = 1
                go("home")

# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "home":
    render_header()
    persona = st.session_state.persona
    p_meta  = PERSONAS[persona]
    _, lvl_name, _, _ = level_info(st.session_state.xp)

    st.markdown(f'<span class="persona-chip">{p_meta["emoji"]} {persona}</span>', unsafe_allow_html=True)
    st.markdown("### Good day! Ready for today's Money Minute?")
    st.markdown("Pick a topic — we'll generate a fresh AI lesson tailored to you.")

    # Recommended
    st.markdown("#### ✨ Recommended for you")
    focus = p_meta["focus"]
    cols  = st.columns(len(focus))
    for col, topic in zip(cols, focus):
        meta = TOPICS[topic]
        with col:
            st.markdown(
                f"""<div style="background:{meta['color']}18; border:1.5px solid {meta['color']}66;
                border-radius:14px; padding:1.1rem; text-align:center;">
                <div style="font-size:2rem">{meta['emoji']}</div>
                <div style="font-weight:600;font-size:0.95rem;margin-top:6px">{topic}</div>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button(f"Start {topic}", key=f"rec_{topic}", use_container_width=True, type="primary"):
                st.session_state.active_topic = topic
                st.session_state.current_lesson = None
                go("lesson")

    # All topics grid
    st.markdown("#### 📚 All topics")
    all_topics = list(TOPICS.keys())
    for row_start in range(0, len(all_topics), 4):
        row = all_topics[row_start:row_start + 4]
        cols = st.columns(len(row))
        for col, topic in zip(cols, row):
            meta = TOPICS[topic]
            done = topic in st.session_state.completed_topics
            with col:
                label = f"{meta['emoji']} {topic}" + (" ✓" if done else "")
                if st.button(label, key=f"all_{topic}", use_container_width=True):
                    st.session_state.active_topic = topic
                    st.session_state.current_lesson = None
                    go("lesson")

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("📖 Lessons done",    st.session_state.lessons_done)
    with c2: st.metric("🗂️ Topics explored", len(st.session_state.completed_topics))
    with c3: st.metric("🏅 Level",           lvl_name)

# ══════════════════════════════════════════════════════════════════════════════
# TOPIC SELECT (from nav)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "topic_select":
    render_header()
    st.markdown("### 📚 Choose a topic")
    for topic, meta in TOPICS.items():
        done = topic in st.session_state.completed_topics
        c1, c2, c3 = st.columns([1, 4, 1])
        with c1: st.markdown(f"**{meta['emoji']}**")
        with c2: st.markdown(f"**{topic}**" + ("  ✅" if done else ""))
        with c3:
            if st.button("Go", key=f"ts_{topic}", use_container_width=True, type="primary"):
                st.session_state.active_topic = topic
                st.session_state.current_lesson = None
                go("lesson")

# ══════════════════════════════════════════════════════════════════════════════
# LESSON
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "lesson":
    render_header()
    topic   = st.session_state.active_topic
    persona = st.session_state.persona
    _, lvl_name, _, _ = level_info(st.session_state.xp)
    meta    = TOPICS[topic]

    # Generate lesson if needed
    cur = st.session_state.current_lesson
    if cur is None or cur.get("_topic") != topic:
        with st.spinner(f"Generating your {topic} lesson with AI..."):
            lesson = generate_lesson(topic, persona, lvl_name)
            lesson["_topic"] = topic
            st.session_state.current_lesson = lesson
            st.session_state.quiz_state   = None
            st.session_state.quiz_correct = None
            st.session_state.chat_history = []

    lesson = st.session_state.current_lesson

    # Hero card
    st.markdown(
        f"""<div class="lesson-card">
        <div class="badge">{meta['emoji']} {topic} · {lvl_name}</div>
        <h2>{lesson['emoji']} {lesson['title']}</h2>
        <p><em>{lesson['hook']}</em></p>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("#### The lesson")
    st.markdown(lesson["body"])

    st.markdown(
        f"""<div class="takeaway-card">
        <h4>💡 Think of it this way</h4>
        <p>{lesson['analogy']}</p>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("#### Key takeaways")
    for t in lesson["takeaways"]:
        st.markdown(f"✅ {t}")

    st.divider()

    # Quiz
    st.markdown("#### 🧠 Quick quiz — test yourself")
    st.markdown(f"**{lesson['quiz_question']}**")

    qs = st.session_state.quiz_state
    qc = st.session_state.quiz_correct

    for i, opt in enumerate(lesson["quiz_options"]):
        if qs is None:
            if st.button(opt, key=f"opt_{i}", use_container_width=True):
                correct = (i == lesson["quiz_answer_index"])
                st.session_state.quiz_state   = "answered"
                st.session_state.quiz_correct = correct
                st.session_state.xp          += 20 if correct else 5
                st.rerun()
        else:
            is_correct_opt = (i == lesson["quiz_answer_index"])
            cls = "quiz-option quiz-correct" if is_correct_opt else "quiz-option"
            st.markdown(f'<div class="{cls}">{opt}</div>', unsafe_allow_html=True)

    if qs == "answered":
        if qc:
            st.success(f"🎉 Correct! +20 XP  —  {lesson['quiz_explanation']}")
        else:
            st.warning(f"Not quite — +5 XP for trying!  {lesson['quiz_explanation']}")

        # Mark complete
        if topic not in st.session_state.completed_topics:
            st.session_state.completed_topics.append(topic)
            st.session_state.lessons_done += 1

        c1, c2 = st.columns(2)
        with c1:
            if st.button("💬 Ask the AI tutor", use_container_width=True):
                go("chat")
        with c2:
            if st.button("🏠 Back to home", use_container_width=True, type="primary"):
                go("home")

# ══════════════════════════════════════════════════════════════════════════════
# AI TUTOR CHAT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "chat":
    render_header()
    lesson  = st.session_state.current_lesson
    persona = st.session_state.persona

    if lesson is None:
        st.info("Complete a lesson first, then come back here to ask the AI tutor questions!")
        if st.button("← Pick a lesson", type="primary"):
            go("topic_select")
        st.stop()

    st.markdown(f"### 💬 AI Tutor · {lesson['emoji']} {lesson['title']}")
    st.caption("Ask anything about this lesson — or how it applies to your life.")

    if not st.session_state.chat_history:
        opening = (
            f"Hey! I'm your FinMind tutor. You just learned about **{lesson['title']}**. "
            f"What questions do you have? I can go deeper, give examples, or help you apply this to your situation."
        )
        st.session_state.chat_history = [{"role": "assistant", "content": opening}]

    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.markdown(f'<div class="chat-ai">🧠 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("**Quick questions:**")
    quick = [
        "Can you give me a real-world example?",
        f"How does this apply to me as a {persona}?",
        "What's the most common mistake people make here?",
        "Give me a 30-day action plan for this topic",
    ]
    q1, q2 = st.columns(2)
    for i, qp in enumerate(quick):
        with (q1 if i % 2 == 0 else q2):
            if st.button(qp, key=f"qp_{i}", use_container_width=True):
                st.session_state._pending_chat = qp

    user_input = st.chat_input("Ask a follow-up question...")
    pending    = st.session_state.pop("_pending_chat", None)
    final      = pending or user_input

    if final:
        st.session_state.chat_history.append({"role": "user", "content": final})
        history_for_claude = st.session_state.chat_history[:-1]
        with st.spinner("Thinking..."):
            reply = ask_tutor(final, lesson, persona, history_for_claude)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.session_state.xp += 5
        st.rerun()

    st.divider()
    if st.button("← Back to lesson", use_container_width=True):
        go("lesson")

# ══════════════════════════════════════════════════════════════════════════════
# PROGRESS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "progress":
    render_header()
    persona  = st.session_state.persona
    p_meta   = PERSONAS[persona]
    xp       = st.session_state.xp
    lvl, lvl_name, xp_prev, xp_next = level_info(xp)
    xp_pct   = min(100, int((xp - xp_prev) / max(1, xp_next - xp_prev) * 100))

    st.markdown("### 📈 Your Progress")
    st.markdown(f'<span class="persona-chip">{p_meta["emoji"]} {persona}</span>', unsafe_allow_html=True)
    st.markdown("")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("🔥 Streak",    f"{st.session_state.streak} days")
    with c2: st.metric("⭐ Total XP",   xp)
    with c3: st.metric("📖 Lessons",   st.session_state.lessons_done)
    with c4: st.metric("🗂️ Topics",    f"{len(st.session_state.completed_topics)}/{len(TOPICS)}")

    st.markdown(f"#### Level {lvl} — {lvl_name}")
    st.markdown(
        f'<div class="xp-bar-wrap"><div class="xp-bar-fill" style="width:{xp_pct}%"></div></div>',
        unsafe_allow_html=True,
    )
    st.caption(f"{xp - xp_prev} / {xp_next - xp_prev} XP to Level {lvl + 1}")

    st.markdown("#### 🗂️ Topics")
    for topic, meta in TOPICS.items():
        done = topic in st.session_state.completed_topics
        c1, c2, c3 = st.columns([1, 3, 1])
        with c1: st.markdown(f"**{meta['emoji']}**")
        with c2: st.markdown(f"**{topic}**")
        with c3: st.markdown("✅ Done" if done else "⬜")

    st.markdown("#### 🏅 Badges earned")
    badges = []
    if st.session_state.lessons_done >= 1:  badges.append(("🌱", "First lesson complete"))
    if st.session_state.lessons_done >= 5:  badges.append(("📚", "5 lessons done"))
    if st.session_state.lessons_done >= 10: badges.append(("🎓", "Scholar — 10 lessons"))
    if st.session_state.streak >= 3:        badges.append(("🔥", "3-day streak"))
    if st.session_state.streak >= 7:        badges.append(("⚡", "7-day streak — On fire!"))
    if len(st.session_state.completed_topics) >= 4: badges.append(("🌍", "Diversified Learner"))
    if xp >= 200:                           badges.append(("💎", "200 XP milestone"))

    if badges:
        for emoji, label in badges:
            st.markdown(f"{emoji} **{label}**")
    else:
        st.info("Complete your first lesson to earn badges!")

    st.divider()
    if st.button("🏠 Back to home", type="primary", use_container_width=True):
        go("home")
