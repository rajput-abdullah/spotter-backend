from __future__ import annotations

import io
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from reportlab.lib.colors import black, white, HexColor
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# =============================================================================
# PAGE CONFIG
# =============================================================================

PAGE_W, PAGE_H = letter

MARGIN = 26

TOP_Y = PAGE_H - MARGIN

GRID_LEFT = 118
GRID_RIGHT = PAGE_W - 58

TOTAL_COL_W = 58

GRID_W = GRID_RIGHT - GRID_LEFT

HEADER_BAR_H = 18
ROW_H = 26

GRID_TOP = 525
GRID_HEADER_BOTTOM = GRID_TOP - HEADER_BAR_H
GRID_BOTTOM = GRID_HEADER_BOTTOM - (ROW_H * 4)

REMARKS_HEIGHT = 82

# =============================================================================
# STATUS CONFIG
# =============================================================================

STATUS_ROWS = {
    "off": 0,
    "sleeper": 1,
    "driving": 2,
    "on": 3,
}

ROW_LABELS = [
    ("1. Off Duty", "off"),
    ("2. Sleeper Berth", "sleeper"),
    ("3. Driving", "driving"),
    ("4. On Duty (not driving)", "on"),
]

STATUS_COLORS = {
    "off": HexColor("#475569"),
    "sleeper": HexColor("#4f46e5"),
    "driving": HexColor("#16a34a"),
    "on": HexColor("#b45309"),
}

# violation colors
VIOLATION_8H = HexColor("#ef4444")   # >8 continuous driving without 30-min break
VIOLATION_11H = HexColor("#7f1d1d")  # >11 total driving hours in day
VIOLATION_SHIFT = HexColor("#b91c1c")# >11h shift span from first on/driving


# =============================================================================
# HELPERS
# =============================================================================

def _parse_iso(ts: str):
    if not ts:
        return None
    s = str(ts)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except Exception:
        try:
            return datetime.strptime(s.split(".")[0], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        except Exception:
            return None


def _normalize_status(status: str) -> str:
    s = (status or "").lower()
    if "driv" in s:
        return "driving"
    if "sleep" in s:
        return "sleeper"
    if "on" in s and "driv" not in s:
        return "on"
    return "off"


def _fmt_hours(hours: float) -> str:
    h = int(hours)
    m = int(round((hours - h) * 60))
    return f"{h}:{m:02d}"


def _minute_x(minute: float):
    return GRID_LEFT + ((minute / 1440.0) * GRID_W)


def _row_center(status_key: str):
    row = STATUS_ROWS[status_key]
    return GRID_HEADER_BOTTOM - (row * ROW_H) - (ROW_H / 2)


def _draw_wrapped(c, text, x, y, line_h=8):
    for line in text.split("\n"):
        c.drawString(x, y, line)
        y -= line_h


# =============================================================================
# HEADER
# =============================================================================

def _draw_header(
    c,
    day_dt,
    page_num,
    total_pages,
    plan_data,
    day_miles=None,
):
    c.setFont("Helvetica-Bold", 24)
    c.drawString(MARGIN, TOP_Y - 12, "Driver's Daily Log")
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN, TOP_Y - 30, "(24 hours)")

    cx = PAGE_W / 2 - 10
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(cx, TOP_Y - 12, day_dt.strftime("%m   /   %d   /   %Y"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(cx, TOP_Y - 28, "(month)        (day)        (year)")

    c.setFont("Helvetica", 8)
    c.drawRightString(PAGE_W - MARGIN, TOP_Y - 8, "Original — File at home terminal.")
    c.drawRightString(PAGE_W - MARGIN, TOP_Y - 22, "Duplicate — Driver retains in his/her possession for 8 days.")
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(PAGE_W - MARGIN, TOP_Y - 40, f"Day {page_num} of {total_pages}")

    route = plan_data.get("route_instructions", {})
    from_loc = route.get("start_location", "")
    to_loc = route.get("end_location", "")

    y = TOP_Y - 62
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, y, "From:")
    c.line(MARGIN + 65, y - 3, 275, y - 3)
    c.setFont("Helvetica", 12)
    c.drawString(MARGIN + 72, y, from_loc)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(295, y, "To:")
    c.line(335, y - 3, PAGE_W - MARGIN, y - 3)
    c.setFont("Helvetica", 12)
    c.drawString(343, y, to_loc)

    y2 = y - 16
    box_w = 140
    box_h = 42
    c.rect(MARGIN, y2 - box_h, box_w, box_h)
    c.rect(MARGIN + box_w + 8, y2 - box_h, box_w, box_h)

    miles = day_miles if day_miles is not None else int(plan_data.get("total_distance_miles") or 0)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(MARGIN + (box_w / 2), y2 - 25, f"{miles} mi")
    c.drawCentredString(MARGIN + box_w + 8 + (box_w / 2), y2 - 25, f"{miles} mi")

    c.setFont("Helvetica", 8)
    c.drawString(MARGIN + 4, y2 - box_h - 12, "Total Miles Driving Today")
    c.drawString(MARGIN + box_w + 12, y2 - box_h - 12, "Total Mileage Today")

    rx = 305
    c.line(rx, y2 - 10, PAGE_W - MARGIN, y2 - 10)
    c.line(rx, y2 - 22, PAGE_W - MARGIN, y2 - 22)
    c.line(rx, y2 - 34, PAGE_W - MARGIN, y2 - 34)
    c.setFont("Helvetica", 8)
    c.drawString(rx, y2 - 20, "Name of Carrier or Carriers")
    c.drawString(rx, y2 - 32, "Main Office Address")
    c.drawString(rx, y2 - 44, "Home Terminal Address")

    y3 = y2 - box_h - 20
    c.line(MARGIN, y3, 288, y3)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, y3 - 10,
                 "Truck/Tractor and Trailer Numbers or License Plate(s)/State (show each unit)")


