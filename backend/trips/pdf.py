from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Dict, Any, List


def generate_logs_pdf(plan_data: Dict[str, Any]) -> bytes:
    """
    Simple multi-page PDF: one page per day/segment grouping.
    plan_data should include 'eld_logs' (list of segments).
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    eld_logs: List[Dict[str, Any]] = plan_data.get("eld_logs", [])
    if not eld_logs:
        c.drawString(50, height - 50, "No ELD logs available")
        c.showPage()
        c.save()
        return buffer.getvalue()

    # group by date (UTC date from start_time)
    pages = {}
    for seg in eld_logs:
        st = seg.get("start_time")
        if not st:
            continue
        date = st.split("T")[0]
        pages.setdefault(date, []).append(seg)

    for date, segments in pages.items():
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 50, f"Driver's Daily Log - {date}")
        c.setFont("Helvetica", 10)
        y = height - 80
        for seg in segments:
            line = f"{seg.get('start_time')} -> {seg.get('end_time')}  : {seg.get('status')}"
            c.drawString(50, y, line)
            y -= 16
            if y < 50:
                c.showPage()
                y = height - 50
        c.showPage()

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes