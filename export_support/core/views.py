import json
import logging
from datetime import datetime

import mohawk
import requests
from directory_forms_api_client import helpers
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import RedirectView, TemplateView
from formtools.wizard.views import NamedUrlSessionWizardView

from .forms import (
    BusinessAdditionalInformationForm,
    BusinessDetailsForm,
    BusinessTypeChoices,
    BusinessTypeForm,
    EnquiryDetailsForm,
    EnquirySubjectChoices,
    EnquirySubjectForm,
    ExportCountriesForm,
    OrganisationAdditionalInformationForm,
    OrganisationDetailsForm,
    PersonalDetailsForm,
    SectorsForm,
    SoloExporterAdditionalInformationForm,
    SoloExporterDetailsForm,
    ZendeskForm,
)
from .utils import dict_to_query_dict

logger = logging.getLogger(__name__)


class IndexView(RedirectView):
    url = reverse_lazy("core:enquiry-wizard")


def is_business_type(business_type_choice):
    def _is_type(wizard):
        cleaned_data = wizard.get_cleaned_data_for_step("business-type")
        if not cleaned_data:
            return True

        business_type = cleaned_data["business_type"]

        return business_type == business_type_choice

    return _is_type


class EnquiryWizardView(NamedUrlSessionWizardView):
    form_list = [
        ("enquiry-subject", EnquirySubjectForm),
        ("export-countries", ExportCountriesForm),
        ("personal-details", PersonalDetailsForm),
        ("business-type", BusinessTypeForm),
        ("business-details", BusinessDetailsForm),
        (
            "business-additional-information",
            BusinessAdditionalInformationForm,
        ),
        ("organisation-details", OrganisationDetailsForm),
        ("organisation-additional-information", OrganisationAdditionalInformationForm),
        ("solo-exporter-details", SoloExporterDetailsForm),
        ("solo-exporter-additional-information", SoloExporterAdditionalInformationForm),
        ("sectors", SectorsForm),
        ("enquiry-details", EnquiryDetailsForm),
    ]
    condition_dict = {
        "business-details": is_business_type(BusinessTypeChoices.PRIVATE_OR_LIMITED),
        "business-additional-information": is_business_type(
            BusinessTypeChoices.PRIVATE_OR_LIMITED
        ),
        "organisation-details": is_business_type(BusinessTypeChoices.OTHER),
        "organisation-additional-information": is_business_type(
            BusinessTypeChoices.OTHER
        ),
        "solo-exporter-details": is_business_type(
            BusinessTypeChoices.SOLE_TRADE_OR_PRIVATE_INDIVIDUAL
        ),
        "solo-exporter-additional-information": is_business_type(
            BusinessTypeChoices.SOLE_TRADE_OR_PRIVATE_INDIVIDUAL
        ),
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

    def send_contact_consent(self):
        # Function to send consent confirmation to legal-basis-api

        enquiry_details_cleaned_data = self.get_cleaned_data_for_step("enquiry-details")
        personal_details_cleaned_data = self.get_cleaned_data_for_step(
            "personal-details"
        )

        if enquiry_details_cleaned_data["email_consent"]:
            url = settings.CONSENT_API_URL
            data = json.dumps(
                {
                    "consents": ["email_marketing"],
                    "modified_at": str(datetime.now()),
                    "email": personal_details_cleaned_data["email"],
                    "key_type": "email",
                }
            )

            header = mohawk.Sender(
                {
                    "id": settings.CONSENT_API_ID,
                    "key": settings.CONSENT_API_KEY,
                    "algorithm": "sha256",
                },
                url,
                settings.CONSENT_API_METHOD,
                content_type="application/json",
                content=data,
            ).request_header

            requests.request(
                settings.CONSENT_API_METHOD,
                url,
                data=data,
                headers={
                    "Authorization": header,
                    "Content-Type": "application/json",
                },
            ).raise_for_status()

            logger.info("Sent consent confirmation to legal-basis-api")

    def get_context_data(self, form, **kwargs):
        ctx = super().get_context_data(form=form, **kwargs)

        if self.steps.current == "export-countries":
            enquiry_subject_form = self.get_form(
                step="enquiry-subject",
                data=self.storage.get_step_data("enquiry-subject"),
            )
            if enquiry_subject_form.is_valid():
                filter_data = enquiry_subject_form.get_filter_data()
            else:
                filter_data = {}

            params = dict_to_query_dict(filter_data)
            guidance_url = reverse("core:non-eu-export-enquiries")

            ctx["guidance_url"] = f"{guidance_url}?{params.urlencode()}"

        return ctx

    def done(self, form_list, form_dict, **kwargs):
        enquiry_subject_cleaned_data = self.get_cleaned_data_for_step("enquiry-subject")
        enquiry_subject = enquiry_subject_cleaned_data["enquiry_subject"]

        display_goods = EnquirySubjectChoices.SELLING_GOODS_ABROAD in enquiry_subject
        display_services = (
            EnquirySubjectChoices.SELLING_SERVICES_ABROAD in enquiry_subject
        )
        display_subheadings = display_goods and display_services

        ctx = {
            "display_goods": display_goods,
            "display_services": display_services,
            "display_subheadings": display_subheadings,
        }

        self.send_contact_consent()
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
