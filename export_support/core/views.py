from django.conf import settings
from django.http import QueryDict
from django.shortcuts import redirect
from django.urls import reverse
from django.urls.base import reverse_lazy
from django.views.generic import FormView, TemplateView
from formtools.wizard.views import SessionWizardView

from .forms import (
    EnquiryContactForm,
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
            url = reverse("core:eu-export-enquiries")
            return redirect(f"{url}?{params.urlencode()}")
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["should_display_sub_headings"] = True
        ctx["should_display_export_goods"] = True
        ctx["should_display_export_services"] = True
        ctx["should_display_import_goods"] = True

        heading_components = {
            EnquirySubjectChoices.SELLING_GOODS_ABROAD: "goods",
            EnquirySubjectChoices.SELLING_SERVICES_ABROAD: "services",
        }
        selected_heading_components = [
            EnquirySubjectChoices.SELLING_GOODS_ABROAD,
            EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
        ]

        enquiry_subject_form = EnquirySubjectForm(self.request.GET)
        if enquiry_subject_form.is_valid():
            selected_heading_components = []

            enquiry_subject_value = enquiry_subject_form.cleaned_data["enquiry_subject"]

            has_export_goods_selected = (
                EnquirySubjectChoices.SELLING_GOODS_ABROAD in enquiry_subject_value
            )
            ctx["should_display_export_goods"] = has_export_goods_selected
            if has_export_goods_selected:
                selected_heading_components.append(
                    EnquirySubjectChoices.SELLING_GOODS_ABROAD
                )

            has_export_services_selected = (
                EnquirySubjectChoices.SELLING_SERVICES_ABROAD in enquiry_subject_value
            )
            ctx["should_display_export_services"] = has_export_services_selected
            if has_export_services_selected:
                selected_heading_components.append(
                    EnquirySubjectChoices.SELLING_SERVICES_ABROAD
                )

            has_import_goods_selected = (
                EnquirySubjectChoices.IMPORTING_GOODS_TO_THE_UK in enquiry_subject_value
            )
            ctx["should_display_import_goods"] = has_import_goods_selected

            num_visible_sections = len(
                [
                    c
                    for c in [
                        has_export_goods_selected,
                        has_export_services_selected,
                        has_import_goods_selected,
                    ]
                    if c
                ]
            )
            ctx["should_display_sub_headings"] = num_visible_sections > 1

            selected_components_heading_content = [
                heading_components[component]
                for component in selected_heading_components
            ]
            ctx[
                "heading"
            ] = f"Sell {' and '.join(selected_components_heading_content)} into the EU"

        return ctx


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

        return ctx


class EnquiryContactView(FormView):
    form_class = EnquiryContactForm
    success_url = reverse_lazy("core:enquiry-contact-success")
    template_name = "core/enquiry_contact.html"


class EnquiryContactSuccessView(TemplateView):
    template_name = "core/enquiry_contact_success.html"