# =============================================================================
# GRID
# =============================================================================

def _draw_grid(c):
    col_w = GRID_W / 24.0
    c.setFillColor(black)
    c.rect(GRID_LEFT, GRID_HEADER_BOTTOM, GRID_W + TOTAL_COL_W, HEADER_BAR_H, stroke=0, fill=1)

    labels = [
        "Mid-\nnight",
        "1","2","3","4","5","6","7","8","9","10","11",
        "Noon",
        "1","2","3","4","5","6","7","8","9","10","11",
        "Mid-\nnight"
    ]
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 7)
    for h, lbl in enumerate(labels):
        x = GRID_LEFT + (h * col_w)
        if "\n" in lbl:
            a, b = lbl.split("\n")
            c.drawCentredString(x, GRID_HEADER_BOTTOM + 8, a)
            c.drawCentredString(x, GRID_HEADER_BOTTOM + 2, b)
        else:
            c.drawCentredString(x, GRID_HEADER_BOTTOM + 5, lbl)

    cx = GRID_RIGHT + (TOTAL_COL_W / 2)
    c.drawCentredString(cx, GRID_HEADER_BOTTOM + 8, "Total")
    c.drawCentredString(cx, GRID_HEADER_BOTTOM + 2, "Hours")

    c.setFillColor(black)
    c.setStrokeColor(black)
    c.setLineWidth(0.8)
    c.rect(GRID_LEFT, GRID_BOTTOM, GRID_W, ROW_H * 4)
    c.rect(GRID_RIGHT, GRID_BOTTOM, TOTAL_COL_W, ROW_H * 4)

    for i in range(1, 4):
        y = GRID_HEADER_BOTTOM - (ROW_H * i)
        c.line(GRID_LEFT, y, GRID_RIGHT + TOTAL_COL_W, y)

    c.setLineWidth(0.5)
    for h in range(25):
        x = GRID_LEFT + (h * col_w)
        c.line(x, GRID_BOTTOM, x, GRID_HEADER_BOTTOM)

    c.setLineWidth(0.25)
    for h in range(24):
        x_left = GRID_LEFT + (h * col_w)
        for q in (1, 2, 3):
            qx = x_left + (col_w * (q / 4.0))
            for r in range(4):
                ry_top = GRID_HEADER_BOTTOM - (ROW_H * r)
                ry_bot = ry_top - ROW_H
                tick = 5 if q == 2 else 3
                c.line(qx, ry_bot, qx, ry_bot + tick)
                c.line(qx, ry_top, qx, ry_top - tick)

    c.setFont("Helvetica", 10)
    for i, (label, _) in enumerate(ROW_LABELS):
        y = GRID_HEADER_BOTTOM - (ROW_H * (i + 0.5)) - 3
        c.drawRightString(GRID_LEFT - 6, y, label)


# =============================================================================
# DUTY GRAPH - HOS state-machine with ELD-style line drawing
# =============================================================================

def _draw_duty_graph(c, segments, plan_data=None):
    """
    Simulate the full HOS trip-planning algorithm and draw the result as an
    ELD-style duty line (horizontal per status, vertical at transitions).

    Rules applied in order:
      1. 1h ON_DUTY pickup before first driving segment
      2. 15-min ON_DUTY fuel stop every 1000 miles
      3. 30-min OFF break after 8h continuous driving
      4. 10h SLEEPER reset after 11h total driving OR 14h on-duty window
      5. Gaps auto-filled as OFF_DUTY
      6. 70h/8-day cycle warning
    """
    if not segments:
        return

    segments = sorted(segments, key=lambda x: x["start"])

    pickup_loc = (plan_data.get("pickup_location") or "") if plan_data else ""

    # ── 1. Prepend 1-hour ON_DUTY (pickup/loading) before first driving ──────
    if _normalize_status(segments[0].get("status")) == "driving":
        fs = segments[0]["start"]
        on_start = fs - timedelta(hours=1)
        day_start = datetime(fs.year, fs.month, fs.day, tzinfo=fs.tzinfo)
        if on_start >= day_start:
            segments.insert(0, {
                "start": on_start, "end": fs,
                "status": "On Duty", "remark": "Loading/Pickup",
                "location": pickup_loc,
            })

    # ── 2. Compute fuel-stop minute-of-day markers ────────────────────────────
    fuel_minutes: List[float] = []
    if plan_data:
        route = plan_data.get("route_instructions") or {}
        total_miles = float(plan_data.get("total_distance_miles") or 0)
        explicit = route.get("fuel_stops") or []

        driving_parts = [
            (s["start"], s["end"])
            for s in segments
            if _normalize_status(s.get("status")) == "driving"
        ]
        total_drive_secs = sum((e - s).total_seconds() for s, e in driving_parts)

        def _mile_to_minute(mile_marker: float):
            if total_miles <= 0 or total_drive_secs <= 0:
                return None
            frac = min(0.9999, mile_marker / total_miles)
            target = frac * total_drive_secs
            acc = 0.0
            for sdt, edt in driving_parts:
                seg_secs = (edt - sdt).total_seconds()
                if acc + seg_secs >= target:
                    mark = sdt + timedelta(seconds=target - acc)
                    return mark.hour * 60 + mark.minute + mark.second / 60.0
                acc += seg_secs
            return None

        if explicit:
            for fs_item in explicit:
                try:
                    m = _mile_to_minute(float(fs_item.get("mile_marker", 0)))
                    if m is not None:
                        fuel_minutes.append(m)
                except Exception:
                    pass
        elif total_miles >= 1000:
            mi = 1000.0
            while mi < total_miles:
                m = _mile_to_minute(mi)
                if m is not None:
                    fuel_minutes.append(m)
                mi += 1000.0

    # ── 3. Splice 15-min ON_DUTY fuel stops into driving segments ─────────────
    for fm in sorted(fuel_minutes):
        rebuilt: List[Dict[str, Any]] = []
        for seg in segments:
            if _normalize_status(seg.get("status")) != "driving":
                rebuilt.append(seg)
                continue
            sdt, edt = seg["start"], seg["end"]
            smin = sdt.hour * 60 + sdt.minute + sdt.second / 60.0
            emin = edt.hour * 60 + edt.minute + edt.second / 60.0
            if not (smin < fm < emin):
                rebuilt.append(seg)
                continue
            fuel_dt = sdt + timedelta(minutes=fm - smin)
            fuel_end = min(fuel_dt + timedelta(minutes=15), edt)
            if fuel_dt > sdt:
                rebuilt.append({"start": sdt, "end": fuel_dt,
                                 "status": seg["status"], "remark": seg.get("remark", "")})
            rebuilt.append({"start": fuel_dt, "end": fuel_end,
                             "status": "On Duty", "remark": "Fuel Stop",
                             "location": "Fuel Stop"})
            if fuel_end < edt:
                rebuilt.append({"start": fuel_end, "end": edt,
                                 "status": seg["status"], "remark": seg.get("remark", "")})
        segments = rebuilt

    # ── 4. HOS state-machine → build final drawable segment list ─────────────
    drawable: List[Dict[str, Any]] = []
    totals: Dict[str, float] = defaultdict(float)

    total_driving = 0.0        # hours driving this shift (resets after 10h rest)
    continuous_driving = 0.0   # hours driving since last ≥30-min break
    shift_start = None          # start of 14-hour on-duty window

    def _emit(sdt: datetime, edt: datetime, status_key: str,
              color=None, location: str = "", remark: str = ""):
        if edt <= sdt:
            return
        drawable.append({
            "start": sdt, "end": edt,
            "status": status_key,
            "color": color or STATUS_COLORS.get(status_key, HexColor("#6b7280")),
            "location": location,
            "remark": remark,
        })
        totals[status_key] += (edt - sdt).total_seconds() / 3600.0

    for seg in segments:
        st: datetime = seg["start"]
        et: datetime = seg["end"]
        status   = _normalize_status(seg.get("status", "off"))
        seg_loc  = seg.get("location", "")
        seg_rmk  = seg.get("remark", "")

        # ── OFF / SLEEPER ─────────────────────────────────────────────────────
        if status in ("off", "sleeper"):
            _emit(st, et, status, location=seg_loc, remark=seg_rmk)
            dur = (et - st).total_seconds()
            if dur >= 30 * 60:
                continuous_driving = 0.0
            if dur >= 10 * 3600:
                total_driving = 0.0
                continuous_driving = 0.0
                shift_start = None
            continue

        # ── ON DUTY (not driving) ─────────────────────────────────────────────
        if status == "on":
            if shift_start is None:
                shift_start = st
            _emit(st, et, "on", location=seg_loc, remark=seg_rmk)
            continue

        # ── DRIVING ──────────────────────────────────────────────────────────
        # Start the 14-hour window on first on/driving activity
        if shift_start is None:
            shift_start = st

        ptr = st
        first_drive_part = True
        while ptr < et:
            rem = (et - ptr).total_seconds()
            shift_h = (ptr - shift_start).total_seconds() / 3600.0
            day_end = datetime(ptr.year, ptr.month, ptr.day,
                               23, 59, 59, tzinfo=ptr.tzinfo)

            secs_8  = max(0.0, (8.0  - continuous_driving) * 3600.0)
            secs_11 = max(0.0, (11.0 - total_driving)      * 3600.0)
            secs_14 = max(0.0, (14.0 - shift_h)            * 3600.0)

            # ── already at a hard limit → 10h sleeper reset ───────────────
            if secs_11 <= 1e-3 or secs_14 <= 1e-3:
                sleep_end = min(ptr + timedelta(hours=10), day_end)
                _emit(ptr, sleep_end, "sleeper",
                      location=seg_loc, remark="10hr Reset")
                total_driving = 0.0
                continuous_driving = 0.0
                shift_start = None
                ptr = sleep_end
                break  # no more driving today after forced reset

            # ── 8h continuous limit → 30-min OFF break ────────────────────
            if secs_8 <= 1e-3:
                break_end = min(ptr + timedelta(minutes=30), day_end)
                _emit(ptr, break_end, "off",
                      location=seg_loc, remark="30-min Break")
                continuous_driving = 0.0
                ptr = break_end
                if shift_start is None:
                    shift_start = ptr
                first_drive_part = False
                continue

            # ── Drive until nearest constraint ────────────────────────────
            part_secs = min(rem, secs_8, secs_11, secs_14)
            if part_secs <= 0:
                break
            part_end = ptr + timedelta(seconds=part_secs)
            # Only attach location/remark to the first part of a driving seg
            _emit(ptr, part_end, "driving",
                  location=seg_loc if first_drive_part else "",
                  remark=seg_rmk  if first_drive_part else "")
            part_h = part_secs / 3600.0
            total_driving      += part_h
            continuous_driving += part_h
            first_drive_part = False
            ptr = part_end

    # ── 5. Auto-fill uncovered time gaps with OFF_DUTY ────────────────────────
    if drawable:
        drawable.sort(key=lambda x: x["start"])
        ref = drawable[0]["start"]
        day_start_dt = datetime(ref.year, ref.month, ref.day,
                                0, 0, 0, tzinfo=ref.tzinfo)
        day_end_dt   = datetime(ref.year, ref.month, ref.day,
                                23, 59, 59, tzinfo=ref.tzinfo)
        filled: List[Dict[str, Any]] = []
        cursor = day_start_dt
        for d in drawable:
            if d["start"] > cursor + timedelta(seconds=60):
                gap_h = (d["start"] - cursor).total_seconds() / 3600.0
                filled.append({"start": cursor, "end": d["start"],
                                "status": "off", "color": STATUS_COLORS["off"]})
                totals["off"] += gap_h
            filled.append(d)
            cursor = d["end"]
        if cursor < day_end_dt - timedelta(minutes=1):
            tail_h = (day_end_dt - cursor).total_seconds() / 3600.0
            filled.append({"start": cursor, "end": day_end_dt,
                            "status": "off", "color": STATUS_COLORS["off"]})
            totals["off"] += tail_h
        drawable = filled

    # ── 6. Draw the duty status line ──────────────────────────────────────────
    #   • Horizontal line  = status duration at that row
    #   • Vertical line    = instant status transition
    prev_y = None
    for d in drawable:
        st   = d["start"]
        et   = d["end"]
        row_y = _row_center(d["status"])

        smin = st.hour * 60 + st.minute + st.second / 60.0
        emin = et.hour * 60 + et.minute + et.second / 60.0
        x1 = _minute_x(smin)
        x2 = max(_minute_x(emin), x1 + 0.5)

        # vertical transition between status rows
        if prev_y is not None and abs(prev_y - row_y) > 0.5:
            c.setStrokeColor(black)
            c.setLineWidth(1.5)
            c.line(x1, prev_y, x1, row_y)

        # horizontal duty line
        c.setStrokeColor(d["color"])
        c.setLineWidth(2.0)
        c.line(x1, row_y, x2, row_y)
        prev_y = row_y

    # ── 7. Totals column ──────────────────────────────────────────────────────
    cx = GRID_RIGHT + (TOTAL_COL_W / 2)
    c.setFillColor(black)
    for i, (_, key) in enumerate(ROW_LABELS):
        y = GRID_HEADER_BOTTOM - (ROW_H * (i + 0.5)) - 5
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(cx, y, _fmt_hours(totals.get(key, 0.0)))
    total_all = sum(totals.values())
    c.setFont("Helvetica", 9)
    c.drawCentredString(cx, GRID_BOTTOM - 12, f"Σ {_fmt_hours(total_all)}")

    # ── 8. Footer rule-counter summary ────────────────────────────────────────
    c.setFont("Helvetica", 7)
    c.setFillColor(HexColor("#334155"))
    c.drawCentredString(
        PAGE_W / 2, GRID_BOTTOM - 28,
        f"Driving today: {_fmt_hours(totals.get('driving', 0.0))} / 11h  |  "
        f"Continuous: {_fmt_hours(continuous_driving)} / 8h",
    )

    # ── 9. 70-hour / 8-day cycle warning ─────────────────────────────────────
    if plan_data:
        try:
            used = float(plan_data.get("current_cycle_used_hrs") or 0.0)
            if used >= 70.0:
                c.setFont("Helvetica-Bold", 8)
                c.setFillColor(VIOLATION_11H)
                c.drawCentredString(
                    PAGE_W / 2, GRID_BOTTOM - 40,
                    "Cycle: 70-hour limit exceeded — driver must take required off-duty time before driving",
                )
        except Exception:
            pass

    return drawable


