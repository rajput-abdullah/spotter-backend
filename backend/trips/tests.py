from django.test import TestCase
from django.urls import reverse
from .planner import plan_trip
from rest_framework.test import APIClient
from .models import Plan
import uuid
from django.utils import timezone
from datetime import timedelta


class PlannerUnitTests(TestCase):

    def test_short_trip_no_breaks(self):
        inp = {
            "current_cycle_used_hrs": 0,
            "total_distance_miles": 50,
            "total_drive_minutes": 60
        }
        out = plan_trip(inp)
        self.assertIn("route_instructions", out)
        self.assertEqual(out["route_instructions"]["distance"], 50)
        # single driving segment of ~60 minutes
        self.assertTrue(any(seg["status"] == "Driving" for seg in out["eld_logs"]))

    def test_long_trip_fuel_stops(self):
        inp = {
            "current_cycle_used_hrs": 0,
            "total_distance_miles": 2100,
            "total_drive_minutes": 1800  # 30 hours
        }
        out = plan_trip(inp)
        # fuel stops at 1000 and 2000
        stops = out["route_instructions"].get("fuel_stops", [])
        markers = [s["mile_marker"] for s in stops]
        self.assertIn(1000, markers)
        self.assertIn(2000, markers)
        # should produce Off Duty resets between days
        self.assertTrue(any("Off Duty" in seg["status"] for seg in out["eld_logs"]))

    def test_off_duty_before_start_if_cycle_used(self):
        inp = {
            "current_cycle_used_hrs": 12,
            "total_distance_miles": 100,
            "total_drive_minutes": 120
        }
        out = plan_trip(inp)
        # first segment should be Off Duty reset
        self.assertTrue(out["eld_logs"][0]["status"].startswith("Off Duty"))


class PlanApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_plan_trip_post_and_get_and_pdf(self):
        url = reverse("plan-trip")
        body = {
            "current_location": "A",
            "pickup_location": "A",
            "pickup_lat": 0.0,
            "pickup_lng": 0.0,
            "dropoff_location": "B",
            "dropoff_lat": 0.0,
            "dropoff_lng": 0.0,
            "current_cycle_used_hrs": 0,
            "total_distance_miles": 1200,
            "total_drive_minutes": 1800
        }
        resp = self.client.post(url, body, format="json")
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn("uuid", data)
        plan_uuid = data["uuid"]

        # GET saved plan
        get_url = reverse("plan-trip-get", kwargs={"uuid": plan_uuid})
        get_resp = self.client.get(get_url)
        self.assertEqual(get_resp.status_code, 200)
        self.assertIn("route_instructions", get_resp.json())

        # GET PDF
        pdf_url = reverse("plan-trip-logs-pdf", kwargs={"uuid": plan_uuid})
        pdf_resp = self.client.get(pdf_url)
        self.assertEqual(pdf_resp.status_code, 200)
        self.assertEqual(pdf_resp["Content-Type"], "application/pdf")