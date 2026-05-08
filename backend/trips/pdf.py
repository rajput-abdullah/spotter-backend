# from __future__ import annotations

# import io
# from collections import defaultdict
# from datetime import datetime, timedelta, timezone
# from typing import Dict, Any, List

# from reportlab.lib.colors import black, white, HexColor
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas

# # =============================================================================
# # PAGE CONFIG
# # =============================================================================

# PAGE_W, PAGE_H = letter

# MARGIN = 26

# TOP_Y = PAGE_H - MARGIN

# GRID_LEFT = 118
# GRID_RIGHT = PAGE_W - 58

# TOTAL_COL_W = 58

# GRID_W = GRID_RIGHT - GRID_LEFT

# HEADER_BAR_H = 18
# ROW_H = 26

# GRID_TOP = 525
# GRID_HEADER_BOTTOM = GRID_TOP - HEADER_BAR_H
# GRID_BOTTOM = GRID_HEADER_BOTTOM - (ROW_H * 4)

# REMARKS_HEIGHT = 82

# # =============================================================================
# # STATUS CONFIG
# # =============================================================================

# STATUS_ROWS = {
#     "off": 0,
#     "sleeper": 1,
#     "driving": 2,
#     "on": 3,
# }

# ROW_LABELS = [
#     ("1. Off Duty", "off"),
#     ("2. Sleeper Berth", "sleeper"),
#     ("3. Driving", "driving"),
#     ("4. On Duty (not driving)", "on"),
# ]

# STATUS_COLORS = {
#     "off": HexColor("#475569"),
#     "sleeper": HexColor("#4f46e5"),
#     "driving": HexColor("#16a34a"),
#     "on": HexColor("#b45309"),
# }

# # =============================================================================
# # HELPERS
# # =============================================================================

# def _parse_iso(ts: str):

#     if not ts:
#         return None

#     if ts.endswith("Z"):
#         ts = ts[:-1] + "+00:00"

#     try:
#         return datetime.fromisoformat(ts)

#     except Exception:
#         return datetime.strptime(
#             ts.split(".")[0],
#             "%Y-%m-%dT%H:%M:%S"
#         )


# def _normalize_status(status: str) -> str:

#     s = (status or "").lower()

#     if "driv" in s:
#         return "driving"

#     if "sleep" in s:
#         return "sleeper"

#     if "on" in s:
#         return "on"

#     return "off"


# def _fmt_hours(hours: float) -> str:

#     h = int(hours)
#     m = int(round((hours - h) * 60))

#     return f"{h}:{m:02d}"


# def _minute_x(minute: float):

#     return GRID_LEFT + ((minute / 1440.0) * GRID_W)


# def _row_center(status_key: str):

#     row = STATUS_ROWS[status_key]

#     return GRID_HEADER_BOTTOM - (row * ROW_H) - (ROW_H / 2)


# def _draw_wrapped(c, text, x, y, line_h=8):

#     for line in text.split("\n"):
#         c.drawString(x, y, line)
#         y -= line_h


# # =============================================================================
# # HEADER
# # =============================================================================

# def _draw_header(
#     c,
#     day_dt,
#     page_num,
#     total_pages,
#     plan_data,
# ):

#     # =========================================================
#     # TITLE
#     # =========================================================

#     c.setFont("Helvetica-Bold", 24)

#     c.drawString(
#         MARGIN,
#         TOP_Y - 12,
#         "Driver's Daily Log"
#     )

#     c.setFont("Helvetica", 10)

#     c.drawString(
#         MARGIN,
#         TOP_Y - 30,
#         "(24 hours)"
#     )

#     # =========================================================
#     # DATE
#     # =========================================================

#     cx = PAGE_W / 2 - 10

#     c.setFont("Helvetica-Bold", 15)

#     c.drawCentredString(
#         cx,
#         TOP_Y - 12,
#         day_dt.strftime("%m   /   %d   /   %Y")
#     )

#     c.setFont("Helvetica", 8)

#     c.drawCentredString(
#         cx,
#         TOP_Y - 28,
#         "(month)        (day)        (year)"
#     )

#     # =========================================================
#     # RIGHT NOTES
#     # =========================================================

#     c.setFont("Helvetica", 8)

#     c.drawRightString(
#         PAGE_W - MARGIN,
#         TOP_Y - 8,
#         "Original — File at home terminal."
#     )

#     c.drawRightString(
#         PAGE_W - MARGIN,
#         TOP_Y - 22,
#         "Duplicate — Driver retains in his/her possession for 8 days."
#     )

#     c.setFont("Helvetica-Bold", 10)

#     c.drawRightString(
#         PAGE_W - MARGIN,
#         TOP_Y - 40,
#         f"Day {page_num} of {total_pages}"
#     )

