from django.conf import settings
from django.http import QueryDict
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView
from django.views.generic.base import RedirectView
from formtools.wizard.views import NamedUrlSessionWizardView

from .forms import (
    EnquiryContactForm,
    EnquirySubjectChoices,
    EnquirySubjectForm,
    ExportCountriesForm,
    ExportDestinationForm,
)


class IndexView(RedirectView):
    url = reverse_lazy("core:enquiry-wizard")


class EnquiryWizardView(NamedUrlSessionWizardView):
    form_list = [
        ("enquiry-subject", EnquirySubjectForm),
        ("export-destination", ExportDestinationForm),
        ("export-countries", ExportCountriesForm),
    ]

    def get_template_names(self):
        templates = {
            form_name: f"core/{form_name.replace('-', '_')}_wizard_step.html"
            for form_name in self.form_list
        }

        return [templates[self.steps.current]]

    def done(self, form_list, form_dict, **kwargs):
        return redirect("core:enquiry-contact-success")


class ImportEnquiriesView(TemplateView):
    template_name = "core/import_enquiries.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["GOV_UK_EXPORT_GOODS_URL"] = settings.GOV_UK_EXPORT_GOODS_URL

        return ctx


class BaseEnquiriesView(TemplateView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["should_display_sub_headings"] = True
        ctx["should_display_export_goods"] = True
        ctx["should_display_export_services"] = True

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

            num_visible_sections = len(
                [
                    c
                    for c in [
                        has_export_goods_selected,
                        has_export_services_selected,
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
            ] = f"Sell {' and '.join(selected_components_heading_content)} {self.heading_ending}"

        return ctx


class EUExportEnquiriesView(BaseEnquiriesView):
    heading_ending = "into the EU"
    template_name = "core/eu_export_enquiries.html"


class NonEUExportEnquiriesView(BaseEnquiriesView):
    heading_ending = "abroad"
    template_name = "core/non_eu_export_enquiries.html"


class EnquiryContactView(FormView):
    form_class = EnquiryContactForm
    success_url = reverse_lazy("core:enquiry-contact-success")
    template_name = "core/enquiry_contact.html"


class EnquiryContactSuccessView(TemplateView):
    template_name = "core/enquiry_contact_success.html"


class StartPageRedirectView(RedirectView):
    url = "https://34ul06.axshare.com/#id=shpprj&p=dev_prototype_-_v1&dp=0&fn=0&c=1"
