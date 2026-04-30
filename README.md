# 🧠 FinMind – Daily Bite-Sized Financial Education

> **INFORMS × Zolve Hackathon 2026** — Driving Engagement in Financial Apps

## Problem Statement
Financial apps are purely transactional — users open them to pay or check a balance, then leave. This leads to low engagement, weak financial habits, and poor retention.

## Our Solution
**FinMind** is an AI-powered daily financial education app that makes users *want* to come back every day. Instead of dashboards, we deliver:

- **Personalized lessons** — 60-second AI-generated lessons tailored to your money persona and level
- **Knowledge quizzes** — earn XP by testing yourself after each lesson
- **AI tutor chat** — ask follow-up questions, get real-world examples
- **Streaks & XP** — gamified progress that builds daily habits
- **8 financial topics** — Budgeting, Saving, Investing, Credit, Taxes, Insurance, Real Estate, Retirement

## User Flow
```
Onboarding quiz (5 Qs)
       ↓
Money Persona assigned (The Impulse Optimist / Anxious Planner / Calm Analyst / Flowing Adventurer)
       ↓
Home dashboard → pick a topic
       ↓
AI generates personalized lesson (hook → body → analogy → takeaways)
       ↓
Quiz → earn XP
       ↓
AI tutor chat for deeper questions
       ↓
Progress screen (streak, XP, badges, topic map)
```

## Why it drives engagement
- Daily lesson habit loop → streaks keep users returning
- Persona-matched content feels personal, not generic
- XP and badges create game-like progression
- AI tutor makes the app feel like a financial coach, not a product
- 8 topics × infinite AI-generated lessons = always fresh content

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend + UI | Streamlit (Python) |
| AI / LLM | Anthropic Claude API (`claude-sonnet-4-20250514`) |
| Language | Python 3.10+ |
| Deployment | Streamlit Cloud (free) |

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/finmind
cd finmind
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your API key
```bash
export ANTHROPIC_API_KEY=your_key_here
```

Or create `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "your_key_here"
```

### 4. Run locally
```bash
streamlit run finmind_app.py
```

### 5. Deploy to Streamlit Cloud (2 minutes)
1. Push repo to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add `ANTHROPIC_API_KEY` in the Secrets section
5. Click Deploy → get a public URL instantly

## Features
- [x] 5-question behavioral onboarding quiz
- [x] 4 money personas with tailored content
- [x] AI-generated lessons (title, hook, body, analogy, takeaways)
- [x] Per-lesson quiz with XP rewards
- [x] AI tutor chat with quick-prompt chips
- [x] XP system + 5 levels (Beginner → FinMind Pro)
- [x] Day streak tracker
- [x] 8 topic categories
- [x] Badge system (7 badges)
- [x] Progress dashboard

## Screenshots
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/4d02e1af-bbbb-43ad-a3a1-7c27295c17dc" />


## Team
Built for the **INFORMS × Zolve Hackathon**, April 2026.
