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

    # Results - Load breakdown
    content.append(Paragraph(f"n1 Slab Load: {data['results'].get('n1_slab_load', 0)} kN/m", styles["Normal"]))
    content.append(Paragraph(f"n2 Beam Self-Weight: {data['results'].get('n2_beam_self_weight', 0)} kN/m", styles["Normal"]))
    content.append(Paragraph(f"n3 Wall Load: {data['results'].get('n3_wall_load', 0)} kN/m", styles["Normal"]))
    content.append(Paragraph(f"w Total UDL: {data['results'].get('w_total_udl', 0)} kN/m", styles["Normal"]))
    content.append(Paragraph(f"p1 Point Load: {data['results'].get('p1_point_load', 0)} kN", styles["Normal"]))
    content.append(Spacer(1, 10))

    # Design results
    content.append(Paragraph(f"Steel Area: {data['results']['steel_area']} mm²", styles["Normal"]))
    content.append(Paragraph(f"M (UDL): {data['results'].get('M_udl', 'N/A')} kNm", styles["Normal"]))
    content.append(Paragraph(f"M (Point): {data['results'].get('M_point', 'N/A')} kNm", styles["Normal"]))
    content.append(Paragraph(f"M (Total): {data['results']['bending_moment']} kNm", styles["Normal"]))
    content.append(Paragraph(f"Max Shear Force: {data['results'].get('max_shear_force', 'N/A')} kN", styles["Normal"]))
    content.append(Paragraph(f"Deflection: {data['deflection']}", styles["Normal"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Reinforcement: {data['reinforcement']['recommended']}", styles["Normal"]))
    content.append(Paragraph(f"Beam Size: {data['beam']['width']}mm x {data['beam']['depth']}mm", styles["Normal"]))

    doc.build(content)

    return filename