#     # =========================================================
#     # FROM / TO
#     # =========================================================

#     route = plan_data.get("route_instructions", {})

#     from_loc = route.get("start_location", "")
#     to_loc = route.get("end_location", "")

#     y = TOP_Y - 62

#     c.setFont("Helvetica-Bold", 14)

#     c.drawString(MARGIN, y, "From:")

#     c.line(MARGIN + 65, y - 3, 275, y - 3)

#     c.setFont("Helvetica", 12)

#     c.drawString(MARGIN + 72, y, from_loc)

#     c.setFont("Helvetica-Bold", 14)

#     c.drawString(295, y, "To:")

#     c.line(335, y - 3, PAGE_W - MARGIN, y - 3)

#     c.setFont("Helvetica", 12)

#     c.drawString(343, y, to_loc)

#     # =========================================================
#     # MILEAGE BOXES
#     # =========================================================

#     y2 = y - 16

#     box_w = 140
#     box_h = 42

#     c.rect(
#         MARGIN,
#         y2 - box_h,
#         box_w,
#         box_h
#     )

#     c.rect(
#         MARGIN + box_w + 8,
#         y2 - box_h,
#         box_w,
#         box_h
#     )

#     miles = int(
#         plan_data.get(
#             "total_distance_miles",
#             0
#         )
#     )

#     c.setFont(
#         "Helvetica-Bold",
#         18
#     )

#     c.drawCentredString(
#         MARGIN + (box_w / 2),
#         y2 - 25,
#         f"{miles} mi"
#     )

#     c.drawCentredString(
#         MARGIN + box_w + 8 + (box_w / 2),
#         y2 - 25,
#         f"{miles} mi"
#     )

#     c.setFont(
#         "Helvetica",
#         8
#     )

#     c.drawString(
#         MARGIN + 4,
#         y2 - box_h - 12,
#         "Total Miles Driving Today"
#     )

#     c.drawString(
#         MARGIN + box_w + 12,
#         y2 - box_h - 12,
#         "Total Mileage Today"
#     )

#     # =========================================================
#     # CARRIER LINES
#     # =========================================================

#     rx = 305

#     c.line(rx, y2 - 10, PAGE_W - MARGIN, y2 - 10)
#     c.line(rx, y2 - 22, PAGE_W - MARGIN, y2 - 22)
#     c.line(rx, y2 - 34, PAGE_W - MARGIN, y2 - 34)

#     c.setFont("Helvetica", 8)

#     c.drawString(rx, y2 - 20, "Name of Carrier or Carriers")
#     c.drawString(rx, y2 - 32, "Main Office Address")
#     c.drawString(rx, y2 - 44, "Home Terminal Address")

#     # =========================================================
#     # TRAILER LINE
#     # =========================================================

#     y3 = y2 - box_h - 20

#     c.line(MARGIN, y3, 288, y3)

#     c.setFont("Helvetica", 8)

#     c.drawString(
#         MARGIN,
#         y3 - 10,
#         "Truck/Tractor and Trailer Numbers or License Plate(s)/State (show each unit)"
#     )


# # =============================================================================
# # GRID
# # =============================================================================

# def _draw_grid(c):

#     col_w = GRID_W / 24.0

#     # =========================================================
#     # BLACK HEADER BAR
#     # =========================================================

#     c.setFillColor(black)

#     c.rect(
#         GRID_LEFT,
#         GRID_HEADER_BOTTOM,
#         GRID_W + TOTAL_COL_W,
#         HEADER_BAR_H,
#         stroke=0,
#         fill=1
#     )

#     labels = [
#         "Mid-\nnight",
#         "1","2","3","4","5","6","7","8","9","10","11",
#         "Noon",
#         "1","2","3","4","5","6","7","8","9","10","11",
#         "Mid-\nnight"
#     ]

#     c.setFillColor(white)

#     c.setFont("Helvetica-Bold", 7)

#     for h, lbl in enumerate(labels):

#         x = GRID_LEFT + (h * col_w)

#         if "\n" in lbl:

#             a, b = lbl.split("\n")

#             c.drawCentredString(x, GRID_HEADER_BOTTOM + 8, a)
#             c.drawCentredString(x, GRID_HEADER_BOTTOM + 2, b)

#         else:

#             c.drawCentredString(
#                 x,
#                 GRID_HEADER_BOTTOM + 5,
#                 lbl
#             )

#     # =========================================================
#     # TOTAL HOURS HEADER
#     # =========================================================

#     cx = GRID_RIGHT + (TOTAL_COL_W / 2)

#     c.drawCentredString(
#         cx,
#         GRID_HEADER_BOTTOM + 8,
#         "Total"
#     )

#     c.drawCentredString(
#         cx,
#         GRID_HEADER_BOTTOM + 2,
#         "Hours"
#     )

