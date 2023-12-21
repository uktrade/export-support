from django.urls import path, re_path

from export_support.core import views

app_name = "core"

enquiry_wizard_view = views.EnquiryWizardView.as_view(
    url_name="core:enquiry-wizard-step",
)

ru_emergency_situation_wizard_view = views.EmergencySituationEnquiryWizardView.as_view(
    url_name="core:ru-emergency-situation-wizard-step",
)
ip_emergency_situation_wizard_view = views.EmergencySituationEnquiryWizardView.as_view(
    url_name="core:ip-emergency-situation-wizard-step",
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
        r"^russia-ukraine/(?P<step>.+)$",
        ru_emergency_situation_wizard_view,
        name="ru-emergency-situation-wizard-step",
    ),
    re_path(
        r"^israel-palestine/(?P<step>.+)$",
        ip_emergency_situation_wizard_view,
        name="ip-emergency-situation-wizard-step",
    ),
    path(
        "not-listed-market-export-enquiries",
        views.NotListedMarketExportEnquiriesView.as_view(),
        name="not-listed-market-export-enquiries",
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
