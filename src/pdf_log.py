# pdf_log.py — compliance PDF banao, English me
# reportlab se banega, simple wala
# PDF English-only hai — font Devanagari nahi likh sakta
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


# PDF banao — date, site, WBGT, brief, risk, roster
def make_pdf(path, date_str, site, wbgt_max, wbgt_noon,
             high_risk_names, roster_df, lang_note, heat_names=None):
    # file banao
    doc = SimpleDocTemplate(path, pagesize=A4,
                            topMargin=2 * cm, bottomMargin=2 * cm)
    # style lo
    styles = getSampleStyleSheet()
    # sab kuch list me daalo
    story = []
    # title
    story.append(Paragraph("Heat-Shift Roster — Compliance Log (OSH Code)", styles["Title"]))
    story.append(Paragraph("Daily compliance log", styles["Normal"]))
    story.append(Spacer(1, 12))
    # date aur site
    story.append(Paragraph(f"Date: {date_str}", styles["Normal"]))
    story.append(Paragraph(f"Site: {site}", styles["Normal"]))
    story.append(Paragraph(f"Max WBGT: {wbgt_max} C, WBGT at 12:00: {wbgt_noon} C", styles["Normal"]))
    story.append(Spacer(1, 12))
    # brief
    story.append(Paragraph("Morning Brief:", styles["Heading2"]))
    story.append(Paragraph(
        f"Today heat is high in the afternoon (WBGT {wbgt_max} C). "
        "Do heavy work in the morning 6-11 and evening 4-8. "
        "Take a break 12-4, drink water, sit in shade. "
        "Full day wage will be paid, break time will not be cut.",
        styles["Normal"]))
    story.append(Spacer(1, 12))
    # high risk workers
    story.append(Paragraph("High Risk Workers:", styles["Heading2"]))
    if high_risk_names:
        for name in high_risk_names:
            story.append(Paragraph(f"- {name} — give light work, no heavy work at midday", styles["Normal"]))
    else:
        story.append(Paragraph("No high risk worker.", styles["Normal"]))
    story.append(Spacer(1, 12))
    # past heat illness — hamesha High risk
    if heat_names:
        story.append(Paragraph("Past Heat Illness:", styles["Heading2"]))
        for name in heat_names:
            story.append(Paragraph(
                f"- {name} — marked yes, always High risk, no heavy work at midday.",
                styles["Normal"]))
        story.append(Spacer(1, 12))
    # roster table
    story.append(Paragraph("New Roster:", styles["Heading2"]))
    # table data banao
    data = [["Task", "Time", "Note"]]
    for _, r in roster_df.iterrows():
        data.append([str(r["task"]), str(r["time"]), str(r["note"])])
    # table banao
    t = Table(data, colWidths=[5 * cm, 5 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    # note — ye medical advice nahi hai
    story.append(Paragraph(
        "Note: This is not medical advice. If a worker feels unwell, "
        "stop work and see a doctor.",
        styles["Normal"]))
    story.append(Paragraph(lang_note, styles["Normal"]))
    # PDF likho
    doc.build(story)
    return path
