from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView
from formtools.wizard.views import SessionWizardView

from .forms import (
    EnquirySubjectChoices,
    EnquirySubjectForm,
    ExportDestinationChoices,
    ExportDestinationForm,
)


def should_display_export_destination_form(wizard):
    enquiry_subject_cleaned_data = wizard.get_cleaned_data_for_step("enquiry_subject")
    if not enquiry_subject_cleaned_data:
        return True

    enquiry_subject_value = enquiry_subject_cleaned_data["enquiry_subject"]
    only_importing = enquiry_subject_value == [
        EnquirySubjectChoices.IMPORTING_GOODS_TO_THE_UK
    ]
    return not only_importing


class EnquiryWizardView(SessionWizardView):
    form_list = [
        ("enquiry_subject", EnquirySubjectForm),
        ("export_destination", ExportDestinationForm),
    ]
    condition_dict = {
        "export_destination": should_display_export_destination_form,
    }

    def get_template_names(self):
        templates = {
            form_name: f"core/{form_name}_wizard_step.html"
            for form_name in self.form_list
        }

        return [templates[self.steps.current]]

    def done(self, form_list, form_dict):
        enquiry_subject_form = form_dict["enquiry_subject"]
        enquiry_subject_value = enquiry_subject_form.cleaned_data["enquiry_subject"]

        only_importing = enquiry_subject_value == [
            EnquirySubjectChoices.IMPORTING_GOODS_TO_THE_UK
        ]
        if only_importing:
            return redirect("core:import-enquiries")

        export_destination_form = form_dict["export_destination"]
        export_destination_value = export_destination_form.cleaned_data[
            "export_destination"
        ]
        if export_destination_value == ExportDestinationChoices.EU:
            return redirect("core:eu-export-enquiries")
        elif export_destination_value == ExportDestinationChoices.NON_EU:
            return redirect("core:non-eu-export-enquiries")


class ImportEnquiriesView(TemplateView):
    template_name = "core/import_enquiries.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["GOV_UK_EXPORT_GOODS_URL"] = settings.GOV_UK_EXPORT_GOODS_URL

        return ctx


class EUExportEnquiriesView(TemplateView):
    template_name = "core/eu_export_enquiries.html"


class NonEUExportEnquiriesView(TemplateView):
    template_name = "core/non_eu_export_enquiries.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["GREAT_CONTACT_FORM_URL"] = settings.GREAT_CONTACT_FORM_URL
        ctx["GOV_UK_EXPORT_GOODS_URL"] = settings.GOV_UK_EXPORT_GOODS_URL

        return ctx