#     # =========================================================
#     # GRID BODY
#     # =========================================================

#     c.setFillColor(black)

#     c.setStrokeColor(black)

#     c.setLineWidth(0.8)

#     c.rect(
#         GRID_LEFT,
#         GRID_BOTTOM,
#         GRID_W,
#         ROW_H * 4
#     )

#     c.rect(
#         GRID_RIGHT,
#         GRID_BOTTOM,
#         TOTAL_COL_W,
#         ROW_H * 4
#     )

#     # =========================================================
#     # HORIZONTAL ROWS
#     # =========================================================

#     for i in range(1, 4):

#         y = GRID_HEADER_BOTTOM - (ROW_H * i)

#         c.line(
#             GRID_LEFT,
#             y,
#             GRID_RIGHT + TOTAL_COL_W,
#             y
#         )

#     # =========================================================
#     # HOUR LINES
#     # =========================================================

#     c.setLineWidth(0.5)

#     for h in range(25):

#         x = GRID_LEFT + (h * col_w)

#         c.line(
#             x,
#             GRID_BOTTOM,
#             x,
#             GRID_HEADER_BOTTOM
#         )

#     # =========================================================
#     # QUARTER HOUR TICKS
#     # =========================================================

#     c.setLineWidth(0.25)

#     for h in range(24):

#         x_left = GRID_LEFT + (h * col_w)

#         for q in (1, 2, 3):

#             qx = x_left + (col_w * (q / 4.0))

#             for r in range(4):

#                 ry_top = GRID_HEADER_BOTTOM - (ROW_H * r)
#                 ry_bot = ry_top - ROW_H

#                 tick = 5 if q == 2 else 3

#                 c.line(qx, ry_bot, qx, ry_bot + tick)
#                 c.line(qx, ry_top, qx, ry_top - tick)

#     # =========================================================
#     # LABELS
#     # =========================================================

#     c.setFont("Helvetica", 10)

#     for i, (label, _) in enumerate(ROW_LABELS):

#         y = GRID_HEADER_BOTTOM - (ROW_H * (i + 0.5)) - 3

#         c.drawRightString(
#             GRID_LEFT - 6,
#             y,
#             label
#         )


# # =============================================================================
# # DUTY GRAPH
# # =============================================================================

# # =============================================================================
# # DUTY GRAPH
# # =============================================================================

# def _draw_duty_graph(c, segments):

#     if not segments:
#         return

#     totals = defaultdict(float)

#     prev_y = None

#     # =========================================================
#     # FMCSA RULE TRACKERS
#     # =========================================================

#     total_driving_hours = 0.0
#     total_on_duty_hours = 0.0

#     rolling_8_day_hours = 0.0

#     driving_since_break = 0.0

#     shift_start_time = None

#     consecutive_off_duty = 0.0

#     sleeper_berth_hours = 0.0

#     c.setLineWidth(2.4)

#     # =========================================================
#     # SORT SEGMENTS
#     # =========================================================

#     segments = sorted(
#         segments,
#         key=lambda x: x["start"]
#     )

#     for seg in segments:

#         st = seg["start"]
#         et = seg["end"]

#         status = _normalize_status(
#             seg["status"]
#         )

#         duration_hours = (
#             (et - st).total_seconds() / 3600.0
#         )

#         totals[status] += duration_hours

#         # =====================================================
#         # DUTY TOTALS
#         # =====================================================

#         if status == "driving":

#             total_driving_hours += duration_hours

#             total_on_duty_hours += duration_hours

#             rolling_8_day_hours += duration_hours

#             driving_since_break += duration_hours

#         elif status == "on":

#             total_on_duty_hours += duration_hours

#             rolling_8_day_hours += duration_hours

#         # =====================================================
#         # SHIFT START
#         # =====================================================

#         if (
#             shift_start_time is None
#             and status in ["driving", "on"]
#         ):
#             shift_start_time = st

#         # =====================================================
#         # OFF DUTY / SLEEPER RESET
#         # =====================================================

#         if status in ["off", "sleeper"]:

#             consecutive_off_duty += duration_hours

#             # Sleeper berth tracking
#             if status == "sleeper":
#                 sleeper_berth_hours += duration_hours

#             # 30-minute break reset
#             if consecutive_off_duty >= 0.5:
#                 driving_since_break = 0.0

#             # 34-hour restart reset
#             if consecutive_off_duty >= 34:
#                 rolling_8_day_hours = 0.0
#                 total_on_duty_hours = 0.0

#         else:

#             consecutive_off_duty = 0.0

#         # =====================================================
#         # GRAPH POSITION
#         # =====================================================

#         start_min = (
#             st.hour * 60
#             + st.minute
#         )

#         end_min = (
#             et.hour * 60
#             + et.minute 
#         )

#         x1 = _minute_x(start_min)

