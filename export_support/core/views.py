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
    ShortEnquiryForm,
    SoloExporterAdditionalInformationForm,
    SoloExporterDetailsForm,
    ZendeskForm,
)
from .models import FormTypeCounter
from .utils import dict_to_query_dict

logger = logging.getLogger(__name__)


class IndexView(RedirectView):

    ab_testing_enabled = settings.AB_TESTING_ENABLED

    if ab_testing_enabled:
        long_count = FormTypeCounter.objects.filter(
            form_type="long", load_or_sub="load"
        ).count()
        short_count = FormTypeCounter.objects.filter(
            form_type="short", load_or_sub="load"
        ).count()

        if short_count >= long_count:
            logger.info(
                "Counts: short - "
                + str(short_count)
                + " long - "
                + str(long_count)
                + " Using long form variation"
            )
            count_update = FormTypeCounter(form_type="long", load_or_sub="load")
            count_update.save()
            url = reverse_lazy("core:enquiry-wizard")
        else:
            logger.info(
                "Counts: short - "
                + str(short_count)
                + " long - "
                + str(long_count)
                + " Using short form variation"
            )
            count_update = FormTypeCounter(form_type="short", load_or_sub="load")
            count_update.save()
            url = reverse_lazy("core:enquiry-wizard-short")
    else:
        # Original code to restore after test:
        url = reverse_lazy("core:enquiry-wizard")


def is_business_type(business_type_choice, on_default_path=False):
    """Returns a function to assert whether the wizard step should be shown
    based on the business type selected.

    The `on_default_path` allows the returned function to return a default
    value if the business type hasn't been filled in yet. This is important
    when we want to show the correct number of steps in the form.
    """

    def _is_type(wizard):
        cleaned_data = wizard.get_cleaned_data_for_step("business-type")
        if not cleaned_data:
            return on_default_path

        business_type = cleaned_data["business_type"]

        return business_type == business_type_choice

    return _is_type


def filter_private_values(value):
    def _is_private_value(val):
        val = str(val)
        return val.startswith("__") and val.endswith("__")

    if isinstance(value, list):
        value = [val for val in value if not _is_private_value(val)]
    else:
        value = value if not _is_private_value(value) else None

    return value


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
        "business-details": is_business_type(
            BusinessTypeChoices.PRIVATE_OR_LIMITED, on_default_path=True
        ),
        "business-additional-information": is_business_type(
            BusinessTypeChoices.PRIVATE_OR_LIMITED,
            on_default_path=True,
        ),
        "organisation-details": is_business_type(BusinessTypeChoices.OTHER),
        "organisation-additional-information": is_business_type(
            BusinessTypeChoices.OTHER,
        ),
        "solo-exporter-details": is_business_type(
            BusinessTypeChoices.SOLE_TRADE_OR_PRIVATE_INDIVIDUAL,
        ),
        "solo-exporter-additional-information": is_business_type(
            BusinessTypeChoices.SOLE_TRADE_OR_PRIVATE_INDIVIDUAL,
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

                field_value = form.cleaned_data[field_name]
                field_value = filter_private_values(field_value)
                if not field_value:
                    continue

                custom_fields_data.append({custom_field_id: field_value})

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

        # Delete counter when AB testing is complete
        count_update = FormTypeCounter(form_type="long", load_or_sub="sub")
        count_update.save()

        return render(self.request, "core/enquiry_contact_success.html", ctx)


class ShortEnquiryWizardView(NamedUrlSessionWizardView):
    form_list = [
        ("short-enquiry", ShortEnquiryForm),
    ]

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

                try:
                    # Need this to fill required fields which are no longer collected
                    field_value = form.cleaned_data[field_name]
                    field_value = filter_private_values(field_value)
                    if not field_value:
                        continue
                except KeyError:
                    field_value = "-"

                custom_fields_data.append({custom_field_id: field_value})

        form_data["_custom_fields"] = custom_fields_data

        return form_data

    def send_to_zendesk(self, form_list):
        form_data = self.get_form_data(form_list)
        zendesk_form = ZendeskForm(data=form_data)
        if not zendesk_form.is_valid():
            raise ValueError("Invalid ZendeskForm", dict(zendesk_form.errors))

        enquiry_details_cleaned_data = self.get_cleaned_data_for_step("short-enquiry")
        full_name = enquiry_details_cleaned_data["full_name"]
        email_address = enquiry_details_cleaned_data["email"]

        subject = "N/A"
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

        enquiry_details_cleaned_data = self.get_cleaned_data_for_step("short-enquiry")

        if enquiry_details_cleaned_data["email_consent"]:
            url = settings.CONSENT_API_URL
            data = json.dumps(
                {
                    "consents": ["email_marketing"],
                    "modified_at": str(datetime.now()),
                    "email": enquiry_details_cleaned_data["email"],
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
        return ctx

    def done(self, form_list, form_dict, **kwargs):
        # enquiry_subject_cleaned_data = self.get_cleaned_data_for_step("short-enquiry")
        # enquiry_subject = enquiry_subject_cleaned_data["enquiry_subject"]
        # enquiry_subject = enquiry_subject_cleaned_data["question"]

        # display_goods = EnquirySubjectChoices.SELLING_GOODS_ABROAD in enquiry_subject
        # display_services = (
        #    EnquirySubjectChoices.SELLING_SERVICES_ABROAD in enquiry_subject
        # )
        # display_subheadings = display_goods and display_services

        # ctx = {
        #    "display_goods": display_goods,
        #    "display_services": display_services,
        #    "display_subheadings": display_subheadings,
        # }

        # logger.critical("*************************************************************")
        # logger.critical("*************************************************************")
        # logger.critical(
        #    "Keys: " + str(self.get_cleaned_data_for_step("short-enquiry").keys())
        # )
        # logger.critical("full_name: " + str(enquiry_subject_cleaned_data["full_name"]))
        # logger.critical("email: " + str(enquiry_subject_cleaned_data["email"]))
        # logger.critical(
        #    "company_name: " + str(enquiry_subject_cleaned_data["company_name"])
        # )
        # logger.critical(
        #    "company_registration_number: "
        #    + str(enquiry_subject_cleaned_data["company_registration_number"])
        # )
        # logger.critical(
        #    "company_post_code: "
        #    + str(enquiry_subject_cleaned_data["company_post_code"])
        # )
        # logger.critical("sectors: " + str(enquiry_subject_cleaned_data["sectors"]))
        # logger.critical("other: " + str(enquiry_subject_cleaned_data["other"]))
        # logger.critical("question: " + str(enquiry_subject_cleaned_data["question"]))
        # logger.critical(
        #    "email_consent: " + str(enquiry_subject_cleaned_data["email_consent"])
        # )
        # logger.critical("*************************************************************")
        # logger.critical("*************************************************************")

        # ('Invalid ZendeskForm', {
        #    'enquiry_subject': ['This field is required.'],
        #    'countries': ['This field is required.'],
        #    'on_behalf_of': ['This field is required.'],
        #    'company_type': ['This field is required.'],
        #    'company_type_category': ['This field is required.'],
        #    'how_did_you_hear_about_this_service': ['This field is required.']
        # })

        # Keys: dict_keys([
        #    'full_name',
        #    'email',
        #    'company_name',
        #    'company_registration_number',
        #    'company_post_code',
        #    'sectors',
        #    'other',
        #    'question',
        #    'email_consent'
        # ])

        ctx = {"enquiry": "short_question"}

        self.send_contact_consent()
        self.send_to_zendesk(form_list)

        count_update = FormTypeCounter(form_type="short", load_or_sub="sub")
        count_update.save()

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
