from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.views import APIView

from .models import Trip, Plan
from .serializers import TripSerializer, PlanInputSerializer, PlanSerializer
from eld.services import ELDService
from .planner import plan_trip
from .pdf import generate_logs_pdf


class TripViewSet(viewsets.ViewSet):

    def create(self, request):
        serializer = TripSerializer(data=request.data)

        if serializer.is_valid():
            trip = serializer.save()

            # Use serializer to serialize the saved instance
            response_data = TripSerializer(trip).data

            # Build trip_details for ELDService robustly:
            # prefer original request values (e.g. distance, driving_time, rest_time)
            # fall back to saved model fields where appropriate.
            # If incoming distance is in kilometers and the model stores miles, convert back.
            req = request.data or {}
            # get distance: prefer request.distance, else derive from distance_miles
            distance = req.get("distance")
            if distance is None and response_data.get("distance_miles") is not None:
                try:
                    # convert miles back to km
                    distance = round(float(response_data["distance_miles"]) / 0.621371, 2)
                except Exception:
                    distance = None

            driving_time = req.get("driving_time")
            rest_time = req.get("rest_time")

            trip_details = {
                "start_location": response_data.get("start_location"),
                "end_location": response_data.get("end_location"),
                "distance": distance,
                "driving_time": driving_time,
                "rest_time": rest_time,
                "driver_name": response_data.get("driver_name"),
                "vehicle_id": response_data.get("vehicle_id"),
                "start_time": response_data.get("start_time"),
                "end_time": response_data.get("end_time"),
            }

            eld_service = ELDService(trip_details)
            result = eld_service.process_trip()

            return Response({
                "trip": response_data,
                "route_instructions": result.get("route_instructions"),
                "eld_logs": result.get("eld_logs")
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HealthCheck(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok"})


class PlanTripView(APIView):
    """
    POST /api/plan-trip/ -> validate input, run planner, persist plan, return JSON
    """
    def post(self, request):
        serializer = PlanInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        input_data = serializer.validated_data
        plan_result = plan_trip(input_data)

        plan = Plan.objects.create(input_data=input_data, plan_data=plan_result)
        out = PlanSerializer(plan).data
        out["route_instructions"] = plan_result.get("route_instructions")
        out["eld_logs"] = plan_result.get("eld_logs")
        return Response(out, status=status.HTTP_201_CREATED)

    def get(self, request, uuid=None):
        if uuid is None:
            return Response({"detail": "UUID required"}, status=status.HTTP_400_BAD_REQUEST)
        plan = get_object_or_404(Plan, uuid=uuid)
        out = PlanSerializer(plan).data
        out["route_instructions"] = plan.plan_data.get("route_instructions")
        out["eld_logs"] = plan.plan_data.get("eld_logs")
        return Response(out)


class PlanLogsPdfView(APIView):
    def get(self, request, uuid):
        plan = get_object_or_404(Plan, uuid=uuid)
        pdf_bytes = generate_logs_pdf(plan.plan_data or {})
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'inline; filename="logs-{uuid}.pdf"'
        return resp