#         x2 = _minute_x(end_min)

#         y = _row_center(status)

#         # =====================================================
#         # DEFAULT COLOR
#         # =====================================================

#         stroke_color = STATUS_COLORS[status]

#         # =====================================================
#         # 11-HOUR DRIVING LIMIT
#         # =====================================================

#         if (
#             status == "driving"
#             and total_driving_hours > 11
#         ):

#             stroke_color = HexColor("#dc2626")

#         # =====================================================
#         # 14-HOUR DRIVING WINDOW
#         # =====================================================

#         if (
#             shift_start_time
#             and status == "driving"
#         ):

#             elapsed = (
#                 (et - shift_start_time).total_seconds()
#                 / 3600.0
#             )

#             if elapsed > 14:
#                 stroke_color = HexColor("#b91c1c")

#         # =====================================================
#         # 30-MINUTE BREAK RULE
#         # =====================================================

#         if (
#             status == "driving"
#             and driving_since_break > 8
#         ):

#             stroke_color = HexColor("#ef4444")

#         # =====================================================
#         # 60/70 HOUR RULE
#         # =====================================================

#         if rolling_8_day_hours > 70:

#             stroke_color = HexColor("#7f1d1d")

#         # =====================================================
#         # DRAW GRAPH
#         # =====================================================

#         c.setStrokeColor(stroke_color)

#         if (
#             prev_y is not None
#             and abs(prev_y - y) > 1
#         ):

#             c.line(
#                 x1,
#                 prev_y,
#                 x1,
#                 y
#             )

#         c.line(
#             x1,
#             y,
#             x2,
#             y
#         )

#         prev_y = y

#     # =========================================================
#     # TOTAL HOURS COLUMN
#     # =========================================================

#     cx = GRID_RIGHT + (TOTAL_COL_W / 2)

#     c.setFillColor(black)

#     for i, (_, key) in enumerate(ROW_LABELS):

#         y = (
#             GRID_HEADER_BOTTOM
#             - (ROW_H * (i + 0.5))
#             - 5
#         )

#         c.setFont("Helvetica-Bold", 13)

#         c.drawCentredString(
#             cx,
#             y,
#             _fmt_hours(
#                 totals.get(key, 0)
#             )
#         )

#     total = sum(totals.values())

#     c.setFont("Helvetica", 9)

#     c.drawCentredString(
#         cx,
#         GRID_BOTTOM - 12,
#         f"Σ {_fmt_hours(total)}"
#     )

#     # =========================================================
#     # RULES FOOTER
#     # =========================================================

#     c.setFont("Helvetica", 7)

#     c.setFillColor(
#         HexColor("#334155")
#     )

#     footer = (
#         f"Driving: {_fmt_hours(total_driving_hours)} / 11h   |   "
#         f"On Duty: {_fmt_hours(total_on_duty_hours)} / 70h   |   "
#         f"Rolling 8-Day: {_fmt_hours(rolling_8_day_hours)}   |   "
#         f"Sleeper: {_fmt_hours(sleeper_berth_hours)}"
#     )

#     c.drawCentredString(
#         PAGE_W / 2,
#         GRID_BOTTOM - 28,
#         footer
#     )
# # =============================================================================
# # REMARKS
# # =============================================================================

# def _draw_remarks(c, remarks):

#     col_w = GRID_W / 24.0

#     # =========================================================
#     # VERTICAL LINES
#     # =========================================================

#     c.setStrokeColor(
#         HexColor("#94a3b8")
#     )

#     c.setLineWidth(0.3)

#     for h in range(25):

#         x = GRID_LEFT + (h * col_w)

#         c.line(
#             x,
#             GRID_BOTTOM,
#             x,
#             GRID_BOTTOM - REMARKS_HEIGHT
#         )

#     c.setStrokeColor(black)

#     c.line(
#         GRID_LEFT,
#         GRID_BOTTOM - REMARKS_HEIGHT,
#         GRID_RIGHT,
#         GRID_BOTTOM - REMARKS_HEIGHT
#     )

#     # =========================================================
#     # REMARKS LABEL
#     # =========================================================

#     c.setFont("Helvetica-Bold", 16)

#     c.drawString(
#         MARGIN,
#         GRID_BOTTOM - 20,
#         "Remarks"
#     )

#     # =========================================================
#     # REMARK MARKERS
#     # =========================================================

#     if remarks:

#         c.setFont("Helvetica", 7)

#         for r in remarks:

#             minute = r["minute"]

#             x = _minute_x(minute)

#             c.setStrokeColor(
#                 STATUS_COLORS["on"]
#             )

#             c.setLineWidth(1)

#             c.line(
#                 x,
#                 GRID_BOTTOM,
#                 x,
#                 GRID_BOTTOM - 8
#             )

#             c.saveState()

