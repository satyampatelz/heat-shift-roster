# pdf_log.py — compliance PDF banao, Hindi + English dono me
# reportlab se banega, simple wala
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


# PDF banao — Hindi pehle, English neeche
def make_pdf(path, date_str, site, wbgt_max, wbgt_noon,
             high_risk_names, roster_df, lang_note):
    # file banao
    doc = SimpleDocTemplate(path, pagesize=A4,
                            topMargin=2 * cm, bottomMargin=2 * cm)
    # style lo
    styles = getSampleStyleSheet()
    # sab kuch list me daalo
    story = []
    # title — Hindi
    story.append(Paragraph("Heat-Shift Roster — Compliance Log", styles["Title"]))
    story.append(Paragraph("OSH Code ke hisaab se daily log (Daily compliance log)", styles["Normal"]))
    story.append(Spacer(1, 12))
    # date aur site — dono bhasha me
    story.append(Paragraph(f"Date / Tarikh: {date_str}", styles["Normal"]))
    story.append(Paragraph(f"Site: {site}", styles["Normal"]))
    story.append(Paragraph(f"Max WBGT: {wbgt_max} C, Dopahar 12 baje WBGT: {wbgt_noon} C", styles["Normal"]))
    story.append(Spacer(1, 12))
    # Hindi brief
    story.append(Paragraph("Hindi Brief:", styles["Heading2"]))
    story.append(Paragraph(
        f"Aaj dopahar me garmi zyada hai (WBGT {wbgt_max} C). "
        "Bhaari kaam subah 6-11 aur shaam 4-8 me karo. "
        "Dopahar 12-4 break lo, paani piyo. "
        "Dihaadi poori milegi, break ka time kaata nahi jayega.",
        styles["Normal"]))
    story.append(Spacer(1, 6))
    # English brief
    story.append(Paragraph("English Brief:", styles["Heading2"]))
    story.append(Paragraph(
        f"Today heat is high (WBGT {wbgt_max} C). "
        "Do heavy work in the morning 6-11 and evening 4-8. "
        "Take a break 12-4, drink water. "
        "Full day wage will be paid, break time will not be cut.",
        styles["Normal"]))
    story.append(Spacer(1, 12))
    # high risk workers
    story.append(Paragraph("High Risk Workers / Zyada Risk Wale Worker:", styles["Heading2"]))
    if high_risk_names:
        for name in high_risk_names:
            story.append(Paragraph(f"- {name} — halka kaam do, dopahar me mat lagao", styles["Normal"]))
    else:
        story.append(Paragraph("Koi High risk worker nahi hai. / No high risk worker.", styles["Normal"]))
    story.append(Spacer(1, 12))
    # roster table
    story.append(Paragraph("Naya Roster / New Roster:", styles["Heading2"]))
    # table data banao
    data = [["Task / Kaam", "Time / Samay", "Note"]]
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
        "Note: Ye medical advice nahi hai. Tabiyat kharab ho to doctor ko dikhao. "
        "/ This is not medical advice. See a doctor if you feel unwell.",
        styles["Normal"]))
    story.append(Paragraph(lang_note, styles["Normal"]))
    # PDF likho
    doc.build(story)
    return path
