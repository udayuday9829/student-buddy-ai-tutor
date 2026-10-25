import json
import re
import streamlit as st
import ollama

# =========================================================
# STUDENT BUDDY AI
# Python 3.13 + Streamlit + Ollama + llama3.2
# =========================================================

st.set_page_config(
    page_title="Student Buddy AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_NAME = "llama3.2"

# -------------------- DESIGN -----------------------------

st.markdown("""
<style>
.stApp { background: #f2f6ff; color: #172554; }
.block-container { max-width: 1250px; padding: 1.4rem 2rem 3rem; }
.stApp h1, .stApp h2, .stApp h3 { color: #14234a; }
.stApp p, .stApp label { color: #475569; }
section[data-testid="stSidebar"] {
    background: #fff;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #14234a; }
/* High-contrast, easy-to-find sidebar navigation */
section[data-testid="stSidebar"] div.stButton > button {
    width: 100%;
    min-height: 68px;
    justify-content: flex-start;
    text-align: left;
    padding: 0.9rem 1rem;
    margin: 0.18rem 0;
    background: #eef2ff;
    color: #172554 !important;
    border: 2px solid #c7d2fe;
    border-radius: 12px;
    font-size: 1.25rem !important;
    line-height: 1.35 !important;
    font-weight: 800 !important;
    box-shadow: 0 2px 5px rgba(30, 41, 59, .06);
}
/* Keep the actual label text high-contrast; Streamlit themes can style nested spans separately. */
section[data-testid="stSidebar"] div.stButton > button:not([kind="primary"]),
section[data-testid="stSidebar"] div.stButton > button:not([kind="primary"]) * {
    color: #172554 !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: #ddd6fe;
    color: #1e1b4b !important;
    border-color: #7c3aed;
}
section[data-testid="stSidebar"] div.stButton > button:focus-visible {
    outline: 3px solid #f59e0b;
    outline-offset: 2px;
}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"],
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] * {
    background: #3028e8;
    color: #ffffff !important;
    border: 2px solid #3028e8;
    box-shadow: 0 4px 10px rgba(48, 40, 232, .22);
}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
    background: #201bb8;
    border-color: #201bb8;
}
/* High-contrast primary action buttons: white text on deep blue, like the reference pill */
div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button,
button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    background: #3028e8 !important;
    color: #ffffff !important;
    border: 2px solid #3028e8 !important;
    border-radius: 14px !important;
    min-height: 62px;
    padding: 0.9rem 1.25rem !important;
    font-size: 1.25rem !important;
    line-height: 1.35 !important;
    font-weight: 800 !important;
    text-shadow: none !important;
    opacity: 1 !important;
}
div[data-testid="stButton"] > button *,
div[data-testid="stFormSubmitButton"] > button *,
button[kind="primary"] *,
button[data-testid="stBaseButton-primary"] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
    font-size: 1.25rem !important;
    font-weight: 800 !important;
}
div[data-testid="stButton"] > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    background: #201bb8 !important;
    color: #ffffff !important;
    border-color: #201bb8 !important;
}
div[data-testid="stButton"] > button:focus-visible,
div[data-testid="stFormSubmitButton"] > button:focus-visible {
    outline: 3px solid #f59e0b !important;
    outline-offset: 3px;
}
div[data-testid="stForm"] {
    background: white;
    border: 1px solid #e0e8f5;
    border-radius: 16px;
    padding: 20px;
}
.stApp textarea, .stApp input {
    background: white !important;
    color: #172554 !important;
}
.feature-card {
    background: white;
    border: 1px solid #e0e8f5;
    border-radius: 18px;
    padding: 24px;
    min-height: 155px;
    box-shadow: 0 6px 22px rgba(26, 52, 105, .05);
}
.feature-card h3 { margin-top: 0; color: #14234a; }
.feature-card p { color: #53627c; line-height: 1.65; }
</style>
""", unsafe_allow_html=True)


# -------------------- STATE -----------------------------

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "quiz_topic" not in st.session_state:
    st.session_state.quiz_topic = ""
if "quiz_subject" not in st.session_state:
    st.session_state.quiz_subject = "Mathematics"


# -------------------- HTML HERO -------------------------

def show_hero():
    # Native Streamlit HTML rendering; no deprecated components.html call.
    st.html("""
    <style>
        .sb-hero {
            position: relative;
            overflow: hidden;
            min-height: 390px;
            padding: 55px 20px;
            border-radius: 24px;
            background: #f2f6ff;
            border: 1px solid #e2eaf8;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-family: Arial, Helvetica, sans-serif;
            box-sizing: border-box;
        }
        .sb-hero * { box-sizing: border-box; }
        .sb-hero-content { position: relative; z-index: 2; max-width: 720px; }
        .sb-hero-eyebrow {
            color: #3028e8;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 20px;
        }
        .sb-hero h1 {
            color: #10234b;
            font-size: clamp(30px, 4vw, 48px);
            line-height: 1.15;
            font-weight: 400;
            margin: 8px 0;
        }
        .sb-hero-subtitle {
            color: #475569;
            font-size: 17px;
            line-height: 1.7;
            max-width: 620px;
            margin: 22px auto;
        }
        .sb-hero-cta {
            display: inline-block;
            background: #3028e8;
            color: #fff !important;
            padding: 14px 26px;
            border-radius: 40px;
            font-weight: 700;
        }
        .sb-hero-circle {
            position: absolute;
            width: 85px; height: 85px;
            right: 4%; top: 18px;
            background: #ff464b; border-radius: 50%;
        }
        .sb-hero-diamond {
            position: absolute;
            width: 60px; height: 60px;
            left: 6%; bottom: 38px;
            background: #8dd8ea; transform: rotate(45deg);
        }
        .sb-hero-triangle {
            position: absolute; width: 0; height: 0;
            right: 5%; bottom: 34px;
            border-top: 42px solid transparent;
            border-bottom: 42px solid transparent;
            border-left: 70px solid #18a65c;
            transform: rotate(-15deg);
        }
        @media (max-width: 600px) {
            .sb-hero { min-height: 350px; padding: 42px 14px; }
            .sb-hero-eyebrow { font-size: 10px; letter-spacing: 1px; }
            .sb-hero-circle { width: 42px; height: 42px; }
            .sb-hero-diamond { width: 28px; height: 28px; }
            .sb-hero-triangle {
                border-top-width: 20px;
                border-bottom-width: 20px;
                border-left-width: 34px;
            }
        }
    </style>
    <section class="sb-hero">
        <div class="sb-hero-circle"></div>
        <div class="sb-hero-diamond"></div>
        <div class="sb-hero-triangle"></div>
        <div class="sb-hero-content">
            <div class="sb-hero-eyebrow">YOUR PERSONAL AI LEARNING COMPANION</div>
            <h1>Next Level AI Tutoring</h1>
            <h1>For Class 10 Learners</h1>
            <div class="sb-hero-subtitle">
                Understand difficult topics, solve problems,
                and prepare for exams with your personal AI tutor.
            </div>
            <div class="sb-hero-cta">Learn &bull; Practise &bull; Improve &rarr;</div>
        </div>
    </section>
    """)


# -------------------- AI HELPERS ------------------------

def ask_ai(prompt, temperature=0.2):
    """Send a prompt to the local Ollama model."""
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": temperature},
    )
    return response["message"]["content"].strip()


