import io
from datetime import datetime

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


def generate_certificate(user, learning_path, completed_date):
    """Generiert ein PDF-Zertifikat im Querformat."""

    buffer = io.BytesIO()
    width, height = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # Farben (passend zum AI Learning Hub Theme)
    dark_bg = HexColor("#161C24")
    paper_bg = HexColor("#212B36")
    primary = HexColor("#00A76F")
    gold = HexColor("#FFB020")
    white = HexColor("#FFFFFF")
    text_secondary = HexColor("#919EAB")

    # === Hintergrund ===
    c.setFillColor(dark_bg)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Innerer Rahmen (Paper-Farbe)
    margin = 30
    c.setFillColor(paper_bg)
    c.roundRect(
        margin, margin, width - 2 * margin, height - 2 * margin, 15, fill=1, stroke=0
    )

    # Dekorativer Rahmen (Primary Color, dünn)
    c.setStrokeColor(primary)
    c.setLineWidth(2)
    c.roundRect(
        margin + 15,
        margin + 15,
        width - 2 * (margin + 15),
        height - 2 * (margin + 15),
        10,
        fill=0,
        stroke=1,
    )

    # === Eckverzierungen ===
    corner_offset = margin + 25
    corner_size = 8
    c.setFillColor(primary)
    for x, y in [
        (corner_offset, corner_offset),
        (width - corner_offset - corner_size, corner_offset),
        (corner_offset, height - corner_offset - corner_size),
        (
            width - corner_offset - corner_size,
            height - corner_offset - corner_size,
        ),
    ]:
        c.rect(x, y, corner_size, corner_size, fill=1, stroke=0)

    # === Header-Bereich ===
    center_x = width / 2

    # AI Learning Hub Logo/Text
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(center_x, height - 80, "AI LEARNING HUB")

    # Dekorative Linie unter Logo
    line_width = 150
    c.setStrokeColor(primary)
    c.setLineWidth(1)
    c.line(
        center_x - line_width / 2,
        height - 90,
        center_x + line_width / 2,
        height - 90,
    )

    # === Haupttitel ===
    c.setFillColor(gold)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(center_x, height - 140, "ZERTIFIKAT")

    # Untertitel
    c.setFillColor(text_secondary)
    c.setFont("Helvetica", 14)
    c.drawCentredString(center_x, height - 165, "der erfolgreichen Absolvierung")

    # === Name des Absolventen ===
    full_name = f"{user.first_name} {user.last_name}".strip() or user.username

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(center_x, height - 220, full_name)

    # Dekorative Linie unter dem Namen
    name_line_width = max(len(full_name) * 14, 200)
    c.setStrokeColor(gold)
    c.setLineWidth(1.5)
    c.line(
        center_x - name_line_width / 2,
        height - 232,
        center_x + name_line_width / 2,
        height - 232,
    )

    # === Kursdetails ===
    c.setFillColor(text_secondary)
    c.setFont("Helvetica", 13)
    c.drawCentredString(center_x, height - 265, "hat den Lernpfad")

    # Lernpfad-Titel
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 22)
    path_title = f"{learning_path.icon} {learning_path.title}"
    c.drawCentredString(center_x, height - 295, path_title)

    # Schwierigkeitsgrad
    difficulty_map = {
        "beginner": "Einsteiger",
        "intermediate": "Mittelstufe",
        "advanced": "Fortgeschritten",
    }
    difficulty_label = difficulty_map.get(
        learning_path.difficulty, learning_path.difficulty
    )

    c.setFillColor(text_secondary)
    c.setFont("Helvetica", 12)
    c.drawCentredString(
        center_x, height - 320, f"Schwierigkeitsgrad: {difficulty_label}"
    )

    # === Statistiken ===
    lesson_count = learning_path.lessons.count()
    total_xp = sum(l.xp_reward for l in learning_path.lessons.all())

    c.setFont("Helvetica", 11)
    c.setFillColor(text_secondary)
    stats_y = height - 355
    c.drawCentredString(
        center_x,
        stats_y,
        f"{lesson_count} Lektionen abgeschlossen  |  {total_xp} XP erworben",
    )

    # === "erfolgreich abgeschlossen am" ===
    c.setFillColor(text_secondary)
    c.setFont("Helvetica", 13)
    c.drawCentredString(center_x, height - 390, "erfolgreich abgeschlossen am")

    # Datum
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    formatted_date = (
        completed_date.strftime("%d. %B %Y")
        if completed_date
        else datetime.now().strftime("%d. %B %Y")
    )
    # Deutsche Monatsnamen
    month_map = {
        "January": "Januar",
        "February": "Februar",
        "March": "März",
        "April": "April",
        "May": "Mai",
        "June": "Juni",
        "July": "Juli",
        "August": "August",
        "September": "September",
        "October": "Oktober",
        "November": "November",
        "December": "Dezember",
    }
    for en, de in month_map.items():
        formatted_date = formatted_date.replace(en, de)
    c.drawCentredString(center_x, height - 415, formatted_date)

    # === Footer ===
    # Zertifikat-ID
    cert_id = (
        f"AILH-{user.id:04d}-{learning_path.id:02d}-"
        f"{completed_date.strftime('%Y%m%d') if completed_date else datetime.now().strftime('%Y%m%d')}"
    )
    c.setFillColor(text_secondary)
    c.setFont("Helvetica", 8)
    c.drawCentredString(center_x, margin + 35, f"Zertifikat-ID: {cert_id}")

    # "Powered by" Footer
    c.setFont("Helvetica", 9)
    c.drawCentredString(
        center_x, margin + 22, "AI Learning Hub — Powered by Anthropic Claude"
    )

    c.save()
    buffer.seek(0)
    return buffer
