from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(data, filename="beam_report.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("AI Structural Beam Design", styles["Title"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Span: {data['input']['span']} m", styles["Normal"]))
    content.append(Paragraph(f"Load: {data['input']['load']} kN/m", styles["Normal"]))
    content.append(Paragraph(f"Concrete (fcu): {data['input'].get('fcu') or data['input'].get('fck', 'N/A')}", styles["Normal"]))
    content.append(Paragraph(f"Steel (fy): {data['input']['fy']}", styles["Normal"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Steel Area: {data['results']['steel_area']} mm²", styles["Normal"]))
    content.append(Paragraph(f"Bending Moment: {data['results']['bending_moment']} kNm", styles["Normal"]))
    content.append(Paragraph(f"Wall Load: {data['results']['wall_load']} kN/m", styles["Normal"]))
    content.append(Paragraph(f"Total Load: {data['results']['total_load']} kN/m", styles["Normal"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Reinforcement: {data['reinforcement']['recommended']}", styles["Normal"]))

    doc.build(content)

    return filename