def extract_json(text):
    """Parse JSON even if the model wraps it in Markdown fences."""
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end < start:
        raise ValueError("The model did not return a JSON object.")
    return json.loads(cleaned[start:end + 1])


def validate_quiz(data, expected_count):
    if not isinstance(data, dict):
        raise ValueError("Quiz response must be a JSON object.")
    questions = data.get("questions")
    if not isinstance(questions, list) or len(questions) != expected_count:
        raise ValueError(
            f"The model did not return exactly {expected_count} questions. Try again."
        )
    for question in questions:
        if not isinstance(question, dict):
            raise ValueError("One question has an invalid format.")
        if not isinstance(question.get("question"), str) or not question["question"].strip():
            raise ValueError("A question is missing its text.")
        options = question.get("options")
        if (
            not isinstance(options, list)
            or len(options) != 4
            or not all(isinstance(option, str) and option.strip() for option in options)
        ):
            raise ValueError("Each question must have four text options.")
        answer = question.get("correct_index")
        if type(answer) is not int or answer not in (0, 1, 2, 3):
            raise ValueError("A question has an invalid correct answer index.")
        if not isinstance(question.get("explanation"), str):
            question["explanation"] = "Review this answer in your textbook."
    return data


# -------------------- SIDEBAR ---------------------------