# =============================================================================
# REMARKS
# =============================================================================

def _draw_remarks(c, remarks):
    col_w = GRID_W / 24.0
    c.setStrokeColor(HexColor("#94a3b8"))
    c.setLineWidth(0.3)
    for h in range(25):
        x = GRID_LEFT + (h * col_w)
        c.line(x, GRID_BOTTOM, x, GRID_BOTTOM - REMARKS_HEIGHT)
    c.setStrokeColor(black)
    c.line(GRID_LEFT, GRID_BOTTOM - REMARKS_HEIGHT, GRID_RIGHT, GRID_BOTTOM - REMARKS_HEIGHT)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN, GRID_BOTTOM - 20, "Remarks")

    if remarks:
        for r in remarks:
            minute = r["minute"]
            x = _minute_x(minute)
            # tick mark below the grid
            c.setStrokeColor(black)
            c.setLineWidth(1)
            c.line(x, GRID_BOTTOM, x, GRID_BOTTOM - 8)
            c.saveState()
            c.translate(x + 3, GRID_BOTTOM - 10)
            c.rotate(-63)
            loc   = r.get("location", "")
            label = r.get("label", "")
            time_str = r.get("time", "")
            y_off = 0
            if loc:
                c.setFont("Helvetica-Bold", 7)
                c.setFillColor(black)
                c.drawString(0, y_off, loc)
                y_off -= 9
            if label:
                c.setFont("Helvetica", 7)
                c.setFillColor(black)
                c.drawString(0, y_off, f"{time_str} {label}" if time_str and not loc else label)
            c.restoreState()

    y = GRID_BOTTOM - REMARKS_HEIGHT - 22
    c.setFont("Helvetica-Bold", 10)
    fields = [
        "Shipping Documents:",
        "DVL or Manifest No.:",
        "Shipper & Commodity:"
    ]
    for field in fields:
        c.drawString(MARGIN, y, field)
        c.line(130, y - 2, GRID_RIGHT, y - 2)
        y -= 18
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(PAGE_W / 2, y - 4,
                        "Enter name of place you reported and where released from work, and when and where each change of duty occurred.")
    c.drawCentredString(PAGE_W / 2, y - 16, "Use time standard of home terminal.")
    return y - 28


