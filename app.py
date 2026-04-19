import streamlit as st
import time
import pandas as pd
import PyPDF2
import re
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# ---------- SESSION ----------
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

# ---------- SKILLS DATABASE ----------
SKILLS_DB = {
    "data scientist": ["python","machine learning","pandas","numpy","sql","statistics"],
    "java developer": ["java","spring","hibernate","oop"],
    "web developer": ["html","css","javascript","react","node"],
    "business analyst": ["excel","sql","power bi","communication","statistics"]
}

# ---------- CLEAN ----------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

# ---------- EXTRACT ----------
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        pdf = PyPDF2.PdfReader(file)
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + " "
    else:
        text = str(file.read(), "utf-8")
    return clean_text(text)

# ---------- SKILL EXTRACTION ----------
def extract_skills(text):
    skills = set()
    all_skills = set(sum(SKILLS_DB.values(), []))

    for skill in all_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            skills.add(skill)

    return list(skills)

# ---------- SMART JD FILTER ----------
def filter_by_job_desc(required, job_desc):
    jd = job_desc.lower()

    final = []

    for skill in required:
        if skill in jd:
            # check negative words
            if not any(word in jd for word in ["no " + skill, "not " + skill]):
                final.append(skill)

    return final if final else required

# ---------- ANALYSIS ----------
def analyze_resume(text, role, job_desc):

    role = role.lower()

    required = []
    for key in SKILLS_DB:
        if key in role:
            required = SKILLS_DB[key]

    if not required:
        required = ["python","sql","communication"]

    # 🔥 FIX: job description filtering
    if job_desc.strip():
        required = filter_by_job_desc(required, job_desc)

    detected = extract_skills(text)

    found = [s for s in required if s in detected]
    missing = [s for s in required if s not in detected]

    # 🔥 IMPROVED SCORE
    skill_score = (len(found) / len(required)) * 100 if required else 0

    # similarity weight reduced (fix low % issue)
    try:
        tfidf = TfidfVectorizer(stop_words="english")
        vectors = tfidf.fit_transform([text, job_desc if job_desc else " ".join(required)])
        similarity = cosine_similarity(vectors[0], vectors[1])[0][0] * 100
    except:
        similarity = 0

    final_score = int((0.85 * skill_score) + (0.15 * similarity))

    return final_score, found, missing, detected, required


# ---------- SIDEBAR ----------
st.sidebar.title("AI Resume Analyzer")

page = st.sidebar.selectbox("Navigation", ["Dashboard", "Resume Analysis"])

job_role = st.sidebar.text_input("Enter Job Role", "Data Scientist")
experience = st.sidebar.slider("Experience", 0, 10, 1)

st.sidebar.markdown("### Job Description")
job_desc = st.sidebar.text_area("Paste Job Description", height=150)

# ---------- HEADER ----------
st.markdown("""
<div style='background: linear-gradient(90deg,#1e3a8a,#2563eb);
padding:30px;border-radius:15px;color:white'>
<h1>☁️ Cloud-Based AI Resume Analyzer</h1>
<p style='font-size:18px;'>Skill Matching & Intelligent Feedback System</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------- DASHBOARD ----------
if page == "Dashboard":

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AI Model", "Active")
    c2.metric("Cloud", "Online")
    c3.metric("Speed", "Fast")
    c4.metric("Accuracy", "Smart AI")

    st.progress(90)
    st.caption("System Ready: 90%")

    st.info("Resume Parsing • NLP Matching • Skill Intelligence • AI Feedback")


# ---------- ANALYSIS ----------
if page == "Resume Analysis":

    tabs = st.tabs(["Upload", "Analysis", "Results"])

    # ---------- UPLOAD ----------
    with tabs[0]:
        file = st.file_uploader("Upload Resume", type=["pdf","txt"])

        if file:
            st.success("Resume uploaded")
            st.session_state.resume_text = extract_text(file)
            st.session_state.analyzed = False

    # ---------- ANALYSIS ----------
    with tabs[1]:

        if not st.session_state.resume_text:
            st.warning("Upload resume first")

        else:
            if st.button("🚀 Start AI Analysis"):

                progress = st.progress(0)
                steps = [
                    "Reading resume...",
                    "Cleaning text...",
                    "Extracting skills...",
                    "Matching role...",
                    "Generating insights..."
                ]

                for i, s in enumerate(steps):
                    st.write(s)
                    progress.progress((i+1)*20)
                    time.sleep(0.3)

                st.session_state.analyzed = True
                st.success("Analysis Completed")

                text = st.session_state.resume_text
                detected = extract_skills(text)

                # 🔥 STRONG OVERVIEW
                st.markdown("### 🔍 What AI Analyzed")

                words = text.split()
                st.write(f"• Total Words: {len(words)}")
                st.write(f"• Unique Words: {len(set(words))}")
                st.write(f"• Skills Detected: {len(detected)}")

                st.markdown("### 📄 Resume Overview")

                if len(words) > 300:
                    st.write("• Detailed resume with strong content")
                else:
                    st.write("• Resume content is limited, can be improved")

                if len(detected) > 5:
                    st.write("• Good technical skill coverage")
                else:
                    st.write("• Add more technical skills")

                if job_desc:
                    st.write("• Compared with job description for accuracy")

                st.markdown("### 🧠 Skills Identified")
                st.success(", ".join(detected) if detected else "No skills detected")


    # ---------- RESULTS ----------
    with tabs[2]:

        if st.session_state.analyzed:

            score, found, missing, detected, required = analyze_resume(
                st.session_state.resume_text, job_role, job_desc
            )

            st.markdown(f"### 📊 Results for: {job_role}")

            c1, c2, c3 = st.columns(3)
            c1.metric("Match Score", f"{score}%")
            c2.metric("Skills Found", len(found))
            c3.metric("Missing Skills", len(missing))

            st.markdown("### 🎯 Required Skills")
            st.info(", ".join(required))

            st.markdown("### ✅ Found Skills")
            st.success(", ".join(found) if found else "None")

            st.markdown("### ❌ Missing Skills")
            st.error(", ".join(missing) if missing else "None")

            # 🔥 BETTER SUGGESTIONS
            st.markdown("### 💡 Intelligent Suggestions")

            if missing:
                for skill in missing:
                    st.write(f"• Add **{skill}** to improve matching")

            st.write("• Add projects related to job role")
            st.write("• Use strong keywords from JD")
            st.write("• Quantify achievements")

            # ---------- VISUAL ----------
            st.markdown("### 📊 Visualization")

            fig, ax = plt.subplots()
            ax.pie([len(found), len(missing)],
                   labels=["Matched","Missing"],
                   autopct="%1.1f%%")
            st.pyplot(fig)

            df = pd.DataFrame({
                "Type":["Matched","Missing"],
                "Count":[len(found), len(missing)]
            }).set_index("Type")

            st.bar_chart(df)

            # 🔥 FIX MATCH LEVEL
            st.markdown(f"### 📈 Match Level: {score}%")
            st.progress(score)

        else:
            st.info("Upload → Analyze → View results")
