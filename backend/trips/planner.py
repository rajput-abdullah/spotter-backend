from datetime import timedelta
from typing import Dict, Any, List
from django.utils import timezone


def plan_trip(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure-Python HOS planner. Input follows the spec:
    - total_distance_miles
    - total_drive_minutes
    - current_cycle_used_hrs
    Returns route_instructions and eld_logs (list of segments).
    """
    total_distance = float(input_data.get("total_distance_miles", 0))
    total_drive_minutes = int(input_data.get("total_drive_minutes", 0))
    current_cycle_used_hrs = float(input_data.get("current_cycle_used_hrs", 0))

    # route instructions
    route_instructions = {
        "start_location": input_data.get("pickup_location") or input_data.get("current_location"),
        "end_location": input_data.get("dropoff_location"),
        "distance": total_distance,
        "estimated_time": str(timedelta(minutes=total_drive_minutes)),
        "route": f"Route from {input_data.get('pickup_location')} to {input_data.get('dropoff_location')}",
        "fuel_stops": []
    }

    # fuel stops every 1000 miles (at 1000, 2000, ... less than distance)
    if total_distance > 1000:
        stops = []
        marker = 1000
        while marker < total_distance:
            stops.append({"mile_marker": marker})
            marker += 1000
        route_instructions["fuel_stops"] = stops

    # HOS rules (reasonable defaults)
    MAX_DAY_DRIVE_MIN = 11 * 60            # 11 hours/day
    CONTINUOUS_LIMIT_MIN = 8 * 60          # 8 hours continuous then break
    MANDATORY_BREAK_MIN = 30               # 30-minute break
    OFF_DUTY_RESET_MIN = 10 * 60           # 10-hour off-duty reset

    remaining = total_drive_minutes
    now = timezone.now()
    cursor = now
    eld_logs: List[Dict[str, Any]] = []

    # If driver already used >=10 hours in cycle, require 10-hr reset first
    if current_cycle_used_hrs >= 10:
        eld_logs.append({
            "start_time": cursor.isoformat(),
            "end_time": (cursor + timedelta(minutes=OFF_DUTY_RESET_MIN)).isoformat(),
            "status": "Off Duty (10-hr reset)"
        })
        cursor += timedelta(minutes=OFF_DUTY_RESET_MIN)

    # Simulate day-by-day driving
    while remaining > 0:
        # daily allowance
        today_allow = MAX_DAY_DRIVE_MIN

        # drive blocks for this day (we will consume up to today_allow)
        day_driving = min(remaining, today_allow)
        driven = 0

        while driven < day_driving:
            # remaining continuous allowance in this block
            cont_allow = min(CONTINUOUS_LIMIT_MIN, day_driving - driven)
            if cont_allow <= 0:
                break

            # drive cont_allow minutes (or the remainder if smaller)
            start = cursor
            end = cursor + timedelta(minutes=cont_allow)
            eld_logs.append({
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "status": "Driving"
            })
            cursor = end
            driven += cont_allow
            remaining -= cont_allow

            # if we still need to drive this day and we've hit the continuous limit, add mandatory break
            if driven < day_driving and cont_allow >= CONTINUOUS_LIMIT_MIN:
                eld_logs.append({
                    "start_time": cursor.isoformat(),
                    "end_time": (cursor + timedelta(minutes=MANDATORY_BREAK_MIN)).isoformat(),
                    "status": "Rest"
                })
                cursor += timedelta(minutes=MANDATORY_BREAK_MIN)

        # if there is still remaining after the day, add a 10-hour off-duty reset (end of day)
        if remaining > 0:
            eld_logs.append({
                "start_time": cursor.isoformat(),
                "end_time": (cursor + timedelta(minutes=OFF_DUTY_RESET_MIN)).isoformat(),
                "status": "Off Duty (10-hr reset)"
            })
            cursor += timedelta(minutes=OFF_DUTY_RESET_MIN)

    return {
        "route_instructions": route_instructions,
        "eld_logs": eld_logs
    }