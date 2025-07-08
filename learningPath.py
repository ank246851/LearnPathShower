import streamlit as st
import requests
import time
from datetime import datetime, timedelta

# --- 1. Gemini API Integration Helper ---
def call_gemini(prompt, api_key):
    """
    Call Gemini (Google AI) API with a prompt, return generated content.
    Replace endpoint and handling as per actual Gemini API documentation.
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    params = {"key": api_key}
    response = requests.post(url, headers=headers, params=params, json=data)
    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return "⚠️ Gemini API call failed or returned unexpected response."

# --- 2. Productivity / Focus Helper ---
def pomodoro_timer(duration=25):
    st.session_state['timer_running'] = True
    for i in range(duration*60, 0, -1):
        if st.session_state.get('timer_stop', False):
            break
        mins, secs = divmod(i, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        st.session_state['timer_display'] = timeformat
        time.sleep(1)
    st.session_state['timer_running'] = False
    st.session_state['timer_display'] = "00:00"

# --- 3. Streamlit App Setup ---
st.set_page_config(page_title="AI Learning Path Generator", page_icon="🎓", layout="wide")
st.markdown(
    "<h1 style='text-align: center; color: #4F8BF9;'>🎓 AI Learning Path Generator (Gemini-powered)</h1>",
    unsafe_allow_html=True,
)

# --- 4. Load Gemini API key securely ---
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("Gemini API key not set! Please add it to your .streamlit/secrets.toml file as GEMINI_API_KEY = \"xxx\"")
    st.stop()

# --- 5. User Profile & Input ---
with st.sidebar:
    st.header("🧑‍🎓 Your Profile")
    username = st.text_input("Name (optional)", key="username")
    topic = st.selectbox("Choose a topic", ["Data Science", "UI/UX", "Web Development", "Cybersecurity", "AI/Machine Learning"])
    level = st.radio("Current Skill Level", ["Beginner", "Intermediate", "Advanced"])
    hours = st.slider("Study hours per week", 1, 40, 5)
    style = st.multiselect("Preferred learning style", ["Videos", "Articles", "Hands-on Projects", "Quizzes", "Flashcards"])
    goal = st.text_input("Your main goal (optional)", placeholder="e.g. Get a job, build a project, etc.")
    st.markdown("---")
    st.subheader("Anti-Distraction Tools")
    if 'focus_mode' not in st.session_state:
        st.session_state['focus_mode'] = False

    if st.button("🔒 Toggle Focus Mode"):
        st.session_state['focus_mode'] = not st.session_state['focus_mode']
    if st.session_state['focus_mode']:
        st.success("Focus Mode is ON: Hide distractions, silence notifications, and stay in this tab!")

    # Pomodoro Timer
    if 'timer_running' not in st.session_state:
        st.session_state['timer_running'] = False
    if 'timer_display' not in st.session_state:
        st.session_state['timer_display'] = "25:00"
    if st.button("⏱️ Start Pomodoro (25m)"):
        st.session_state['timer_stop'] = False
        st.info("Pomodoro started. Stay focused!")
        pomodoro_timer(25)
    st.markdown(f"**Timer:** {st.session_state['timer_display']}")
    if st.session_state['timer_running']:
        if st.button("🛑 Stop Timer"):
            st.session_state['timer_stop'] = True

    # Motivational Quote
    if st.button("💡 Need Motivation?"):
        quote_prompt = "Give me a short motivational quote for students fighting digital distractions."
        quote = call_gemini(quote_prompt, api_key)
        st.info(quote)

# --- 6. Learning Path Generation ---
st.markdown("## 🚀 Generate Your Gemini-Powered Learning Path")
if st.button("Generate Learning Path"):
    with st.spinner("Gemini is crafting your personalized learning path..."):
        base_prompt = (
            f"You are an expert mentor. Create a detailed, step-by-step '{topic}' learning path for a {level} learner "
            f"who can study {hours} hrs/week. Preferred learning style(s): {', '.join(style) if style else 'any'}. "
            f"Goal: {goal if goal else 'Just to learn'}.\n"
            "For each step/module, provide: 1) Name, 2) What to learn, 3) Curated resources (with 1-2 links), "
            "4) Creative project ideas, 5) A checkpoint quiz (3 questions), and 6) Estimated time in weeks."
            "Finish with an overall project idea and a motivational message."
        )
        plan = call_gemini(base_prompt, api_key)
        st.markdown("### 🎯 Your Personalized Learning Path")
        st.markdown(plan)

        # Save progress (in session, for now)
        st.session_state['learning_path'] = plan
        st.session_state['path_generated_at'] = datetime.now()

# --- 7. Progress Tracker & Checkpoints ---
st.markdown("## 📊 Progress & Checkpoints")
if 'learning_path' in st.session_state:
    st.info("Track your modules below. Mark steps as complete to stay motivated!")
    modules = [line for line in st.session_state['learning_path'].split('\n') if line.strip().lower().startswith('step') or line.strip().lower().startswith('module')]
    if not modules:
        modules = [f"Module {i+1}" for i in range(5)]
    completed = st.multiselect("Completed modules", modules, key="completed_modules")
    progress = len(completed) / len(modules) if modules else 0
    st.progress(progress)
    st.markdown(f"**{len(completed)} / {len(modules)} modules completed!**")
    if progress == 1:
        st.success("Congratulations! You've completed this learning path! 🎉")

# --- 8. AI Buddy (Gemini Q&A) ---
st.markdown("## 🤖 AI Study Buddy (Ask Gemini)")
question = st.text_input("Ask me anything about your topic, or paste a resource link for a summary:")
if question:
    with st.spinner("Gemini is thinking..."):
        if question.startswith("http"):
            prompt = f"Summarize the following resource and suggest quiz questions: {question}"
        else:
            prompt = f"Explain for a {level} {topic} student: {question}"
        answer = call_gemini(prompt, api_key)
        st.success(answer)

# --- 9. Dynamic Project Generation ---
st.markdown("## 💡 Suggest a Unique Project")
if st.button("Gemini: Surprise Me With a Project Idea!"):
    project_prompt = (
        f"Generate a creative, real-world project idea for a {level} {topic} learner. "
        f"Outline the project, key features, and how it helps master the topic. Make it fun and challenging."
    )
    project_idea = call_gemini(project_prompt, api_key)
    st.markdown(project_idea)

# --- 10. Adaptive Quiz (Bonus) ---
st.markdown("## 📝 On-the-Fly Quiz")
if st.button("Generate Adaptive Quiz"):
    quiz_prompt = (
        f"Create a 5-question adaptive quiz for a {level} {topic} learner. "
        "Vary difficulty and include correct answers."
    )
    quiz = call_gemini(quiz_prompt, api_key)
    st.markdown(quiz)

# --- 11. Community & Accountability (Demo Only) ---
st.markdown("## 🤝 Accountability & Community")
st.info("Invite a friend to join your path, or share your progress on social media for extra motivation! (Feature coming soon)")

# --- 12. Footer ---
st.markdown("---")
st.markdown(
    "<small>Made with ❤️ using Streamlit & Gemini AI. Your journey to mastery starts now!</small>",
    unsafe_allow_html=True,
)