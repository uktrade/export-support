from csp.decorators import csp_exempt
from django.urls import path

from . import views

app_name = "healthcheck"

urlpatterns = [
    path(
        "companies-house/",
        csp_exempt(views.CompaniesHouseHealthCheckView.as_view()),
        name="companies-house",
    ),
    path(
        "directory-forms/",
        csp_exempt(views.DirectoryFormsHealthCheckView.as_view()),
        name="directory-forms",
    ),
]
