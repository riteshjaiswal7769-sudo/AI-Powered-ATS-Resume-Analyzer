import streamlit as st
import pandas as pd
import plotly.express as px
import base64

from ats_engine import extract_text_from_pdf, analyze_resume
from pdf_report import generate_pdf_report


st.set_page_config(
    page_title="AI ATS Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}

.title {
    text-align: center;
    font-size: 45px;
    font-weight: 800;
    color: #1f4e79;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #555;
    margin-bottom: 30px;
}

.card {
    background-color: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
}

.big-score {
    font-size: 55px;
    font-weight: 900;
    color: #1f8f4d;
    text-align: center;
}

.small-heading {
    font-size: 22px;
    font-weight: 700;
    color: #1f4e79;
}
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="title">AI-Powered ATS Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Upload resume PDF, paste job description, and generate ATS score with skill gap report</div>',
    unsafe_allow_html=True
)


col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Upload Resume")
    uploaded_resume = st.file_uploader("Upload PDF Resume", type=["pdf"])
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Job Description")
    job_description = st.text_area("Paste Job Description Here", height=250)
    st.markdown('</div>', unsafe_allow_html=True)


st.write("")

analyze_button = st.button("Generate ATS Analysis", use_container_width=True)


if analyze_button:
    if uploaded_resume is None:
        st.warning("Please upload your resume PDF.")
    elif job_description.strip() == "":
        st.warning("Please paste the job description.")
    else:
        with st.spinner("Analyzing resume..."):
            resume_text = extract_text_from_pdf(uploaded_resume)
            result = analyze_resume(resume_text, job_description)

        st.success("Analysis completed successfully!")

        st.markdown("## Result Dashboard")

        score_col, skill_col, keyword_col, format_col = st.columns(4)

        with score_col:
            st.metric("Final ATS Score", f"{result['ats_score']}%")

        with skill_col:
            st.metric("Skill Score", f"{result['skill_score']}%")

        with keyword_col:
            st.metric("Keyword Score", f"{result['keyword_score']}%")

        with format_col:
            st.metric("Format Score", f"{result['format_score']}%")

        st.write("")

        left, right = st.columns(2)

        with left:
            st.markdown("### Matched Skills")
            if result["matched_skills"]:
                st.success(", ".join(result["matched_skills"]))
            else:
                st.error("No matched skills found.")

        with right:
            st.markdown("### Missing Skills")
            if result["missing_skills"]:
                st.error(", ".join(result["missing_skills"]))
            else:
                st.success("No missing skills found.")

        st.markdown("### Resume Section Check")

        section_df = pd.DataFrame({
            "Section": list(result["sections"].keys()),
            "Present": ["Yes" if value else "No" for value in result["sections"].values()]
        })

        st.dataframe(section_df, use_container_width=True)

        st.markdown("### Recommendations")

        for rec in result["recommendations"]:
            st.write(f"✅ {rec}")

        st.markdown("### Score Breakdown")

        score_df = pd.DataFrame({
            "Category": ["Skill Score", "Keyword Score", "Format Score"],
            "Score": [
                result["skill_score"],
                result["keyword_score"],
                result["format_score"]
            ]
        })

        fig = px.bar(
            score_df,
            x="Category",
            y="Score",
            title="ATS Score Breakdown",
            text="Score"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Skill Match Chart")

        skill_df = pd.DataFrame({
            "Category": ["Matched Skills", "Missing Skills"],
            "Count": [
                len(result["matched_skills"]),
                len(result["missing_skills"])
            ]
        })

        fig2 = px.pie(
            skill_df,
            names="Category",
            values="Count",
            title="Matched vs Missing Skills"
        )

        st.plotly_chart(fig2, use_container_width=True)

        report_path = generate_pdf_report(result)

        with open(report_path, "rb") as file:
            st.download_button(
                label="Download ATS PDF Report",
                data=file,
                file_name="ATS_Resume_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()            
    
st.markdown("---")
st.markdown("## Ask Bhavya - Resume Assistant")

avatar_base64 = get_image_base64("bhavya_avatar.png")

st.markdown(f"""
<div style="
    background-color: #ffffff;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.10);
    display: flex;
    align-items: center;
    gap: 20px;
">
    <img src="data:image/png;base64,{avatar_base64}" 
         style="width:90px; height:90px; border-radius:50%;">
    <div>
        <h3 style="margin-bottom:5px;">Bhavya</h3>
        <p style="color:#555;">Hi, I am Bhavya, your ATS Resume Assistant. Ask me how to improve your resume.</p>
    </div>
</div>
""", unsafe_allow_html=True)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


user_question = st.chat_input("Ask Bhavya something...")

if user_question:
    st.session_state.chat_history.append(("You", user_question))

    question = user_question.lower()

    if "score" in question:
        bot_reply = "Your ATS score depends on skill match, keyword similarity, and resume format. Try to add missing skills from the job description."
    
    elif "missing" in question or "skill" in question:
        bot_reply = "Focus on missing skills shown in the report. Add them only if you really know them or have project experience."
    
    elif "project" in question:
        bot_reply = "Add 2-3 strong projects with tools, dataset, problem statement, and results. For Data Science, mention Python, SQL, ML, Pandas, and visualization."
    
    elif "improve" in question or "resume" in question:
        bot_reply = "Improve your resume by adding technical skills, measurable project outcomes, proper section headings, and keywords from the job description."
    
    elif "ats" in question:
        bot_reply = "ATS means Applicant Tracking System. It checks whether your resume contains job-related keywords, skills, and proper formatting."
    
    else:
        bot_reply = "I can help you with ATS score, missing skills, resume improvement, projects, and job description matching."

    st.session_state.chat_history.append(("Bhavya", bot_reply))


for sender, message in st.session_state.chat_history:
    if sender == "You":
        with st.chat_message("user"):
            st.write(message)
    else:
        with st.chat_message("assistant", avatar="bhavya_avatar.png"):
            st.write(message)    