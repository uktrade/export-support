from django.urls import path, re_path

from export_support.core import views

app_name = "core"

enquiry_wizard_view = views.EnquiryWizardView.as_view(
    url_name="core:enquiry-wizard-step",
)

russia_ukraine_wizard_view = views.RussiaUkraineEnquiryWizardView.as_view(
    url_name="core:russia-ukraine-wizard-step",
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
        r"^russia-ukraine-enquiry/(?P<step>.+)$",
        russia_ukraine_wizard_view,
        name="russia-ukraine-wizard-step",
    ),
    path(
        "russia-ukraine-enquiry",
        russia_ukraine_wizard_view,
        name="russia-ukraine-enquiry-wizard",
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
