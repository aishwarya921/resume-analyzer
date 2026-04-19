import streamlit as st
from PyPDF2 import PdfReader
import re

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# ---------- COMMON SKILLS DATABASE ----------
ALL_SKILLS = [
    "python", "java", "c", "c++", "sql", "excel", "power bi", "tableau",
    "machine learning", "deep learning", "nlp", "data analysis",
    "pandas", "numpy", "matplotlib", "statistics",
    "spring", "hibernate", "jdbc", "oop", "servlets",
    "html", "css", "javascript", "react",
    "communication", "teamwork", "leadership"
]

# ---------- FUNCTIONS ----------

def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        pdf = PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text() or ""
    else:
        text = file.read().decode("utf-8", errors="ignore")
    return text.lower()


def clean_text(text):
    return re.sub(r'[^a-zA-Z ]', ' ', text.lower())


def get_role_keywords(role):
    return role.lower().split()


def calculate_match(resume_text, role):
    resume_text = clean_text(resume_text)
    role_keywords = get_role_keywords(role)

    # Step 1: find relevant skills based on role words
    relevant_skills = []

    for skill in ALL_SKILLS:
        for word in role_keywords:
            if word in skill:
                relevant_skills.append(skill)

    # fallback (if nothing matched)
    if not relevant_skills:
        relevant_skills = ALL_SKILLS[:10]

    # Step 2: check resume
    found = []
    for skill in relevant_skills:
        if skill in resume_text:
            found.append(skill)

    score = int((len(found) / len(relevant_skills)) * 100)
    missing = list(set(relevant_skills) - set(found))

    return score, found, missing, relevant_skills


# ---------- SIDEBAR ----------

st.sidebar.title("AI Resume Analyzer")

page = st.sidebar.selectbox("Navigation", ["Dashboard", "Resume Analysis"])

job_role = st.sidebar.text_input("Enter Job Role", "data analyst")
st.sidebar.write("Selected Role:", job_role)

experience = st.sidebar.slider("Experience (years)", 0, 10, 1)

# ---------- HEADER ----------

st.markdown("""
<div style='background: linear-gradient(90deg,#1e3a8a,#2563eb);
padding:25px;border-radius:10px;color:white'>
<h1>AI Resume Analyzer</h1>
<p>Universal Skill Matching System</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------- DASHBOARD ----------

if page == "Dashboard":
    st.subheader("System Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("AI Model", "Active")
    c2.metric("System", "Universal")
    c3.metric("Processing", "Fast")
    c4.metric("Accuracy", "Dynamic")

# ---------- ANALYSIS ----------

if page == "Resume Analysis":

    st.subheader("Upload Resume")

    file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])

    if file:
        st.success("File uploaded successfully")

        resume_text = extract_text(file)

        score, found, missing, relevant_skills = calculate_match(resume_text, job_role)

        st.markdown("## Results")

        c1, c2, c3 = st.columns(3)
        c1.metric("Match Score", f"{score}%")
        c2.metric("Skills Found", len(found))
        c3.metric("Missing Skills", len(missing))

        st.markdown("### Skill Match")
        st.progress(score)

        st.markdown("### Relevant Skills for Role")
        st.write(relevant_skills)

        st.markdown("### Found Skills")
        st.write(found if found else "No matching skills found")

        st.markdown("### Missing Skills")
        st.write(missing)

        st.markdown("### Suggestions")
        for skill in missing:
            st.write(f"• Learn {skill}")

        st.markdown("### Visualization")
        st.bar_chart({"Match": [score], "Gap": [100 - score]})

    else:
        st.info("Please upload a resume to begin analysis")