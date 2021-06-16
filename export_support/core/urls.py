from django.urls import path

from export_support.core import views

app_name = "core"
urlpatterns = [
    path("", views.EnquirySubjectFormView.as_view(), name="index"),
    path(
        "import-enquiries", views.ImportEnquiriesView.as_view(), name="import-enquiries"
    ),
    path(
        "export-destination",
        views.ExportDestinationFormView.as_view(),
        name="export-destination",
    ),
    path(
        "non-eu-export-enquiries",
        views.NonEUExportEnquiriesView.as_view(),
        name="non-eu-export-enquiries",
    ),
]
