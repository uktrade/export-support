from django.urls import path, re_path

from export_support.core import views

app_name = "core"

enquiry_wizard_view = views.EnquiryWizardView.as_view(
    url_name="core:enquiry-wizard-step",
)

short_enquiry_wizard_view = views.ShortEnquiryWizardView.as_view(
    url_name="core:short-enquiry-wizard-step",
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
    re_path(
        r"^enquiry-short/(?P<step>.+)$",
        short_enquiry_wizard_view,
        name="short-enquiry-wizard-step",
    ),
    path(
        "enquiry-short",
        short_enquiry_wizard_view,
        name="enquiry-wizard-short",
    ),
    path(
        "non-eu-export-enquiries",
        views.NonEUExportEnquiriesView.as_view(),
        name="non-eu-export-enquiries",
    ),
    path(
        "privacy",
        views.PrivacyView.as_view(),
        name="privacy",
    ),
    path(
        "legal-disclaimer",
        views.LegalDisclaimer.as_view(),
        name="legal-disclaimer",
    ),
    path(
        "accessibility-statement",
        views.AccessibilityStatement.as_view(),
        name="accessibility-statement",
    ),
]
