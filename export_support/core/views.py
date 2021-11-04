from directory_forms_api_client import helpers
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import RedirectView, TemplateView
from formtools.wizard.views import NamedUrlSessionWizardView

from .forms import (
    BusinessDetailsForm,
    EnquiryDetailsForm,
    EnquirySubjectChoices,
    ExportCountriesForm,
    OnBehalfOfChoices,
    PersonalDetailsForm,
    SectorsForm,
    ZendeskForm,
)


class IndexView(RedirectView):
    url = reverse_lazy("core:enquiry-wizard")


def is_company(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step("personal-details")
    if not cleaned_data:
        return True

    return cleaned_data["on_behalf_of"] != OnBehalfOfChoices.NOT_A_COMPANY


class EnquiryWizardView(NamedUrlSessionWizardView):
    form_list = [
        ("export-countries", ExportCountriesForm),
        ("personal-details", PersonalDetailsForm),
        ("business-details", BusinessDetailsForm),
        ("sectors", SectorsForm),
        ("enquiry-details", EnquiryDetailsForm),
    ]
    condition_dict = {
        "business-details": is_company,
        "business-size": is_company,
    }

    def get_template_names(self):
        templates = {
            form_name: f"core/{form_name.replace('-', '_')}_wizard_step.html"
            for form_name in self.form_list
        }

        return [templates[self.steps.current]]

    def get_form_data(self, form_list):
        form_data = {}
        custom_fields_data = []
        custom_field_mapping = settings.ZENDESK_CUSTOM_FIELD_MAPPING

        for form in form_list:
            for field_name, field_value in form.get_zendesk_data().items():
                field_name = ZendeskForm.FIELD_MAPPING.get(field_name, field_name)
                form_data[field_name] = field_value
                try:
                    custom_field_id = custom_field_mapping[field_name]
                except KeyError:
                    continue
                else:
                    custom_fields_data.append(
                        {custom_field_id: form.cleaned_data[field_name]}
                    )

        form_data["_custom_fields"] = custom_fields_data

        return form_data

    def send_to_zendesk(self, form_list):
        form_data = self.get_form_data(form_list)
        zendesk_form = ZendeskForm(data=form_data)
        if not zendesk_form.is_valid():
            raise ValueError("Invalid ZendeskForm", dict(zendesk_form.errors))

        personal_details_cleaned_data = self.get_cleaned_data_for_step(
            "personal-details"
        )
        first_name = personal_details_cleaned_data["first_name"]
        last_name = personal_details_cleaned_data["last_name"]
        full_name = f"{first_name} {last_name}"
        email_address = personal_details_cleaned_data["email"]

        enquiry_details_cleaned_data = self.get_cleaned_data_for_step("enquiry-details")
        subject = enquiry_details_cleaned_data["nature_of_enquiry"] or "N/A"
        question = enquiry_details_cleaned_data["question"]

        spam_control = helpers.SpamControl(contents=question)
        sender = helpers.Sender(
            country_code="",
            email_address=email_address,
        )

        zendesk_form.save(
            form_url=settings.FORM_URL,
            full_name=full_name,
            email_address=email_address,
            subject=subject,
            service_name=settings.ZENDESK_SERVICE_NAME,
            subdomain=settings.ZENDESK_SUBDOMAIN,
            spam_control=spam_control,
            sender=sender,
        )

    def get_context_data(self, form, **kwargs):
        ctx = super().get_context_data(form=form, **kwargs)

        if self.steps.current == "export-countries":
            guidance_url = reverse("core:non-eu-export-enquiries")
            ctx["guidance_url"] = guidance_url

        return ctx

    def done(self, form_list, form_dict, **kwargs):
        ctx = {
            "display_goods": True,
            "display_services": True,
            "display_subheadings": True,
        }

        self.send_to_zendesk(form_list)

        return render(self.request, "core/enquiry_contact_success.html", ctx)


class NonEUExportEnquiriesView(TemplateView):
    template_name = "core/non_eu_export_enquiries.html"

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

        selected_components_heading_content = [
            heading_components[component] for component in selected_heading_components
        ]
        ctx[
            "heading"
        ] = f"Sell {' and '.join(selected_components_heading_content)} abroad"

        return ctx


class PrivacyView(TemplateView):
    template_name = "core/privacy.html"


class LegalDisclaimer(TemplateView):
    template_name = "core/legal_disclaimer.html"


class AccessibilityStatement(TemplateView):
    template_name = "core/accessibility_statement.html"
