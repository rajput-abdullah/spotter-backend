from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# project-level urls.py already does path('trips/', include('trips.urls')),
# so register an empty prefix here to expose /trips/ and /trips/{pk}/
router.register(r'', views.TripViewSet, basename='trip')

urlpatterns = [
    path('', include(router.urls)),
    path("", views.HealthCheck.as_view(), name="health"),
    path("plan-trip/", views.PlanTripView.as_view(), name="plan-trip"),
    path("plan-trip/<uuid:uuid>/", views.PlanTripView.as_view(), name="plan-trip-get"),
    path("plan-trip/<uuid:uuid>/logs.pdf", views.PlanLogsPdfView.as_view(), name="plan-trip-logs-pdf"),
]