with st.sidebar:
    st.markdown("# 🎓 Student Buddy")
    st.caption("Your personal AI learning companion")
    st.divider()
    st.markdown("### Navigation")

    # The current page is highlighted with a high-contrast primary button.
    home_label = "✓  🏠 Home  ·  CURRENT" if st.session_state.page == "Home" else "🏠  Home"
    tutor_label = "✓  📚 Study Tutor  ·  CURRENT" if st.session_state.page == "Study Tutor" else "📚  Study Tutor"
    quiz_label = "✓  🧠 Quiz & MCQ Generator  ·  CURRENT" if st.session_state.page == "Quiz" else "🧠  Quiz & MCQ Generator"

    if st.button(home_label, key="nav_home", type="primary" if st.session_state.page == "Home" else "secondary", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
    if st.button(tutor_label, key="nav_tutor", type="primary" if st.session_state.page == "Study Tutor" else "secondary", use_container_width=True):
        st.session_state.page = "Study Tutor"
        st.rerun()
    if st.button(quiz_label, key="nav_quiz", type="primary" if st.session_state.page == "Quiz" else "secondary", use_container_width=True):
        st.session_state.page = "Quiz"
        st.rerun()

    st.divider()
    st.markdown("### ⚙️ Study Settings")
    subject = st.selectbox(
        "Choose subject",
        ["English", "Mathematics", "Science", "Social Science"],
        key="chosen_subject",
    )
    answer_length = st.selectbox(
        "Explanation length", ["Short", "Medium", "Detailed"], index=1
    )
    st.divider()
    st.caption("Powered by Ollama + Llama 3.2")
    st.caption("AI model runs locally on your computer.")


# -------------------- HOME PAGE -------------------------

if st.session_state.page == "Home":
    show_hero()
    st.markdown("<h2 style='text-align:center'>Meet Your AI Tutors</h2>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center'>Choose a learning tool to get started.</p>",
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        st.markdown("""
        <div class="feature-card">
            <h3>📚 AI Study Tutor</h3>
            <p>Understand difficult topics, work through examples, solve maths
            problems, and summarize a passage in simple language.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Studying →", key="home_study", use_container_width=True):
            st.session_state.page = "Study Tutor"
            st.rerun()

    with right:
        st.markdown("""
        <div class="feature-card">
            <h3>🧠 Quiz & MCQ Tutor</h3>
            <p>Generate multiple-choice questions, check your answers, calculate
            your score, and review explanations.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Quiz →", key="home_quiz", use_container_width=True):
            st.session_state.page = "Quiz"
            st.rerun()

    st.write("")
    st.divider()
    st.markdown("### ✨ Your learning journey")
    c1, c2, c3 = st.columns(3)
    c1.markdown("**📖 Learn**")
    c1.caption("Understand topics in simple language.")
    c2.markdown("**✍️ Practise**")
    c2.caption("Solve questions and test your knowledge.")
    c3.markdown("**📈 Improve**")
    c3.caption("Review mistakes and build confidence.")


# -------------------- STUDY TUTOR -----------------------

elif st.session_state.page == "Study Tutor":
    show_hero()
    st.subheader("📚 Your AI Study Tutor")
    st.write("Ask a question, solve a maths problem, or summarize a passage.")

    task = st.selectbox(
        "What would you like help with?",
        ["Explain a topic", "Solve a Mathematics problem",
         "Summarize an article or chapter"],
    )

    if task == "Summarize an article or chapter":
        label = "Paste your article or chapter"
        placeholder = "Paste the passage you want to summarize..."
    elif task == "Solve a Mathematics problem":
        label = "Enter your Mathematics problem"
        placeholder = "Example: Solve x^2 + 5x + 6 = 0"
    else:
        label = "Enter your question or topic"
        placeholder = "Example: Explain quadratic equations."

    question = st.text_area(label, height=150, placeholder=placeholder)

    if st.button("✨ Generate Answer", type="primary"):
        if not question.strip():
            st.warning("Please enter a question or passage.")
        else:
            if task == "Summarize an article or chapter":
                prompt = f"""
You are a careful Class 10 study assistant.
Summarize the passage in {answer_length.lower()} length.
Use clear headings and bullet points where helpful.
Use only information supported by the passage; do not invent facts.
PASSAGE:
{question}
"""
            elif task == "Solve a Mathematics problem":
                prompt = f"""
You are a patient Class 10 Mathematics tutor.
Solve this problem step by step. Explain the formula, substitution,
calculations and final answer. Check the result if possible.
Use {answer_length.lower()} detail and simple language.
PROBLEM:
{question}
"""
            else:
                prompt = f"""
You are Student Buddy, a friendly Class 10 tutor.
Subject: {subject}
Question or topic: {question}
Explain in simple language with headings, key points and one suitable example.
Keep the answer {answer_length.lower}. Do not invent facts if uncertain.
"""
            try:
                with st.spinner("Your AI tutor is thinking..."):
                    answer = ask_ai(prompt)
                st.markdown("### 💡 Your Answer")
                st.markdown(answer)
                st.caption(
                    "AI-generated answers can contain mistakes. "
                    "Check important answers against your textbook."
                )
            except Exception as exc:
                st.error(
                    "Could not contact Ollama. Make sure Ollama is running "
                    "and the llama3.2 model is installed."
                )
                with st.expander("Technical details"):
                    st.code(str(exc))


# -------------------- QUIZ GENERATOR --------------------

elif st.session_state.page == "Quiz":
    show_hero()
    st.subheader("🧠 Quiz & MCQ Generator")
    st.write("Create a practice quiz, answer the questions, and review your score.")

    with st.form("quiz_setup"):
        topic = st.text_input("Topic or chapter",
                              placeholder="Example: Quadratic Equations")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
        count = st.selectbox("Number of questions", [5, 10])
        create = st.form_submit_button("🚀 Generate My Quiz", type="primary")

    if create:
        if not topic.strip():
            st.warning("Please enter a topic or chapter.")
        else:
            prompt = f"""
Create exactly {count} Class 10 multiple-choice questions.
Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}

Return ONLY a valid JSON object in this format:
{{
  "title": "Quiz title",
  "questions": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 0,
      "explanation": "Why this answer is correct"
    }}
  ]
}}

Rules:
- Exactly {count} questions.
- Exactly four non-empty options per question.
- correct_index must be an integer 0, 1, 2, or 3.
- Exactly one option should be correct.
- Provide a short explanation for each answer.
- Use suitable Class 10 language and check calculations.
- Do not add Markdown fences or text outside the JSON.
"""
            try:
                with st.spinner("Creating your quiz with Llama 3.2..."):
                    raw = ask_ai(prompt, temperature=0.1)
                    quiz = validate_quiz(extract_json(raw), count)
                st.session_state.quiz = quiz
                st.session_state.quiz_topic = topic.strip()
                st.session_state.quiz_subject = subject
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()
            except Exception as exc:
                st.error(
                    "The quiz could not be generated or checked. "
                    "Try again, or use a simpler topic."
                )
                with st.expander("Technical details"):
                    st.code(str(exc))

    quiz = st.session_state.quiz
    if quiz is not None:
        st.divider()
        st.markdown(f"### 📝 {quiz.get('title', 'Practice Quiz')}")
        st.caption(
            f"Subject: {st.session_state.quiz_subject} | "
            f"Topic: {st.session_state.quiz_topic}"
        )

        with st.form("answer_quiz"):
            chosen = {}
            for index, item in enumerate(quiz["questions"]):
                st.markdown(f"**Question {index + 1}. {item['question']}**")
                chosen[index] = st.radio(
                    "Choose your answer",
                    options=[0, 1, 2, 3],
                    format_func=lambda value, opts=item["options"]: (
                        f"{'ABCD'[value]}. {opts[value]}"
                    ),
                    index=None,
                    key=f"quiz_choice_{index}",
                )
                st.write("")
            submitted = st.form_submit_button("✅ Check My Answers", type="primary")

        if submitted:
            st.session_state.quiz_answers = chosen
            st.session_state.quiz_submitted = True

        if st.session_state.quiz_submitted:
            answers = st.session_state.quiz_answers
            questions = quiz["questions"]
            score = sum(
                1 for i, item in enumerate(questions)
                if answers.get(i) == item["correct_index"]
            )
            total = len(questions)
            percentage = round(score * 100 / total) if total else 0

            st.divider()
            st.markdown("## 📊 Your Results")
            m1, m2, m3 = st.columns(3)
            m1.metric("Score", f"{score}/{total}")
            m2.metric("Percentage", f"{percentage}%")
            m3.metric(
                "Feedback",
                "Excellent!" if percentage >= 80
                else "Good effort!" if percentage >= 50
                else "Keep practising!",
            )
            st.progress(percentage / 100)
            st.markdown("### 📖 Answer Review")

            for i, item in enumerate(questions):
                answer = answers.get(i)
                correct = item["correct_index"]
                with st.expander(f"Question {i + 1}"):
                    st.write(item["question"])
                    if answer == correct:
                        st.success(f"Correct: {item['options'][correct]}")
                    else:
                        if answer is None:
                            st.error("Not answered.")
                        else:
                            st.error(f"Your answer: {item['options'][answer]}")
                        st.write(f"Correct answer: {item['options'][correct]}")
                    st.info(f"Explanation: {item['explanation']}")

            if st.button("🔄 Create Another Quiz"):
                st.session_state.quiz = None
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_topic = ""
                st.rerun()


# -------------------- FOOTER ----------------------------

st.divider()
st.markdown(
    "<p style='text-align:center;color:#64748b;font-size:0.9rem'>"
    "🎓 Student Buddy AI &nbsp; | &nbsp; Learn • Practise • Improve"
    "</p>",
    unsafe_allow_html=True,
)
