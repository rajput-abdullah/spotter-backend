from django.urls import path
from .views import EldView

urlpatterns = [
    path('eld/', EldView.as_view(), name='eld'),
]