# =============================================================================
# RECAP
# =============================================================================

def _draw_recap(c, top_y, plan_data):
    box_h = 110
    y_bottom = top_y - box_h
    left_x = MARGIN
    c.rect(left_x, y_bottom, 62, box_h)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_x + 4, top_y - 14, "Recap:")
    c.setFont("Helvetica", 8)
    _draw_wrapped(c, "Complete at end of day", left_x + 4, top_y - 28)
    c.drawString(left_x + 4, y_bottom + 32, "On duty hours")
    c.drawString(left_x + 4, y_bottom + 20, "today, Total")
    c.drawString(left_x + 4, y_bottom + 8, "lines 3 & 4")

    sec1_x = left_x + 66
    sec_w = 218
    c.rect(sec1_x, y_bottom, sec_w, box_h)
    c.line(sec1_x, top_y - 24, sec1_x + sec_w, top_y - 24)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(sec1_x + (sec_w / 2), top_y - 16, "70 Hour / 8 Day Drivers")
    sub_w = sec_w / 3
    for i in range(1, 3):
        c.line(sec1_x + (sub_w * i), y_bottom, sec1_x + (sub_w * i), top_y - 24)
    titles = ["A.", "B.", "C."]
    descs = [
        "Total hours on\nduty last 7 days\nincluding today.",
        "Total hours\navailable\ntomorrow\n70 hr. minus A*.",
        "Total hours on\nduty last 5 days\nincluding today."
    ]
    for i in range(3):
        x = sec1_x + (sub_w * i) + 6
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, top_y - 40, titles[i])
        c.setFont("Helvetica", 8)
        _draw_wrapped(c, descs[i], x, top_y - 54)

    sec2_x = sec1_x + sec_w + 6
    c.rect(sec2_x, y_bottom, sec_w, box_h)
    c.line(sec2_x, top_y - 24, sec2_x + sec_w, top_y - 24)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(sec2_x + (sec_w / 2), top_y - 16, "60 Day / 7 Day Drivers")
    for i in range(1, 3):
        c.line(sec2_x + (sub_w * i), y_bottom, sec2_x + (sub_w * i), top_y - 24)
    descs2 = [
        "Total hours on\nduty last 8 days\nincluding today.",
        "Total hours\navailable\ntomorrow\n60 hr. minus A*.",
        "Total hours on\nduty last 7 days\nincluding today."
    ]
    for i in range(3):
        x = sec2_x + (sub_w * i) + 6
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, top_y - 40, titles[i])
        c.setFont("Helvetica", 8)
        _draw_wrapped(c, descs2[i], x, top_y - 54)

    note_x = sec2_x + sec_w + 6
    note_w = PAGE_W - MARGIN - note_x
    c.rect(note_x, y_bottom, note_w, box_h)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(note_x + 4, top_y - 16, "*If you took")
    c.setFont("Helvetica", 8)
    _draw_wrapped(c, "34 consecutive\nhours off duty\nyou have 60/70\nhours\navailable", note_x + 4, top_y - 30)

    c.setFont("Helvetica", 9)
    miles = int(plan_data.get("total_distance_miles", 0))
    summary = (f"Trip plan: {len(plan_data.get('eld_logs', []))}-segment trip, {miles} mi.")
    c.drawString(MARGIN, y_bottom - 18, summary)