#             c.translate(
#                 x + 3,
#                 GRID_BOTTOM - 10
#             )

#             c.rotate(-63)

#             txt = (
#                 f"{r['time']} "
#                 f"{r['label']}"
#             )

#             c.drawString(0, 0, txt)

#             c.restoreState()

#     # =========================================================
#     # SHIPPING FIELDS
#     # =========================================================

#     y = GRID_BOTTOM - REMARKS_HEIGHT - 22

#     c.setFont("Helvetica-Bold", 10)

#     fields = [
#         "Shipping Documents:",
#         "DVL or Manifest No.:",
#         "Shipper & Commodity:"
#     ]

#     for field in fields:

#         c.drawString(MARGIN, y, field)

#         c.line(130, y - 2, GRID_RIGHT, y - 2)

#         y -= 18

#     # =========================================================
#     # NOTE
#     # =========================================================

#     c.setFont("Helvetica-Oblique", 8)

#     c.drawCentredString(
#         PAGE_W / 2,
#         y - 4,
#         "Enter name of place you reported and where released from work, and when and where each change of duty occurred."
#     )

#     c.drawCentredString(
#         PAGE_W / 2,
#         y - 16,
#         "Use time standard of home terminal."
#     )

#     return y - 28


# # =============================================================================
# # RECAP
# # =============================================================================

# def _draw_recap(c, top_y, plan_data):

#     box_h = 110

#     y_bottom = top_y - box_h

#     left_x = MARGIN

#     # =========================================================
#     # RECAP BOX
#     # =========================================================

#     c.rect(left_x, y_bottom, 62, box_h)

#     c.setFont("Helvetica-Bold", 10)

#     c.drawString(left_x + 4, top_y - 14, "Recap:")

#     c.setFont("Helvetica", 8)

#     _draw_wrapped(
#         c,
#         "Complete at end of day",
#         left_x + 4,
#         top_y - 28
#     )

#     c.drawString(left_x + 4, y_bottom + 32, "On duty hours")
#     c.drawString(left_x + 4, y_bottom + 20, "today, Total")
#     c.drawString(left_x + 4, y_bottom + 8, "lines 3 & 4")

#     # =========================================================
#     # 70 HOUR
#     # =========================================================

#     sec1_x = left_x + 66
#     sec_w = 218

#     c.rect(sec1_x, y_bottom, sec_w, box_h)

#     c.line(sec1_x, top_y - 24, sec1_x + sec_w, top_y - 24)

#     c.setFont("Helvetica-Bold", 10)

#     c.drawCentredString(
#         sec1_x + (sec_w / 2),
#         top_y - 16,
#         "70 Hour / 8 Day Drivers"
#     )

#     sub_w = sec_w / 3

#     for i in range(1, 3):

#         c.line(
#             sec1_x + (sub_w * i),
#             y_bottom,
#             sec1_x + (sub_w * i),
#             top_y - 24
#         )

#     titles = ["A.", "B.", "C."]

#     descs = [
#         "Total hours on\nduty last 7 days\nincluding today.",
#         "Total hours\navailable\ntomorrow\n70 hr. minus A*.",
#         "Total hours on\nduty last 5 days\nincluding today."
#     ]

#     for i in range(3):

#         x = sec1_x + (sub_w * i) + 6

#         c.setFont("Helvetica-Bold", 10)

#         c.drawString(x, top_y - 40, titles[i])

#         c.setFont("Helvetica", 8)

#         _draw_wrapped(
#             c,
#             descs[i],
#             x,
#             top_y - 54
#         )

#     # =========================================================
#     # 60 HOUR
#     # =========================================================

#     sec2_x = sec1_x + sec_w + 6

#     c.rect(sec2_x, y_bottom, sec_w, box_h)

#     c.line(sec2_x, top_y - 24, sec2_x + sec_w, top_y - 24)

#     c.setFont("Helvetica-Bold", 10)

#     c.drawCentredString(
#         sec2_x + (sec_w / 2),
#         top_y - 16,
#         "60 Day / 7 Day Drivers"
#     )

#     for i in range(1, 3):

#         c.line(
#             sec2_x + (sub_w * i),
#             y_bottom,
#             sec2_x + (sub_w * i),
#             top_y - 24
#         )

#     descs2 = [
#         "Total hours on\nduty last 8 days\nincluding today.",
#         "Total hours\navailable\ntomorrow\n60 hr. minus A*.",
#         "Total hours on\nduty last 7 days\nincluding today."
#     ]

#     for i in range(3):

#         x = sec2_x + (sub_w * i) + 6

#         c.setFont("Helvetica-Bold", 10)

#         c.drawString(x, top_y - 40, titles[i])

#         c.setFont("Helvetica", 8)

