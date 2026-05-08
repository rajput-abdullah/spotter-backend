from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List


def _parse_iso(ts: str) -> datetime:
    if ts is None:
        return None
    # handle trailing Z
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        # fallback: naive parse
        return datetime.strptime(ts.split(".")[0], "%Y-%m-%dT%H:%M:%S")


STATUS_COLORS = {
    "Driving": colors.HexColor("#1f77b4"),
    "Rest": colors.HexColor("#ff7f0e"),
    "Off Duty": colors.HexColor("#2ca02c"),
    "Off Duty (10-hr reset)": colors.HexColor("#2ca02c"),
    "On Duty": colors.HexColor("#9467bd"),
    "Sleeper": colors.HexColor("#8c564b"),
    "Other": colors.HexColor("#7f7f7f"),
}


def _status_color(status: str):
    if not status:
        return STATUS_COLORS["Other"]
    for key in STATUS_COLORS:
        if key.lower() in status.lower():
            return STATUS_COLORS[key]
    return STATUS_COLORS["Other"]


def generate_logs_pdf(plan_data: Dict[str, Any]) -> bytes:
    """
    Produce a multi-page PDF, one page per day in plan_data['eld_logs'].
    Each page contains:
     - header with trip info (if available)
     - a 24-hour horizontal grid (00:00 — 24:00)
     - colored blocks for each duty segment intersecting that day
     - legend
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 0.5 * inch
    content_w = width - 2 * margin
    content_h = height - 2 * margin

    eld_logs: List[Dict[str, Any]] = plan_data.get("eld_logs", []) or []
    if not eld_logs:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, height - margin - 20, "No ELD logs available")
        c.showPage()
        c.save()
        return buffer.getvalue()

    # group segments by local date (YYYY-MM-DD) using start_time
    pages = {}
    for seg in eld_logs:
        st = _parse_iso(seg.get("start_time"))
        et = _parse_iso(seg.get("end_time"))
        if st is None or et is None:
            continue
        # break segments that span multiple dates into per-day pieces
        cursor = st
        while cursor.date() <= et.date():
            day_end = datetime.combine(cursor.date(), datetime.max.time()).replace(tzinfo=cursor.tzinfo)
            seg_end = min(et, day_end)
            pages.setdefault(cursor.date().isoformat(), []).append({
                "start": cursor,
                "end": seg_end,
                "status": seg.get("status")
            })
            cursor = seg_end + timedelta(seconds=1)

    # draw a page per date (sorted)
    for date_str in sorted(pages.keys()):
        segments = pages[date_str]
        # Header
        c.setFont("Helvetica-Bold", 14)
        title = f"Driver's Daily Log — {date_str}"
        c.drawString(margin, height - margin - 10, title)

        # Trip meta if available
        meta_y = height - margin - 30
        meta_vals = []
        if plan_data.get("route_instructions"):
            ri = plan_data["route_instructions"]
            meta_vals.append(f"{ri.get('start_location')} → {ri.get('end_location')}")
            meta_vals.append(f"Distance: {ri.get('distance')} mi")
        # optional driver/vehicle
        driver = plan_data.get("driver_name") or plan_data.get("trip", {}).get("driver_name") or ""
        vehicle = plan_data.get("vehicle_id") or plan_data.get("trip", {}).get("vehicle_id") or ""
        if driver:
            meta_vals.append(f"Driver: {driver}")
        if vehicle:
            meta_vals.append(f"Vehicle: {vehicle}")

        c.setFont("Helvetica", 9)
        x = margin
        for i, mv in enumerate(meta_vals):
            c.drawString(x, meta_y, mv)
            x += 200

        # Grid area
        grid_top = meta_y - 40
        grid_left = margin
        grid_height = 1.25 * inch
        grid_width = content_w
        hour_w = grid_width / 24.0
        hour_h = grid_height

        # Draw hour ticks and labels
        c.setStrokeColor(colors.black)
        c.rect(grid_left, grid_top - grid_height, grid_width, grid_height, stroke=1, fill=0)
        c.setFont("Helvetica", 7)
        for h in range(25):
            x_pos = grid_left + h * hour_w
            c.setStrokeColor(colors.lightgrey)
            c.line(x_pos, grid_top - grid_height, x_pos, grid_top)
            if h < 24:
                label = f"{h:02d}:00"
                c.setFillColor(colors.black)
                c.drawString(x_pos + 2, grid_top - grid_height - 12, label)

        # Draw segments as colored blocks intersecting this date between 00:00 and 24:00
        day_start = datetime.fromisoformat(date_str + "T00:00:00+00:00")
        day_end = day_start + timedelta(days=1)
        for seg in segments:
            s = seg["start"].astimezone(timezone.utc) if seg["start"].tzinfo else seg["start"].replace(tzinfo=timezone.utc)
            e = seg["end"].astimezone(timezone.utc) if seg["end"].tzinfo else seg["end"].replace(tzinfo=timezone.utc)
            # clamp to day
            s_clamped = max(s, day_start)
            e_clamped = min(e, day_end)
            # compute positions
            minutes_from_midnight_start = (s_clamped - day_start).total_seconds() / 60.0
            minutes_from_midnight_end = (e_clamped - day_start).total_seconds() / 60.0
            fraction_start = minutes_from_midnight_start / (24 * 60)
            fraction_end = minutes_from_midnight_end / (24 * 60)
            x0 = grid_left + fraction_start * grid_width
            x1 = grid_left + fraction_end * grid_width
            # draw rect
            color = _status_color(seg.get("status"))
            c.setFillColor(color)
            c.setStrokeColor(color.darker(0.2))
            rect_y = grid_top - grid_height + 4
            rect_h = hour_h - 8
            c.roundRect(x0, rect_y, max(1, x1 - x0), rect_h, 2, stroke=0, fill=1)

        # Legend
        legend_y = grid_top - grid_height - 40
        legend_x = margin
        c.setFont("Helvetica", 9)
        c.drawString(legend_x, legend_y + 20, "Legend:")
        lx = legend_x
        for name, col in STATUS_COLORS.items():
            c.setFillColor(col)
            c.rect(lx, legend_y, 12, 12, fill=1, stroke=0)
            c.setFillColor(colors.black)
            c.drawString(lx + 16, legend_y + 2, name)
            lx += 110
            if lx > width - margin - 100:
                lx = legend_x
                legend_y -= 18

        c.showPage()

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes