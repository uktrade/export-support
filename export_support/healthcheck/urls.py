from django.urls import path

from . import views

app_name = "healthcheck"

urlpatterns = [
    path("", views.HealthCheckView.as_view(), name="healthcheck"),
]