#         _draw_wrapped(
#             c,
#             descs2[i],
#             x,
#             top_y - 54
#         )

#     # =========================================================
#     # SIDE NOTE
#     # =========================================================

#     note_x = sec2_x + sec_w + 6
#     note_w = PAGE_W - MARGIN - note_x

#     c.rect(note_x, y_bottom, note_w, box_h)

#     c.setFont("Helvetica-Bold", 8)

#     c.drawString(note_x + 4, top_y - 16, "*If you took")

#     c.setFont("Helvetica", 8)

#     _draw_wrapped(
#         c,
#         "34 consecutive\nhours off duty\nyou have 60/70\nhours\navailable",
#         note_x + 4,
#         top_y - 30
#     )

#     # =========================================================
#     # SUMMARY
#     # =========================================================

#     c.setFont("Helvetica", 9)

#     miles = int(plan_data.get("total_distance_miles", 0))

#     summary = (
#         f"Trip plan: {len(plan_data.get('eld_logs', []))}-segment trip, "
#         f"{miles} mi."
#     )

#     c.drawString(
#         MARGIN,
#         y_bottom - 18,
#         summary
#     )
# def build_log_pdf(plan_data):

#     buf = io.BytesIO()

#     c = canvas.Canvas(
#         buf,
#         pagesize=letter
#     )

#     eld_logs = plan_data.get("eld_logs", [])

#     if not eld_logs:

#         c.setFont("Helvetica", 18)

#         c.drawString(
#             100,
#             700,
#             "No ELD logs found"
#         )

#         c.save()

#         pdf = buf.getvalue()

#         buf.close()

#         return pdf

#     # =========================================================
#     # SPLIT LOGS BY DAY
#     # =========================================================

#     pages = defaultdict(list)

#     for seg in eld_logs:

#         st = _parse_iso(seg.get("start_time"))
#         et = _parse_iso(seg.get("end_time"))

#         if not st or not et:
#             continue

#         if st.tzinfo is None:
#             st = st.replace(tzinfo=timezone.utc)

#         if et.tzinfo is None:
#             et = et.replace(tzinfo=timezone.utc)

#         cursor = st

#         while cursor < et:

#             day_start = datetime(
#                 cursor.year,
#                 cursor.month,
#                 cursor.day,
#                 tzinfo=timezone.utc
#             )

#             next_day = day_start + timedelta(days=1)

#             seg_end = min(et, next_day)

#             key = day_start.date().isoformat()

#             pages[key].append({
#                 "start": cursor,
#                 "end": seg_end,
#                 "status": seg.get("status", "Off Duty"),
#                 "remark": seg.get("remark", "")
#             })

#             cursor = seg_end

#     sorted_days = sorted(pages.keys())

#     # =========================================================
#     # PAGE LOOP
#     # =========================================================

#     for idx, day in enumerate(sorted_days, start=1):

#         segments = pages[day]

#         day_dt = datetime.fromisoformat(day)

#         # =====================================================
#         # HEADER
#         # =====================================================

#         _draw_header(
#             c,
#             day_dt,
#             idx,
#             len(sorted_days),
#             plan_data
#         )
        

#         # =====================================================
#         # GRID
#         # =====================================================

#         _draw_grid(c)

#         # =====================================================
#         # DUTY GRAPH
#         # =====================================================

#         _draw_duty_graph(
#             c,
#             segments
#         )

#         # =====================================================
#         # REMARKS
#         # =====================================================

#         remarks = []

#         for seg in segments:

#             if seg.get("remark"):

#                 st = seg["start"]

#                 minute = (
#                     st.hour * 60
#                     + st.minute
#                 )

#                 remarks.append({
#                     "minute": minute,
#                     "time": st.strftime("%I:%M %p"),
#                     "label": seg["remark"]
#                 })

#         next_y = _draw_remarks(
#             c,
#             remarks
#         )

#         # =====================================================
#         # RECAP
#         # =====================================================

#         _draw_recap(
#             c,
#             next_y,
#             plan_data
#         )

#         c.showPage()

#     c.save()

#     pdf = buf.getvalue()

#     buf.close()

#     return pdf


# def generate_logs_pdf(plan_data):
#     return build_log_pdf(plan_data)
# ...existing code...
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

    miles = int(plan_data.get("total_distance_miles", 0))
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
# DUTY GRAPH - with rule enforcement
# =============================================================================

