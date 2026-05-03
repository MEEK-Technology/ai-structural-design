from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(data, filename="beam_report.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("AI Structural Beam Design", styles["Title"]))
    content.append(Spacer(1, 10))

    # Input parameters
    content.append(Paragraph(f"Beam Type: {data['input'].get('beam_type', 'simply_supported').replace('_', ' ').title()}", styles["Normal"]))
    content.append(Paragraph(f"Load Type: {data['input'].get('load_type', 'udl').replace('_', ' ').title()}", styles["Normal"]))
    content.append(Paragraph(f"Span: {data['input']['span']} m", styles["Normal"]))
    content.append(Paragraph(f"Load: {data['input']['load']} {'kN' if data['input'].get('load_type') == 'point_load' else 'kN/m'}", styles["Normal"]))
    content.append(Paragraph(f"Concrete (fcu): {data['input'].get('fcu') or data['input'].get('fck', 'N/A')}", styles["Normal"]))
    content.append(Paragraph(f"Steel (fy): {data['input']['fy']}", styles["Normal"]))
    content.append(Paragraph(f"Support: {data['input'].get('support_left', 'pinned').title()} — {data['input'].get('support_right', 'roller').title()}", styles["Normal"]))
    content.append(Spacer(1, 10))

    # Results
    content.append(Paragraph(f"Steel Area: {data['results']['steel_area']} mm²", styles["Normal"]))
    content.append(Paragraph(f"Bending Moment: {data['results']['bending_moment']} kNm", styles["Normal"]))
    content.append(Paragraph(f"Max Shear Force: {data['results'].get('max_shear_force', 'N/A')} kN", styles["Normal"]))
    content.append(Paragraph(f"Wall Load: {data['results']['wall_load']} kN/m", styles["Normal"]))
    content.append(Paragraph(f"Total Load: {data['results']['total_load']} kN/m", styles["Normal"]))
    content.append(Paragraph(f"Deflection: {data['deflection']}", styles["Normal"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Reinforcement: {data['reinforcement']['recommended']}", styles["Normal"]))
    content.append(Paragraph(f"Beam Size: {data['beam']['width']}mm x {data['beam']['depth']}mm", styles["Normal"]))

    doc.build(content)

    return filename