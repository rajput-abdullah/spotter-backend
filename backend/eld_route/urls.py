from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.views import APIView


class RootHealthCheck(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, _request):
        return Response({"status": "ok", "service": "spotter-backend"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("trips.urls")),   # all API endpoints at /api/…
    path("eld/", include("eld.urls")),
    path("", RootHealthCheck.as_view(), name="root-health"),  # Render health probe
]