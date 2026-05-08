from django.test import TestCase
from trips.models import Trip
from eld.services import calculate_eld_logs

class EldLogicTests(TestCase):

    def setUp(self):
        # Set up initial trip data for testing
        self.trip = Trip.objects.create(
            start_location="Location A",
            end_location="Location B",
            start_time="2023-10-01T08:00:00Z",
            end_time="2023-10-01T18:00:00Z",
            driver_id="driver_123",
            vehicle_id="vehicle_456"
        )

    def test_calculate_eld_logs(self):
        # Test ELD log calculation based on trip details
        logs = calculate_eld_logs(self.trip)
        self.assertIsNotNone(logs)
        self.assertGreater(len(logs), 0)

    def test_hours_of_service_compliance(self):
        # Test compliance with Hours of Service regulations
        logs = calculate_eld_logs(self.trip)
        total_drive_time = sum(log['drive_time'] for log in logs)
        total_rest_time = sum(log['rest_time'] for log in logs)

        # Assuming HOS regulations allow 11 hours of driving and 10 hours of rest
        self.assertLessEqual(total_drive_time, 11 * 60)  # in minutes
        self.assertGreaterEqual(total_rest_time, 10 * 60)  # in minutes

    def tearDown(self):
        # Clean up after tests
        self.trip.delete()