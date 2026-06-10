import re
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skills import SKILLS_LIST


def extract_text_from_pdf(uploaded_file):
    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s+#.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills(text):
    text = clean_text(text)
    found_skills = []

    for skill in SKILLS_LIST:
        if skill.lower() in text:
            found_skills.append(skill)

    return sorted(list(set(found_skills)))


def keyword_similarity_score(resume_text, jd_text):
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([resume_text, jd_text])

    score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    return round(score * 100, 2)


def calculate_skill_score(resume_skills, jd_skills):
    if len(jd_skills) == 0:
        return 0

    matched = set(resume_skills) & set(jd_skills)
    score = (len(matched) / len(jd_skills)) * 100

    return round(score, 2)


def check_resume_sections(resume_text):
    text = clean_text(resume_text)

    sections = {
        "education": "education" in text,
        "skills": "skills" in text or "technical skills" in text,
        "projects": "projects" in text or "academic projects" in text,
        "experience": "experience" in text or "internship" in text,
        "contact": "email" in text or "phone" in text or "linkedin" in text
    }

    return sections


def calculate_format_score(sections):
    total_sections = len(sections)
    found_sections = sum(sections.values())

    return round((found_sections / total_sections) * 100, 2)


def generate_recommendations(missing_skills, sections):
    recommendations = []

    for skill in missing_skills:
        recommendations.append(f"Add or improve '{skill}' in your resume if you have knowledge of it.")

    if not sections["projects"]:
        recommendations.append("Add a Projects section to show practical experience.")

    if not sections["skills"]:
        recommendations.append("Add a clear Technical Skills section.")

    if not sections["experience"]:
        recommendations.append("Add internship, training, or project-based experience.")

    if not sections["contact"]:
        recommendations.append("Add contact details like email, phone, LinkedIn, or GitHub.")

    if not recommendations:
        recommendations.append("Your resume is well aligned with the job description.")

    return recommendations


def analyze_resume(resume_text, job_description):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    matched_skills = sorted(list(set(resume_skills) & set(jd_skills)))
    missing_skills = sorted(list(set(jd_skills) - set(resume_skills)))

    skill_score = calculate_skill_score(resume_skills, jd_skills)
    keyword_score = keyword_similarity_score(resume_text, job_description)

    sections = check_resume_sections(resume_text)
    format_score = calculate_format_score(sections)

    final_score = (
        skill_score * 0.50 +
        keyword_score * 0.35 +
        format_score * 0.15
    )

    final_score = round(final_score, 2)

    recommendations = generate_recommendations(missing_skills, sections)

    return {
        "ats_score": final_score,
        "skill_score": skill_score,
        "keyword_score": keyword_score,
        "format_score": format_score,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "sections": sections,
        "recommendations": recommendations
    }