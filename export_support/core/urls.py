from django.urls import path

from export_support.core import views

app_name = "core"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("enquiry", views.EnquiryWizardView.as_view(), name="enquiry-wizard"),
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
    path(
        "enquiry-contact",
        views.EnquiryContactView.as_view(),
        name="enquiry-contact",
    ),
    path(
        "enquiry-contact-success",
        views.EnquiryContactSuccessView.as_view(),
        name="enquiry-contact-success",
    ),
    # Only necessary for user testing
    path(
        "start",
        views.StartPageRedirectView.as_view(),
        name="start-page-redirect",
    ),
]
