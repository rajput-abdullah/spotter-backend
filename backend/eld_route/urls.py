from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("trips.urls")),   # existing API mount
    path("", include("trips.urls")),       # <-- add this so /plan-trip/ is available
    path("eld/", include("eld.urls")),
]