def _draw_duty_graph(c, segments):
    if not segments:
        return

    # segments are datetimes within same calendar day
    segments = sorted(segments, key=lambda x: x["start"])

    totals = defaultdict(float)   # totals by status (hours)
    total_driving_hours = 0.0     # cumulative driving hours in day
    driving_since_break = 0.0     # continuous driving since last 30+ min off/sleeper
    shift_start_time = None       # first time status is "driving" or "on"
    prev_y = None

    c.setLineWidth(2.2)

    def draw_rect(start_dt, end_dt, status_key, color):
        start_min = start_dt.hour * 60 + start_dt.minute + start_dt.second / 60.0
        end_min = end_dt.hour * 60 + end_dt.minute + end_dt.second / 60.0
        x1 = _minute_x(start_min)
        x2 = _minute_x(end_min)
        rect_w = max(1.0, x2 - x1)
        rect_y = _row_center(status_key) - (ROW_H / 4)
        rect_h = ROW_H / 2
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.roundRect(x1, rect_y, rect_w, rect_h, 3, stroke=0, fill=1)
        return x1, x2, rect_y + rect_h / 2  # center y used for vertical jumps

    for seg in segments:
        st: datetime = seg["start"]
        et: datetime = seg["end"]
        status = _normalize_status(seg.get("status", "off"))
        duration_h = (et - st).total_seconds() / 3600.0
        totals[status] += duration_h

        # establish shift start when first on/driving
        if shift_start_time is None and status in ("driving", "on"):
            shift_start_time = st

        # if status is off/sleeper then update driving_since_break and continue
        if status in ("off", "sleeper"):
            # increase continuous off time so we can reset driving_since_break when >=0.5
            # treat the whole off/sleeper segment as break
            driving_since_break = 0.0
            # draw off/sleeper block using default colors
            color = STATUS_COLORS.get(status, HexColor("#444444"))
            center_y = _row_center(status)
            # draw a filled narrow band for off/sleeper segments
            draw_rect(st, et, status, color)
            # vertical jump at transition
            if prev_y is not None and abs(prev_y - center_y) > 1:
                x_jump = _minute_x(st.hour * 60 + st.minute + st.second / 60.0)
                c.setStrokeColor(black)
                c.line(x_jump, prev_y, x_jump, center_y)
                prev_y = center_y
            else:
                prev_y = center_y
            continue

        # status is driving or on (non-driving on-duty)
        # We only enforce driving rules for "driving" rows; "on" is counted to shift and totals
        # We'll draw "on" segments in their color and they interrupt driving_since_break (they are not breaks)
        if status == "on":
            color = STATUS_COLORS.get("on")
            center_y = _row_center("on")
            draw_rect(st, et, "on", color)
            if prev_y is not None and abs(prev_y - center_y) > 1:
                x_jump = _minute_x(st.hour * 60 + st.minute + st.second / 60.0)
                c.line(x_jump, prev_y, x_jump, center_y)
            prev_y = center_y
            # non-driving on-duty does NOT reset driving_since_break; it continues
            driving_since_break += duration_h if status == "driving" else 0.0
            continue

        # at this point status == "driving"
        ptr = st
        remaining = (et - st).total_seconds()
        # convert thresholds to absolute datetimes
        # 8h continuous driving threshold (from current driving_since_break)
        if driving_since_break < 8.0:
            secs_until_8h = max(0.0, (8.0 - driving_since_break) * 3600.0)
            thresh_8h = ptr + timedelta(seconds=secs_until_8h) if secs_until_8h > 0 else ptr
        else:
            thresh_8h = ptr  # already in violation

        # 11h total driving threshold
        if total_driving_hours < 11.0:
            secs_until_11_total = max(0.0, (11.0 - total_driving_hours) * 3600.0)
            thresh_11_total = ptr + timedelta(seconds=secs_until_11_total) if secs_until_11_total > 0 else ptr
        else:
            thresh_11_total = ptr  # already in violation

        # 11h shift span threshold (from shift_start_time)
        if shift_start_time is not None:
            secs_until_shift_11 = max(0.0, (11.0 - ((ptr - shift_start_time).total_seconds() / 3600.0)) * 3600.0)
            thresh_shift = ptr + timedelta(seconds=secs_until_shift_11) if secs_until_shift_11 > 0 else ptr
        else:
            thresh_shift = None

        # draw loop: continue splitting the segment until fully drawn
        while ptr < et:
            # compute next threshold time (earliest that causes violation)
            candidates = []
            if thresh_8h is not None and thresh_8h > ptr:
                candidates.append(thresh_8h)
            if thresh_11_total is not None and thresh_11_total > ptr:
                candidates.append(thresh_11_total)
            if thresh_shift is not None and thresh_shift > ptr:
                candidates.append(thresh_shift)
            # take earliest candidate within segment
            next_thresh = min(candidates) if candidates else None
            part_end = min(et, next_thresh) if next_thresh is not None else et

            # Determine color for this part:
            # - normal driving color if none of the three violations have been reached yet
            # - if driving_since_break already >=8 at ptr -> 8h violation
            # - if total_driving_hours >=11 at ptr -> total 11h violation
            # - if shift exceeded at ptr -> shift violation
            # Priority for display: total_11 > shift > continuous_8 (choose darkest for total)
            part_in_violation = False
            part_color = STATUS_COLORS["driving"]
            # check conditions at start ptr
            if driving_since_break >= 8.0:
                part_in_violation = True
                part_color = VIOLATION_8H
            if total_driving_hours >= 11.0:
                part_in_violation = True
                part_color = VIOLATION_11H
            if shift_start_time is not None and ((ptr - shift_start_time).total_seconds() / 3600.0) >= 11.0:
                part_in_violation = True
                # use shift color if more severe than 8h but less severe than total; choose VIOLATION_SHIFT
                part_color = VIOLATION_SHIFT

            # draw this part
            draw_rect(ptr, part_end, "driving", part_color)

            # vertical jump handling
            center_y = _row_center("driving")
            if prev_y is not None and abs(prev_y - center_y) > 1:
                x_jump = _minute_x(ptr.hour * 60 + ptr.minute + ptr.second / 60.0)
                c.setStrokeColor(black)
                c.line(x_jump, prev_y, x_jump, center_y)
            prev_y = center_y

            # advance counters by this part duration
            part_secs = (part_end - ptr).total_seconds()
            part_hours = part_secs / 3600.0
            total_driving_hours += part_hours
            driving_since_break += part_hours

            # update pointer
            ptr = part_end

            # if we hit a threshold exactly, mark that threshold as crossed (so next loop will treat as violation)
            # recompute thresholds relative to new ptr
            if driving_since_break < 8.0:
                secs_until_8h = max(0.0, (8.0 - driving_since_break) * 3600.0)
                thresh_8h = ptr + timedelta(seconds=secs_until_8h) if secs_until_8h > 0 else ptr
            else:
                thresh_8h = ptr

            if total_driving_hours < 11.0:
                secs_until_11_total = max(0.0, (11.0 - total_driving_hours) * 3600.0)
                thresh_11_total = ptr + timedelta(seconds=secs_until_11_total) if secs_until_11_total > 0 else ptr
            else:
                thresh_11_total = ptr

            if shift_start_time is not None:
                secs_until_shift_11 = max(0.0, (11.0 - ((ptr - shift_start_time).total_seconds() / 3600.0)) * 3600.0)
                thresh_shift = ptr + timedelta(seconds=secs_until_shift_11) if secs_until_shift_11 > 0 else ptr
            else:
                thresh_shift = None

        # after finishing driving segment, it remains continuous unless an off/sleeper segment comes later
        # (do not reset driving_since_break here)

    # draw totals column
    cx = GRID_RIGHT + (TOTAL_COL_W / 2)
    c.setFillColor(black)
    for i, (_, key) in enumerate(ROW_LABELS):
        y = GRID_HEADER_BOTTOM - (ROW_H * (i + 0.5)) - 5
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(cx, y, _fmt_hours(totals.get(key, 0)))
    total = sum(totals.values())
    c.setFont("Helvetica", 9)
    c.drawCentredString(cx, GRID_BOTTOM - 12, f"Σ {_fmt_hours(total)}")

    # rules summary footer
    c.setFont("Helvetica", 7)
    c.setFillColor(HexColor("#334155"))
    footer = (
        f"Driving today: {_fmt_hours(total_driving_hours)} / 11h   |   "
        f"Continuous driving since break: {_fmt_hours(driving_since_break)} / 8h   |   "
        f"Shift start: {shift_start_time.strftime('%H:%M') if shift_start_time else 'N/A'}"
    )
    c.drawCentredString(PAGE_W / 2, GRID_BOTTOM - 28, footer)


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
        c.setFont("Helvetica", 7)
        for r in remarks:
            minute = r["minute"]
            x = _minute_x(minute)
            c.setStrokeColor(STATUS_COLORS["on"])
            c.setLineWidth(1)
            c.line(x, GRID_BOTTOM, x, GRID_BOTTOM - 8)
            c.saveState()
            c.translate(x + 3, GRID_BOTTOM - 10)
            c.rotate(-63)
            txt = f"{r['time']} {r['label']}"
            c.drawString(0, 0, txt)
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
                "remark": seg.get("remark", "")
            })
            cursor = seg_end

    sorted_days = sorted(pages.keys())
    for idx, day in enumerate(sorted_days, start=1):
        segments = pages[day]
        day_dt = datetime.fromisoformat(day)
        _draw_header(c, day_dt, idx, len(sorted_days), plan_data)
        _draw_grid(c)
        _draw_duty_graph(c, segments)

        # remarks
        remarks = []
        for seg in segments:
            if seg.get("remark"):
                st = seg["start"]
                minute = st.hour * 60 + st.minute
                remarks.append({
                    "minute": minute,
                    "time": st.strftime("%I:%M %p"),
                    "label": seg["remark"]
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