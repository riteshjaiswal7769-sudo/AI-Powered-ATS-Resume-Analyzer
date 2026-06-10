from fpdf import FPDF


def generate_pdf_report(result):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, "ATS Resume Analysis Report", ln=True, align="C")

    pdf.ln(10)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Final ATS Score: {result['ats_score']}%", ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Skill Score: {result['skill_score']}%", ln=True)
    pdf.cell(0, 8, f"Keyword Score: {result['keyword_score']}%", ln=True)
    pdf.cell(0, 8, f"Resume Format Score: {result['format_score']}%", ln=True)

    pdf.ln(8)

    def section(title, items):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, title, ln=True)

        pdf.set_font("Arial", "", 11)

        if items:
            if isinstance(items, list):
                text = ", ".join(items)
            else:
                text = str(items)
        else:
            text = "None"

        pdf.multi_cell(0, 8, text)
        pdf.ln(3)

    section("Resume Skills", result["resume_skills"])
    section("Job Description Skills", result["jd_skills"])
    section("Matched Skills", result["matched_skills"])
    section("Missing Skills", result["missing_skills"])

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Recommendations", ln=True)

    pdf.set_font("Arial", "", 11)

    for rec in result["recommendations"]:
        pdf.multi_cell(0, 8, f"- {rec}")

    file_name = "ATS_Resume_Report.pdf"
    pdf.output(file_name)

    return file_name