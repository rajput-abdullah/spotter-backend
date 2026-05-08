from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Trip, Plan
from uuid import UUID

class TripSerializer(serializers.ModelSerializer):
    # accept optional write-only 'distance' (miles) from clients
    distance = serializers.FloatField(write_only=True, required=False)
    driving_time = serializers.FloatField(write_only=True, required=False)
    rest_time = serializers.FloatField(write_only=True, required=False)

    class Meta:
        model = Trip
        fields = "__all__"
        extra_kwargs = {
            "distance_miles": {"required": False},
            "start_time": {"required": False},
            "end_time": {"required": False},
            "driver_name": {"required": False, "allow_blank": True},
            "vehicle_id": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        # If client provided 'distance' (miles), persist to distance_miles
        distance_input = validated_data.pop("distance", None)
        if distance_input is not None:
            validated_data["distance_miles"] = float(distance_input)

        # driving_time (hours) -> compute end_time
        driving_time = validated_data.pop("driving_time", None)
        # rest_time left as meta (not saved) unless model has it (model doesn't)
        validated_data.pop("rest_time", None)

        # set start_time if missing
        if not validated_data.get("start_time"):
            validated_data["start_time"] = timezone.now()

        # compute end_time from start_time + driving_time (if provided)
        if driving_time is not None:
            try:
                driving_hours = float(driving_time)
                validated_data["end_time"] = validated_data["start_time"] + timedelta(hours=driving_hours)
            except Exception:
                # fallback to same as start
                validated_data["end_time"] = validated_data["start_time"]

        # provide defaults for driver_name / vehicle_id from context request if available
        request_obj = self.context.get("request") if hasattr(self, "context") else None
        if not validated_data.get("driver_name"):
            if request_obj:
                validated_data["driver_name"] = request_obj.data.get("driver_name") or ""
            else:
                validated_data["driver_name"] = ""

        if not validated_data.get("vehicle_id"):
            if request_obj:
                validated_data["vehicle_id"] = request_obj.data.get("vehicle_id") or ""
            else:
                validated_data["vehicle_id"] = ""

        return super().create(validated_data)


class PlanInputSerializer(serializers.Serializer):
    current_location = serializers.CharField()
    pickup_location = serializers.CharField()
    pickup_lat = serializers.FloatField(required=False, allow_null=True)
    pickup_lng = serializers.FloatField(required=False, allow_null=True)
    dropoff_location = serializers.CharField()
    dropoff_lat = serializers.FloatField(required=False, allow_null=True)
    dropoff_lng = serializers.FloatField(required=False, allow_null=True)
    current_cycle_used_hrs = serializers.FloatField()
    total_distance_miles = serializers.FloatField()
    total_drive_minutes = serializers.IntegerField()


class PlanSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = Plan
        fields = ["uuid", "input_data", "plan_data", "created_at"]
        read_only_fields = ["uuid", "plan_data", "created_at"]
