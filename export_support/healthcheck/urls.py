from csp.decorators import csp_exempt
from django.urls import path

from . import views

app_name = "healthcheck"

urlpatterns = [
    path("", csp_exempt(views.HealthCheckView.as_view()), name="healthcheck"),
]
