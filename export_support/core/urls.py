from django.urls import path, re_path

from export_support.core import views

app_name = "core"

enquiry_wizard_view = views.EnquiryWizardView.as_view(
    url_name="core:enquiry-wizard-step",
)

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    re_path(
        r"^enquiry/(?P<step>.+)$",
        enquiry_wizard_view,
        name="enquiry-wizard-step",
    ),
    path(
        "enquiry",
        enquiry_wizard_view,
        name="enquiry-wizard",
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