def build_log_pdf(plan_data):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    eld_logs = plan_data.get("eld_logs", [])
    if not eld_logs:
        c.setFont("Helvetica", 18)
        c.drawString(100, 700, "No ELD logs found")
        c.save()
        pdf = buf.getvalue()
        buf.close()
        return pdf

    # group segments by calendar day (split multi-day segments)
    pages = defaultdict(list)
    for seg in eld_logs:
        st = _parse_iso(seg.get("start_time"))
        et = _parse_iso(seg.get("end_time"))
        if not st or not et:
            continue
        if st.tzinfo is None:
            st = st.replace(tzinfo=timezone.utc)
        if et.tzinfo is None:
            et = et.replace(tzinfo=timezone.utc)
        cursor = st
        while cursor < et:
            day_start = datetime(cursor.year, cursor.month, cursor.day, tzinfo=cursor.tzinfo)
            next_day = day_start + timedelta(days=1)
            seg_end = min(et, next_day)
            key = day_start.date().isoformat()
            pages[key].append({
                "start": cursor,
                "end": seg_end,
                "status": seg.get("status", "Off Duty"),
                "remark": seg.get("remark", ""),
                "location": seg.get("location", ""),
            })
            cursor = seg_end

    total_trip_miles = float(plan_data.get("total_distance_miles") or 0)
    total_driving_secs_all = sum(
        (seg["end"] - seg["start"]).total_seconds()
        for day_segs in pages.values()
        for seg in day_segs
        if _normalize_status(seg.get("status", "off")) == "driving"
    )

    sorted_days = sorted(pages.keys())
    for idx, day in enumerate(sorted_days, start=1):
        segments = pages[day]
        day_dt = datetime.fromisoformat(day)

        # Proportion of total trip miles driven on this calendar day
        if total_driving_secs_all > 0 and total_trip_miles > 0:
            day_driving_secs = sum(
                (seg["end"] - seg["start"]).total_seconds()
                for seg in segments
                if _normalize_status(seg.get("status", "off")) == "driving"
            )
            day_miles = int(round(total_trip_miles * day_driving_secs / total_driving_secs_all))
        else:
            day_miles = int(total_trip_miles) if len(sorted_days) == 1 else 0

        _draw_header(c, day_dt, idx, len(sorted_days), plan_data, day_miles=day_miles)
        _draw_grid(c)
        drawable = _draw_duty_graph(c, segments, plan_data)

        # Build remarks at every status transition in the processed drawable list.
        _STATUS_LABEL = {
            "off":     "Off Duty",
            "sleeper": "Sleeper Berth",
            "driving": "Driving",
            "on":      "On Duty (Not Driving)",
        }
        remarks = []
        seen_minutes: set = set()
        prev_status = None
        for d in (drawable or []):
            status = d["status"]
            if status == prev_status:
                prev_status = status
                continue  # same status, no transition
            prev_status = status

            st = d["start"]
            minute = st.hour * 60 + st.minute
            loc   = d.get("location", "")
            label = d.get("remark", "") or _STATUS_LABEL.get(status, "")

            # Skip silent auto-filled midnight gap (no location, no remark, at 00:00)
            if minute == 0 and not d.get("location") and not d.get("remark"):
                continue

            if minute in seen_minutes:
                continue
            seen_minutes.add(minute)
            remarks.append({
                "minute":   minute,
                "time":     st.strftime("%I:%M %p"),
                "location": loc,
                "label":    label,
            })
        next_y = _draw_remarks(c, remarks)
        _draw_recap(c, next_y, plan_data)
        c.showPage()

    c.save()
    pdf = buf.getvalue()
    buf.close()
    return pdf


def generate_logs_pdf(plan_data):
    return build_log_pdf(plan_data)
# ...existing code...