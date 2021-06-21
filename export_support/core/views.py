from django.conf import settings
from django.http import QueryDict
from django.shortcuts import redirect
from django.urls import reverse
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

        params = QueryDict(mutable=True)
        for form in form_list:
            for key, value in form.get_filter_data().items():
                if isinstance(value, list):
                    params.setlist(key, value)
                else:
                    params[key] = value

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
            url = reverse("core:non-eu-export-enquiries")
            return redirect(f"{url}?{params.urlencode()}")


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

        ctx["should_display_import_goods_section"] = True

        enquiry_subject_form = EnquirySubjectForm(self.request.GET)
        if enquiry_subject_form.is_valid():
            enquiry_subject_value = enquiry_subject_form.cleaned_data["enquiry_subject"]
            has_import_selected = (
                EnquirySubjectChoices.IMPORTING_GOODS_TO_THE_UK in enquiry_subject_value
            )
            ctx["should_display_import_goods_section"] = has_import_selected

        ctx["GOV_UK_EXPORT_GOODS_URL"] = settings.GOV_UK_EXPORT_GOODS_URL

        return ctx
