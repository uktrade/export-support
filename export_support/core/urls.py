from django.urls import path

from export_support.core import views

app_name = "core"
urlpatterns = [
    path("", views.EnquiryWizardView.as_view(), name="wizard"),
    path(
        "import-enquiries", views.ImportEnquiriesView.as_view(), name="import-enquiries"
    ),
    path(
        "eu-export-enquiries",
        views.EUExportEnquiriesView.as_view(),
        name="eu-export-enquiries",
    ),
    path(
        "non-eu-export-enquiries",
        views.NonEUExportEnquiriesView.as_view(),
        name="non-eu-export-enquiries",
    ),
]
