from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import RedirectView, TemplateView
from formtools.wizard.views import NamedUrlSessionWizardView

from .forms import (
    BusinessDetailsForm,
    EnquiryDetailsForm,
    EnquirySubjectChoices,
    EnquirySubjectForm,
    ExportCountriesForm,
    ExportDestinationChoices,
    ExportDestinationForm,
    PersonalDetailsForm,
    SectorsForm,
)
from .utils import dict_to_query_dict, get_reference_number


class IndexView(RedirectView):
    url = reverse_lazy("core:enquiry-wizard")


def is_eu_enquiry(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step("export-destination")

    if not cleaned_data:
        return True

    return cleaned_data["export_destination"] == ExportDestinationChoices.EU


class EnquiryWizardView(NamedUrlSessionWizardView):
    form_list = [
        ("enquiry-subject", EnquirySubjectForm),
        ("export-destination", ExportDestinationForm),
        ("export-countries", ExportCountriesForm),
        ("personal-details", PersonalDetailsForm),
        ("business-details", BusinessDetailsForm),
        ("sectors", SectorsForm),
        ("enquiry-details", EnquiryDetailsForm),
    ]
    condition_dict = {
        "export-countries": is_eu_enquiry,
        "personal-details": is_eu_enquiry,
        "business-details": is_eu_enquiry,
        "sectors": is_eu_enquiry,
        "enquiry-details": is_eu_enquiry,
    }

    def get_template_names(self):
        templates = {
            form_name: f"core/{form_name.replace('-', '_')}_wizard_step.html"
            for form_name in self.form_list
        }

        return [templates[self.steps.current]]

    def done(self, form_list, form_dict, **kwargs):
        cleaned_data = self.get_cleaned_data_for_step("export-destination")

        if (
            cleaned_data
            and cleaned_data["export_destination"] == ExportDestinationChoices.NON_EU
        ):
            enquiry_subject_form = form_dict["enquiry-subject"]
            filter_data = enquiry_subject_form.get_filter_data()
            params = dict_to_query_dict(filter_data)
            url = reverse("core:non-eu-export-enquiries")

            return redirect(f"{url}?{params.urlencode()}")

        ctx = {
            "reference_number": get_reference_number(),
        }

        return render(self.request, "core/enquiry_contact_success.html", ctx)


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


class EnquiryContactSuccessView(TemplateView):
    template_name = "core/enquiry_contact_success.html"


class StartPageRedirectView(RedirectView):
    url = "https://34ul06.axshare.com/#id=shpprj&p=dev_prototype_-_v1&dp=0&fn=0&c=1"
