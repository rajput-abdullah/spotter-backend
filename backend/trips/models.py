import uuid
from django.db import models

class Trip(models.Model):
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    distance_miles = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    driver_name = models.CharField(max_length=255)
    vehicle_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.driver_name} - {self.start_location} to {self.end_location}"

class ELDLog(models.Model):
    trip = models.ForeignKey(Trip, related_name='eld_logs', on_delete=models.CASCADE)
    log_time = models.DateTimeField()
    status = models.CharField(max_length=50)  # e.g., 'Driving', 'On Duty', 'Off Duty'
    duration_hours = models.FloatField()

    def __str__(self):
        return f"Log for {self.trip.driver_name} at {self.log_time} - Status: {self.status}"

# New: Plan model to store incoming plan requests + computed plan
class Plan(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    input_data = models.JSONField()
    plan_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plan {self.uuid}"