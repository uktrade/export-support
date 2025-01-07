import logging
from enum import Enum

import pytest
import requests_mock
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from ...consts import ENQUIRY_MARKET_CODES
from ...forms import (
    SECTORS_MAP,
    BusinessTypeChoices,
    CompanyTurnoverChoices,
    DoYouHaveAProductYouWantToExportChoices,
    EnquirySubjectChoices,
    HaveYouExportedBeforeChoices,
    HowDidYouHearAboutThisServiceChoices,
    NumberOfEmployeesChoices,
    OnBehalfOfChoices,
    OrganisationTypeChoices,
    PositivityForGrowthChoices,
    PrivateOrPublicCompanyTypeChoices,
    SoloExporterTypeChoices,
)

logger = logging.getLogger(__name__)

MARKET_MACHINE_READABLE_VALUES = list(ENQUIRY_MARKET_CODES.values())


def get_coerced_field_value(field_value):
    if isinstance(field_value, list):
        return [get_coerced_field_value(v) for v in field_value]
    if isinstance(field_value, Enum):
        return str(field_value)
    return field_value


def get_form_data(step_name, data):
    form_data = {
        "enquiry_wizard_view-current_step": step_name,
        **{
            f"{step_name}-{field_name}": get_coerced_field_value(field_value)
            for field_name, field_value in data.items()
        },
    }

    return form_data


def get_step_url(step_name):
    return reverse("core:enquiry-wizard-step", kwargs={"step": step_name})


def assert_number_of_steps(response, *, current_step_number, total_number_of_steps):
    ctx = response.context_data
    steps = ctx["wizard"]["steps"]
    assert steps.step1 == current_step_number
    assert steps.count == total_number_of_steps


@pytest.mark.django_db
def test_full_steps_private_or_limited_business_type_wizard_success(
    client, settings, mocker
):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {}

    mock_zendesk_form_action_class = mocker.patch(
        "export_support.core.forms.ZendeskForm.action_class"
    )

    wizard_start_url = reverse("core:enquiry-wizard")
    response = client.get(wizard_start_url)
    assert response.status_code == 302

    enquiry_subject_url = get_step_url("enquiry-subject")
    assert response.url == enquiry_subject_url

    response = client.get(enquiry_subject_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=1, total_number_of_steps=8)
    assertTemplateUsed(response, "core/enquiry_subject_wizard_step.html")
    response = client.post(
        enquiry_subject_url,
        get_form_data(
            "enquiry-subject",
            {
                "enquiry_subject": [
                    EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                    EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
                ]
            },
        ),
    )
    assert response.status_code == 302

    export_markets_url = get_step_url("export-markets")
    assert response.url == export_markets_url

    response = client.get(export_markets_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=2, total_number_of_steps=8)
    assertTemplateUsed(response, "core/export_markets_wizard_step.html")
    response = client.post(
        export_markets_url,
        get_form_data(
            "export-markets",
            {"markets": ["mexico__ess_export", "nigeria__ess_export"]},
        ),
    )
    assert response.status_code == 302

    personal_details_url = get_step_url("personal-details")
    assert response.url == personal_details_url

    response = client.get(personal_details_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=3, total_number_of_steps=8)
    assertTemplateUsed(response, "core/personal_details_wizard_step.html")
    response = client.post(
        personal_details_url,
        get_form_data(
            "personal-details",
            {
                "first_name": "Firstname",
                "last_name": "Lastname",
                "email": "test@example.com",
                "on_behalf_of": OnBehalfOfChoices.OWN_COMPANY,
            },
        ),
    )
    assert response.status_code == 302

    business_type_url = get_step_url("business-type")
    assert response.url == business_type_url

    response = client.get(business_type_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=4, total_number_of_steps=8)
    assertTemplateUsed(response, "core/business_type_wizard_step.html")
    response = client.post(
        business_type_url,
        get_form_data(
            "business-type",
            {
                "business_type": BusinessTypeChoices.PRIVATE_OR_LIMITED,
            },
        ),
    )
    assert response.status_code == 302

    business_details_url = get_step_url("business-details")
    assert response.url == business_details_url

    response = client.get(business_details_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=5, total_number_of_steps=8)
    assertTemplateUsed(response, "core/business_details_wizard_step.html")
    response = client.post(
        business_details_url,
        get_form_data(
            "business-details",
            {
                "company_name": "Companyname",
                "company_post_code": "SW1A 2BL",
                "company_registration_number": "12345678",
                "have_you_exported_before": HaveYouExportedBeforeChoices.NO,
                "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
            },
        ),
    )
    assert response.status_code == 302

    business_additional_information_url = get_step_url(
        "business-additional-information"
    )
    assert response.url == business_additional_information_url

    response = client.get(business_additional_information_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=6, total_number_of_steps=8)
    assertTemplateUsed(
        response, "core/business_additional_information_wizard_step.html"
    )
    response = client.post(
        business_additional_information_url,
        get_form_data(
            "business-additional-information",
            {
                "company_type": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
                "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
                "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
            },
        ),
    )
    assert response.status_code == 302

    sectors_url = get_step_url("sectors")
    assert response.url == sectors_url

    response = client.get(sectors_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=7, total_number_of_steps=8)
    assertTemplateUsed(response, "core/sectors_wizard_step.html")
    response = client.post(
        sectors_url,
        get_form_data(
            "sectors",
            {
                "sectors": [sector for sector in SECTORS_MAP.keys()],
                "other": "ANOTHER SECTOR",
            },
        ),
    )
    assert response.status_code == 302

    enquiry_details_url = get_step_url("enquiry-details")
    assert response.url == enquiry_details_url

    response = client.get(enquiry_details_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=8, total_number_of_steps=8)
    assertTemplateUsed(response, "core/enquiry_details_wizard_step.html")
    response = client.post(
        enquiry_details_url,
        get_form_data(
            "enquiry-details",
            {
                "nature_of_enquiry": "NATURE OF ENQUIRY",
                "question": "QUESTION",
                "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
            },
        ),
    )
    assert response.status_code == 302

    done_url = get_step_url("done")
    assert response.url == done_url

    with requests_mock.mock():
        response = client.get(done_url)

    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_contact_success.html")

    mock_zendesk_form_action_class.assert_called_with(
        form_url="FORM_URL",
        full_name="Firstname Lastname",
        email_address="test@example.com",
        subject="NATURE OF ENQUIRY",
        service_name="ZENDESK_SERVICE_NAME",
        subdomain="ZENDESK_SUBDOMAIN",
        spam_control={"contents": "QUESTION"},
        sender={
            "email_address": "test@example.com",
            "country_code": "",
            "ip_address": None,
        },
    )
    mock_zendesk_form_action_class().save.assert_called_with(
        {
            "aaa_question": "QUESTION",
            "company_name": "Companyname",
            "company_post_code": "SW1A 2BL",
            "company_registration_number": "12345678",
            "company_turnover": "Below £85,000",
            "company_type": "Private limited company",
            "company_type_category": "UK private or public limited company",
            "markets": "Mexico, Nigeria",
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            "how_did_you_hear_about_this_service": "Search engine",
            "marketing_consent": True,
            "have_you_exported_before": "No",
            "do_you_have_a_product_you_want_to_export": "Yes",
            "positivity_for_growth": "Neutral",
            "_custom_fields": None,
        }
    )


@pytest.mark.django_db
def test_full_steps_other_organisation_business_type_wizard_success(
    client, settings, mocker
):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {}

    mock_zendesk_form_action_class = mocker.patch(
        "export_support.core.forms.ZendeskForm.action_class"
    )

    wizard_start_url = reverse("core:enquiry-wizard")
    response = client.get(wizard_start_url)
    assert response.status_code == 302

    enquiry_subject_url = get_step_url("enquiry-subject")
    assert response.url == enquiry_subject_url

    response = client.get(enquiry_subject_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=1, total_number_of_steps=8)
    assertTemplateUsed(response, "core/enquiry_subject_wizard_step.html")
    response = client.post(
        enquiry_subject_url,
        get_form_data(
            "enquiry-subject",
            {
                "enquiry_subject": [
                    EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                    EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
                ]
            },
        ),
    )
    assert response.status_code == 302

    export_markets_url = get_step_url("export-markets")
    assert response.url == export_markets_url

    response = client.get(export_markets_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=2, total_number_of_steps=8)
    assertTemplateUsed(response, "core/export_markets_wizard_step.html")
    response = client.post(
        export_markets_url,
        get_form_data(
            "export-markets",
            {"markets": ["japan__ess_export", "lithuania__ess_export"]},
        ),
    )
    assert response.status_code == 302

    personal_details_url = get_step_url("personal-details")
    assert response.url == personal_details_url

    response = client.get(personal_details_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=3, total_number_of_steps=8)
    assertTemplateUsed(response, "core/personal_details_wizard_step.html")
    response = client.post(
        personal_details_url,
        get_form_data(
            "personal-details",
            {
                "first_name": "Firstname",
                "last_name": "Lastname",
                "email": "test@example.com",
                "on_behalf_of": OnBehalfOfChoices.OWN_COMPANY,
            },
        ),
    )
    assert response.status_code == 302

    business_type_url = get_step_url("business-type")
    assert response.url == business_type_url

    response = client.get(business_type_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=4, total_number_of_steps=8)
    assertTemplateUsed(response, "core/business_type_wizard_step.html")
    response = client.post(
        business_type_url,
        get_form_data(
            "business-type",
            {
                "business_type": BusinessTypeChoices.OTHER,
            },
        ),
    )
    assert response.status_code == 302

    organisation_details_url = get_step_url("organisation-details")
    assert response.url == organisation_details_url

    response = client.get(organisation_details_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=5, total_number_of_steps=8)
    assertTemplateUsed(response, "core/organisation_details_wizard_step.html")
    response = client.post(
        organisation_details_url,
        get_form_data(
            "organisation-details",
            {
                "company_name": "Organisationname",
                "company_post_code": "SW1A 2BL",
                "company_registration_number": "12345678",
                "have_you_exported_before": HaveYouExportedBeforeChoices.NO,
                "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
            },
        ),
    )
    assert response.status_code == 302

    organisation_additional_information = get_step_url(
        "organisation-additional-information"
    )
    assert response.url == organisation_additional_information

    response = client.get(organisation_additional_information)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=6, total_number_of_steps=8)
    assertTemplateUsed(
        response, "core/organisation_additional_information_wizard_step.html"
    )
    response = client.post(
        organisation_additional_information,
        get_form_data(
            "organisation-additional-information",
            {
                "company_type": OrganisationTypeChoices.CHARITY_OR_SOCIAL_ENTERPRISE,
                "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
                "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
            },
        ),
    )
    assert response.status_code == 302

    sectors_url = get_step_url("sectors")
    assert response.url == sectors_url

    response = client.get(sectors_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=7, total_number_of_steps=8)
    assertTemplateUsed(response, "core/sectors_wizard_step.html")
    response = client.post(
        sectors_url,
        get_form_data(
            "sectors",
            {
                "sectors": [sector for sector in SECTORS_MAP.keys()],
                "other": "ANOTHER SECTOR",
            },
        ),
    )
    assert response.status_code == 302

    enquiry_details_url = get_step_url("enquiry-details")
    assert response.url == enquiry_details_url

    response = client.get(enquiry_details_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=8, total_number_of_steps=8)
    assertTemplateUsed(response, "core/enquiry_details_wizard_step.html")
    response = client.post(
        enquiry_details_url,
        get_form_data(
            "enquiry-details",
            {
                "nature_of_enquiry": "NATURE OF ENQUIRY",
                "question": "QUESTION",
                "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
            },
        ),
    )
    assert response.status_code == 302

    done_url = get_step_url("done")
    assert response.url == done_url

    with requests_mock.mock():
        response = client.get(done_url)

    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_contact_success.html")

    mock_zendesk_form_action_class.assert_called_with(
        form_url="FORM_URL",
        full_name="Firstname Lastname",
        email_address="test@example.com",
        subject="NATURE OF ENQUIRY",
        service_name="ZENDESK_SERVICE_NAME",
        subdomain="ZENDESK_SUBDOMAIN",
        spam_control={"contents": "QUESTION"},
        sender={
            "email_address": "test@example.com",
            "country_code": "",
            "ip_address": None,
        },
    )
    mock_zendesk_form_action_class().save.assert_called_with(
        {
            "aaa_question": "QUESTION",
            "company_name": "Organisationname",
            "company_post_code": "SW1A 2BL",
            "company_registration_number": "12345678",
            "company_turnover": "Below £85,000",
            "company_type": "Charity / Social enterprise",
            "company_type_category": "Other type of UK organisation",
            "markets": "Japan, Lithuania",
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            "how_did_you_hear_about_this_service": "Search engine",
            "marketing_consent": True,
            "have_you_exported_before": "No",
            "do_you_have_a_product_you_want_to_export": "Yes",
            "positivity_for_growth": "Neutral",
            "_custom_fields": None,
        }
    )


@pytest.mark.django_db
def test_full_steps_solo_exporter_business_type_wizard_success(
    client, settings, mocker
):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {}

    mock_zendesk_form_action_class = mocker.patch(
        "export_support.core.forms.ZendeskForm.action_class"
    )

    wizard_start_url = reverse("core:enquiry-wizard")
    response = client.get(wizard_start_url)
    assert response.status_code == 302

    enquiry_subject_url = get_step_url("enquiry-subject")
    assert response.url == enquiry_subject_url

    response = client.get(enquiry_subject_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=1, total_number_of_steps=8)
    assertTemplateUsed(response, "core/enquiry_subject_wizard_step.html")
    response = client.post(
        enquiry_subject_url,
        get_form_data(
            "enquiry-subject",
            {
                "enquiry_subject": [
                    EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                    EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
                ]
            },
        ),
    )
    assert response.status_code == 302

    export_markets_url = get_step_url("export-markets")
    assert response.url == export_markets_url

    response = client.get(export_markets_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=2, total_number_of_steps=8)
    assertTemplateUsed(response, "core/export_markets_wizard_step.html")
    response = client.post(
        export_markets_url,
        get_form_data(
            "export-markets",
            {
                "markets": [
                    "iceland__ess_export",
                    "italy__ess_export",
                    "jamaica__ess_export",
                ]
            },
        ),
    )
    assert response.status_code == 302

    personal_details_url = get_step_url("personal-details")
    assert response.url == personal_details_url

    response = client.get(personal_details_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=3, total_number_of_steps=8)
    assertTemplateUsed(response, "core/personal_details_wizard_step.html")
    response = client.post(
        personal_details_url,
        get_form_data(
            "personal-details",
            {
                "first_name": "Firstname",
                "last_name": "Lastname",
                "email": "test@example.com",
                "on_behalf_of": OnBehalfOfChoices.OWN_COMPANY,
            },
        ),
    )
    assert response.status_code == 302

    business_type_url = get_step_url("business-type")
    assert response.url == business_type_url

    response = client.get(business_type_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=4, total_number_of_steps=8)
    assertTemplateUsed(response, "core/business_type_wizard_step.html")
    response = client.post(
        business_type_url,
        get_form_data(
            "business-type",
            {
                "business_type": BusinessTypeChoices.SOLE_TRADE_OR_PRIVATE_INDIVIDUAL,
            },
        ),
    )
    assert response.status_code == 302

    solo_exporter_details_url = get_step_url("solo-exporter-details")
    assert response.url == solo_exporter_details_url

    response = client.get(solo_exporter_details_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=5, total_number_of_steps=8)
    assertTemplateUsed(response, "core/solo_exporter_details_wizard_step.html")
    response = client.post(
        solo_exporter_details_url,
        get_form_data(
            "solo-exporter-details",
            {
                "company_name": "Soloexporter",
                "company_post_code": "SW1A 2BL",
                "have_you_exported_before": HaveYouExportedBeforeChoices.NO,
                "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
            },
        ),
    )
    assert response.status_code == 302

    solo_exporter_additional_information_url = get_step_url(
        "solo-exporter-additional-information"
    )
    assert response.url == solo_exporter_additional_information_url

    response = client.get(solo_exporter_additional_information_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=6, total_number_of_steps=8)
    assertTemplateUsed(
        response, "core/solo_exporter_additional_information_wizard_step.html"
    )
    response = client.post(
        solo_exporter_additional_information_url,
        get_form_data(
            "solo-exporter-additional-information",
            {
                "company_type": SoloExporterTypeChoices.SOLE_TRADER,
                "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
            },
        ),
    )
    assert response.status_code == 302

    sectors_url = get_step_url("sectors")
    assert response.url == sectors_url

    response = client.get(sectors_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=7, total_number_of_steps=8)
    assertTemplateUsed(response, "core/sectors_wizard_step.html")
    response = client.post(
        sectors_url,
        get_form_data(
            "sectors",
            {
                "sectors": [sector for sector in SECTORS_MAP.keys()],
                "other": "ANOTHER SECTOR",
            },
        ),
    )
    assert response.status_code == 302

    enquiry_details_url = get_step_url("enquiry-details")
    assert response.url == enquiry_details_url

    response = client.get(enquiry_details_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=8, total_number_of_steps=8)
    assertTemplateUsed(response, "core/enquiry_details_wizard_step.html")
    response = client.post(
        enquiry_details_url,
        get_form_data(
            "enquiry-details",
            {
                "nature_of_enquiry": "NATURE OF ENQUIRY",
                "question": "QUESTION",
                "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
            },
        ),
    )
    assert response.status_code == 302

    done_url = get_step_url("done")
    assert response.url == done_url

    with requests_mock.mock():
        response = client.get(done_url)

    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_contact_success.html")

    mock_zendesk_form_action_class.assert_called_with(
        form_url="FORM_URL",
        full_name="Firstname Lastname",
        email_address="test@example.com",
        subject="NATURE OF ENQUIRY",
        service_name="ZENDESK_SERVICE_NAME",
        subdomain="ZENDESK_SUBDOMAIN",
        spam_control={"contents": "QUESTION"},
        sender={
            "email_address": "test@example.com",
            "country_code": "",
            "ip_address": None,
        },
    )
    mock_zendesk_form_action_class().save.assert_called_with(
        {
            "aaa_question": "QUESTION",
            "company_name": "Soloexporter",
            "company_post_code": "SW1A 2BL",
            "company_registration_number": "",
            "company_turnover": "Below £85,000",
            "company_type": "Sole trader",
            "company_type_category": "Sole trader or private individual",
            "markets": "Iceland, Italy, Jamaica",
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            # noqa: E501
            "how_did_you_hear_about_this_service": "Search engine",
            "marketing_consent": True,
            "have_you_exported_before": "No",
            "do_you_have_a_product_you_want_to_export": "Yes",
            "positivity_for_growth": "Neutral",
            "_custom_fields": None,
        }
    )


@pytest.mark.django_db
def test_full_steps_private_or_limited_business_type_wizard_success_custom_fields(
    client, settings, mocker
):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {
        "company_turnover": "111",
        "enquiry_subject": "222",
        "markets": "333",
        "company_registration_number": "444",
        "company_type": "555",
        "company_post_code": "666",
    }

    mock_zendesk_form_action_class = mocker.patch(
        "export_support.core.forms.ZendeskForm.action_class"
    )

    wizard_start_url = reverse("core:enquiry-wizard")
    response = client.get(wizard_start_url)
    assert response.status_code == 302

    enquiry_subject_url = get_step_url("enquiry-subject")
    assert response.url == enquiry_subject_url

    response = client.get(enquiry_subject_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_subject_wizard_step.html")
    response = client.post(
        enquiry_subject_url,
        get_form_data(
            "enquiry-subject",
            {
                "enquiry_subject": [
                    EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                    EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
                ]
            },
        ),
    )
    assert response.status_code == 302

    export_markets_url = get_step_url("export-markets")
    assert response.url == export_markets_url

    response = client.get(export_markets_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/export_markets_wizard_step.html")
    response = client.post(
        export_markets_url,
        get_form_data(
            "export-markets",
            {
                "markets": [
                    "greece__ess_export",
                    "croatia__ess_export",
                    "india__ess_export",
                ]
            },
        ),
    )
    assert response.status_code == 302

    personal_details_url = get_step_url("personal-details")
    assert response.url == personal_details_url

    response = client.get(personal_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/personal_details_wizard_step.html")
    response = client.post(
        personal_details_url,
        get_form_data(
            "personal-details",
            {
                "first_name": "Firstname",
                "last_name": "Lastname",
                "email": "test@example.com",
                "on_behalf_of": OnBehalfOfChoices.OWN_COMPANY,
            },
        ),
    )
    assert response.status_code == 302

    business_type_url = get_step_url("business-type")
    assert response.url == business_type_url

    response = client.get(business_type_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/business_type_wizard_step.html")
    response = client.post(
        business_type_url,
        get_form_data(
            "business-type",
            {
                "business_type": BusinessTypeChoices.PRIVATE_OR_LIMITED,
            },
        ),
    )
    assert response.status_code == 302

    business_details_url = get_step_url("business-details")
    assert response.url == business_details_url

    response = client.get(business_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/business_details_wizard_step.html")
    response = client.post(
        business_details_url,
        get_form_data(
            "business-details",
            {
                "company_name": "Companyname",
                "company_post_code": "SW1A 2BL",
                "company_registration_number": "12345678",
                "have_you_exported_before": HaveYouExportedBeforeChoices.NO,
                "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
            },
        ),
    )
    assert response.status_code == 302

    business_additional_information_url = get_step_url(
        "business-additional-information"
    )
    assert response.url == business_additional_information_url

    response = client.get(business_additional_information_url)
    assert response.status_code == 200
    assertTemplateUsed(
        response, "core/business_additional_information_wizard_step.html"
    )
    response = client.post(
        business_additional_information_url,
        get_form_data(
            "business-additional-information",
            {
                "company_type": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
                "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
                "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
            },
        ),
    )
    assert response.status_code == 302

    sectors_url = get_step_url("sectors")
    assert response.url == sectors_url

    response = client.get(sectors_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/sectors_wizard_step.html")
    response = client.post(
        sectors_url,
        get_form_data(
            "sectors",
            {
                "sectors": [sector for sector in SECTORS_MAP.keys()],
                "other": "ANOTHER SECTOR",
            },
        ),
    )
    assert response.status_code == 302

    enquiry_details_url = get_step_url("enquiry-details")
    assert response.url == enquiry_details_url

    response = client.get(enquiry_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_details_wizard_step.html")
    response = client.post(
        enquiry_details_url,
        get_form_data(
            "enquiry-details",
            {
                "nature_of_enquiry": "NATURE OF ENQUIRY",
                "question": "QUESTION",
                "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
            },
        ),
    )
    assert response.status_code == 302

    done_url = get_step_url("done")
    assert response.url == done_url

    response = client.get(done_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_contact_success.html")

    mock_zendesk_form_action_class.assert_called_with(
        form_url="FORM_URL",
        full_name="Firstname Lastname",
        email_address="test@example.com",
        subject="NATURE OF ENQUIRY",
        service_name="ZENDESK_SERVICE_NAME",
        subdomain="ZENDESK_SUBDOMAIN",
        spam_control={"contents": "QUESTION"},
        sender={
            "email_address": "test@example.com",
            "country_code": "",
            "ip_address": None,
        },
    )
    mock_zendesk_form_action_class().save.assert_called_with(
        {
            "aaa_question": "QUESTION",
            "company_name": "Companyname",
            "company_post_code": "SW1A 2BL",
            "company_registration_number": "12345678",
            "company_turnover": "Below £85,000",
            "company_type": "Private limited company",
            "company_type_category": "UK private or public limited company",
            "markets": "Greece, Croatia, India",
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            # noqa: E501
            "how_did_you_hear_about_this_service": "Search engine",
            "marketing_consent": False,
            "have_you_exported_before": "No",
            "do_you_have_a_product_you_want_to_export": "Yes",
            "positivity_for_growth": "Neutral",
            "_custom_fields": [
                {
                    "222": [
                        EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                        EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
                    ]
                },
                {
                    "333": [
                        "greece__ess_export",
                        "croatia__ess_export",
                        "india__ess_export",
                    ]
                },
                {"666": "SW1A 2BL"},
                {"444": "12345678"},
                {"555": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY},
                {"111": CompanyTurnoverChoices.BELOW_85000},
            ],
        }
    )


@pytest.mark.django_db
def test_full_steps_other_organisation_business_type_wizard_success_custom_fields(
    client, settings, mocker
):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {
        "company_turnover": "111",
        "enquiry_subject": "222",
        "markets": "333",
        "company_registration_number": "444",
        "company_type": "555",
        "company_post_code": "666",
    }

    mock_zendesk_form_action_class = mocker.patch(
        "export_support.core.forms.ZendeskForm.action_class"
    )

    wizard_start_url = reverse("core:enquiry-wizard")
    response = client.get(wizard_start_url)
    assert response.status_code == 302

    enquiry_subject_url = get_step_url("enquiry-subject")
    assert response.url == enquiry_subject_url

    response = client.get(enquiry_subject_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_subject_wizard_step.html")
    response = client.post(
        enquiry_subject_url,
        get_form_data(
            "enquiry-subject",
            {
                "enquiry_subject": [
                    EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                    EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
                ]
            },
        ),
    )
    assert response.status_code == 302

    export_markets_url = get_step_url("export-markets")
    assert response.url == export_markets_url

    response = client.get(export_markets_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/export_markets_wizard_step.html")
    response = client.post(
        export_markets_url,
        get_form_data(
            "export-markets",
            {
                "markets": [
                    "germany__ess_export",
                    "france__ess_export",
                    "the_gambia__ess_export",
                ]
            },
        ),
    )
    assert response.status_code == 302

    personal_details_url = get_step_url("personal-details")
    assert response.url == personal_details_url

    response = client.get(personal_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/personal_details_wizard_step.html")
    response = client.post(
        personal_details_url,
        get_form_data(
            "personal-details",
            {
                "first_name": "Firstname",
                "last_name": "Lastname",
                "email": "test@example.com",
                "on_behalf_of": OnBehalfOfChoices.OWN_COMPANY,
            },
        ),
    )
    assert response.status_code == 302

    business_type_url = get_step_url("business-type")
    assert response.url == business_type_url

    response = client.get(business_type_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/business_type_wizard_step.html")
    response = client.post(
        business_type_url,
        get_form_data(
            "business-type",
            {
                "business_type": BusinessTypeChoices.OTHER,
            },
        ),
    )
    assert response.status_code == 302

    organisation_details_url = get_step_url("organisation-details")
    assert response.url == organisation_details_url

    response = client.get(organisation_details_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=5, total_number_of_steps=8)
    assertTemplateUsed(response, "core/organisation_details_wizard_step.html")
    response = client.post(
        organisation_details_url,
        get_form_data(
            "organisation-details",
            {
                "company_name": "Organisationname",
                "company_post_code": "SW1A 2BL",
                "company_registration_number": "12345678",
                "have_you_exported_before": HaveYouExportedBeforeChoices.NO,
                "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
            },
        ),
    )
    assert response.status_code == 302

    organisation_additional_information = get_step_url(
        "organisation-additional-information"
    )
    assert response.url == organisation_additional_information

    response = client.get(organisation_additional_information)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=6, total_number_of_steps=8)
    assertTemplateUsed(
        response, "core/organisation_additional_information_wizard_step.html"
    )
    response = client.post(
        organisation_additional_information,
        get_form_data(
            "organisation-additional-information",
            {
                "company_type": OrganisationTypeChoices.CHARITY_OR_SOCIAL_ENTERPRISE,
                "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
                "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
            },
        ),
    )
    assert response.status_code == 302

    sectors_url = get_step_url("sectors")
    assert response.url == sectors_url

    response = client.get(sectors_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/sectors_wizard_step.html")
    response = client.post(
        sectors_url,
        get_form_data(
            "sectors",
            {
                "sectors": [sector for sector in SECTORS_MAP.keys()],
                "other": "ANOTHER SECTOR",
            },
        ),
    )
    assert response.status_code == 302

    enquiry_details_url = get_step_url("enquiry-details")
    assert response.url == enquiry_details_url

    response = client.get(enquiry_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_details_wizard_step.html")
    response = client.post(
        enquiry_details_url,
        get_form_data(
            "enquiry-details",
            {
                "nature_of_enquiry": "NATURE OF ENQUIRY",
                "question": "QUESTION",
                "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
            },
        ),
    )
    assert response.status_code == 302

    done_url = get_step_url("done")
    assert response.url == done_url

    response = client.get(done_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_contact_success.html")

    mock_zendesk_form_action_class.assert_called_with(
        form_url="FORM_URL",
        full_name="Firstname Lastname",
        email_address="test@example.com",
        subject="NATURE OF ENQUIRY",
        service_name="ZENDESK_SERVICE_NAME",
        subdomain="ZENDESK_SUBDOMAIN",
        spam_control={"contents": "QUESTION"},
        sender={
            "email_address": "test@example.com",
            "country_code": "",
            "ip_address": None,
        },
    )
    mock_zendesk_form_action_class().save.assert_called_with(
        {
            "aaa_question": "QUESTION",
            "company_name": "Organisationname",
            "company_post_code": "SW1A 2BL",
            "company_registration_number": "12345678",
            "company_turnover": "Below £85,000",
            "company_type": "Charity / Social enterprise",
            "company_type_category": "Other type of UK organisation",
            "markets": "Germany, France, The Gambia",
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            # noqa: E501
            "how_did_you_hear_about_this_service": "Search engine",
            "marketing_consent": False,
            "have_you_exported_before": "No",
            "do_you_have_a_product_you_want_to_export": "Yes",
            "positivity_for_growth": "Neutral",
            "_custom_fields": [
                {
                    "222": [
                        EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                        EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
                    ]
                },
                {
                    "333": [
                        "germany__ess_export",
                        "france__ess_export",
                        "the_gambia__ess_export",
                    ],
                },
                {"444": "12345678"},
                {"666": "SW1A 2BL"},
                {"555": OrganisationTypeChoices.CHARITY_OR_SOCIAL_ENTERPRISE},
                {"111": CompanyTurnoverChoices.BELOW_85000},
            ],
        }
    )


@pytest.mark.django_db
def test_full_steps_solo_exporter_business_type_wizard_success_custom_fields(
    client, settings, mocker
):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {
        "company_turnover": "111",
        "enquiry_subject": "222",
        "markets": "333",
        "company_registration_number": "444",
        "company_type": "555",
        "company_post_code": "666",
        "number_of_employees": "777",
    }

    mock_zendesk_form_action_class = mocker.patch(
        "export_support.core.forms.ZendeskForm.action_class"
    )

    wizard_start_url = reverse("core:enquiry-wizard")
    response = client.get(wizard_start_url)
    assert response.status_code == 302

    enquiry_subject_url = get_step_url("enquiry-subject")
    assert response.url == enquiry_subject_url

    response = client.get(enquiry_subject_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_subject_wizard_step.html")
    response = client.post(
        enquiry_subject_url,
        get_form_data(
            "enquiry-subject",
            {
                "enquiry_subject": [
                    EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                    EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
                ]
            },
        ),
    )
    assert response.status_code == 302

    export_markets_url = get_step_url("export-markets")
    assert response.url == export_markets_url

    response = client.get(export_markets_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/export_markets_wizard_step.html")
    response = client.post(
        export_markets_url,
        get_form_data(
            "export-markets",
            {"markets": ["congo__ess_export", "cuba__ess_export"]},
        ),
    )
    assert response.status_code == 302

    personal_details_url = get_step_url("personal-details")
    assert response.url == personal_details_url

    response = client.get(personal_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/personal_details_wizard_step.html")
    response = client.post(
        personal_details_url,
        get_form_data(
            "personal-details",
            {
                "first_name": "Firstname",
                "last_name": "Lastname",
                "email": "test@example.com",
                "on_behalf_of": OnBehalfOfChoices.OWN_COMPANY,
            },
        ),
    )
    assert response.status_code == 302

    business_type_url = get_step_url("business-type")
    assert response.url == business_type_url

    response = client.get(business_type_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/business_type_wizard_step.html")
    response = client.post(
        business_type_url,
        get_form_data(
            "business-type",
            {
                "business_type": BusinessTypeChoices.SOLE_TRADE_OR_PRIVATE_INDIVIDUAL,
            },
        ),
    )
    assert response.status_code == 302

    solo_exporter_details_url = get_step_url("solo-exporter-details")
    assert response.url == solo_exporter_details_url

    response = client.get(solo_exporter_details_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=5, total_number_of_steps=8)
    assertTemplateUsed(response, "core/solo_exporter_details_wizard_step.html")
    response = client.post(
        solo_exporter_details_url,
        get_form_data(
            "solo-exporter-details",
            {
                "company_name": "Soloexporter",
                "company_post_code": "SW1A 2BL",
                "have_you_exported_before": HaveYouExportedBeforeChoices.NO,
                "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
            },
        ),
    )
    assert response.status_code == 302

    solo_exporter_additional_information_url = get_step_url(
        "solo-exporter-additional-information"
    )
    assert response.url == solo_exporter_additional_information_url

    response = client.get(solo_exporter_additional_information_url)
    assert response.status_code == 200
    assert_number_of_steps(response, current_step_number=6, total_number_of_steps=8)
    assertTemplateUsed(
        response, "core/solo_exporter_additional_information_wizard_step.html"
    )
    response = client.post(
        solo_exporter_additional_information_url,
        get_form_data(
            "solo-exporter-additional-information",
            {
                "company_type": SoloExporterTypeChoices.SOLE_TRADER,
                "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
            },
        ),
    )
    assert response.status_code == 302

    sectors_url = get_step_url("sectors")
    assert response.url == sectors_url

    response = client.get(sectors_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/sectors_wizard_step.html")
    response = client.post(
        sectors_url,
        get_form_data(
            "sectors",
            {
                "sectors": [sector for sector in SECTORS_MAP.keys()],
                "other": "ANOTHER SECTOR",
            },
        ),
    )
    assert response.status_code == 302

    enquiry_details_url = get_step_url("enquiry-details")
    assert response.url == enquiry_details_url

    response = client.get(enquiry_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_details_wizard_step.html")
    response = client.post(
        enquiry_details_url,
        get_form_data(
            "enquiry-details",
            {
                "nature_of_enquiry": "NATURE OF ENQUIRY",
                "question": "QUESTION",
                "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
            },
        ),
    )
    assert response.status_code == 302

    done_url = get_step_url("done")
    assert response.url == done_url

    response = client.get(done_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_contact_success.html")

    mock_zendesk_form_action_class.assert_called_with(
        form_url="FORM_URL",
        full_name="Firstname Lastname",
        email_address="test@example.com",
        subject="NATURE OF ENQUIRY",
        service_name="ZENDESK_SERVICE_NAME",
        subdomain="ZENDESK_SUBDOMAIN",
        spam_control={"contents": "QUESTION"},
        sender={
            "email_address": "test@example.com",
            "country_code": "",
            "ip_address": None,
        },
    )
    mock_zendesk_form_action_class().save.assert_called_with(
        {
            "aaa_question": "QUESTION",
            "company_name": "Soloexporter",
            "company_post_code": "SW1A 2BL",
            "company_registration_number": "",
            "company_turnover": "Below £85,000",
            "company_type": "Sole trader",
            "company_type_category": "Sole trader or private individual",
            "markets": "Congo, Cuba",
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            # noqa: E501
            "how_did_you_hear_about_this_service": "Search engine",
            "have_you_exported_before": "No",
            "do_you_have_a_product_you_want_to_export": "Yes",
            "positivity_for_growth": "Neutral",
            "marketing_consent": False,
            "_custom_fields": [
                {
                    "222": [
                        EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                        EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
                    ]
                },
                {
                    "333": [
                        "congo__ess_export",
                        "cuba__ess_export",
                    ]
                },
                {"666": "SW1A 2BL"},
                {"555": SoloExporterTypeChoices.SOLE_TRADER},
                {"111": CompanyTurnoverChoices.BELOW_85000},
                {"777": NumberOfEmployeesChoices.FEWER_THAN_10},
            ],
        }
    )


@pytest.mark.django_db
def test_full_steps_wizard_success_private_custom_fields_are_ignored(
    client, settings, mocker
):
    # In this case a "private" custom field is one that begins and ends with double underscores.
    # These are values that don't match up to a tag in Zendesk so shouldn't be sent through.
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {
        "company_type": "111",
        "company_turnover": "222",
    }

    mock_zendesk_form_action_class = mocker.patch(
        "export_support.core.forms.ZendeskForm.action_class"
    )

    wizard_start_url = reverse("core:enquiry-wizard")
    response = client.get(wizard_start_url)
    assert response.status_code == 302

    enquiry_subject_url = get_step_url("enquiry-subject")
    assert response.url == enquiry_subject_url

    response = client.get(enquiry_subject_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_subject_wizard_step.html")
    response = client.post(
        enquiry_subject_url,
        get_form_data(
            "enquiry-subject",
            {
                "enquiry_subject": [
                    EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                    EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
                ]
            },
        ),
    )
    assert response.status_code == 302

    export_markets_url = get_step_url("export-markets")
    assert response.url == export_markets_url

    response = client.get(export_markets_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/export_markets_wizard_step.html")
    response = client.post(
        export_markets_url,
        get_form_data(
            "export-markets",
            {"markets": ["andorra__ess_export", "australia__ess_export"]},
        ),
    )
    assert response.status_code == 302

    personal_details_url = get_step_url("personal-details")
    assert response.url == personal_details_url

    response = client.get(personal_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/personal_details_wizard_step.html")
    response = client.post(
        personal_details_url,
        get_form_data(
            "personal-details",
            {
                "first_name": "Firstname",
                "last_name": "Lastname",
                "email": "test@example.com",
                "on_behalf_of": OnBehalfOfChoices.OWN_COMPANY,
            },
        ),
    )
    assert response.status_code == 302

    business_type_url = get_step_url("business-type")
    assert response.url == business_type_url

    response = client.get(business_type_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/business_type_wizard_step.html")
    response = client.post(
        business_type_url,
        get_form_data(
            "business-type",
            {
                "business_type": BusinessTypeChoices.PRIVATE_OR_LIMITED,
            },
        ),
    )
    assert response.status_code == 302

    business_details_url = get_step_url("business-details")
    assert response.url == business_details_url

    response = client.get(business_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/business_details_wizard_step.html")
    response = client.post(
        business_details_url,
        get_form_data(
            "business-details",
            {
                "company_name": "Companyname",
                "company_post_code": "SW1A 2BL",
                "company_registration_number": "12345678",
                "have_you_exported_before": HaveYouExportedBeforeChoices.NO,
                "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
            },
        ),
    )
    assert response.status_code == 302

    business_additional_information_url = get_step_url(
        "business-additional-information"
    )
    assert response.url == business_additional_information_url

    response = client.get(business_additional_information_url)
    assert response.status_code == 200
    assertTemplateUsed(
        response, "core/business_additional_information_wizard_step.html"
    )
    response = client.post(
        business_additional_information_url,
        get_form_data(
            "business-additional-information",
            {
                "company_type": PrivateOrPublicCompanyTypeChoices.OTHER,
                "other_type_of_business": "Othertypeofbusiness",
                "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
                "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
            },
        ),
    )
    assert response.status_code == 302

    sectors_url = get_step_url("sectors")
    assert response.url == sectors_url

    response = client.get(sectors_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/sectors_wizard_step.html")
    response = client.post(
        sectors_url,
        get_form_data(
            "sectors",
            {
                "sectors": [sector for sector in SECTORS_MAP.keys()],
                "other": "ANOTHER SECTOR",
            },
        ),
    )
    assert response.status_code == 302

    enquiry_details_url = get_step_url("enquiry-details")
    assert response.url == enquiry_details_url

    response = client.get(enquiry_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_details_wizard_step.html")
    response = client.post(
        enquiry_details_url,
        get_form_data(
            "enquiry-details",
            {
                "nature_of_enquiry": "NATURE OF ENQUIRY",
                "question": "QUESTION",
                "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
            },
        ),
    )
    assert response.status_code == 302

    done_url = get_step_url("done")
    assert response.url == done_url

    response = client.get(done_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_contact_success.html")

    mock_zendesk_form_action_class.assert_called_with(
        form_url="FORM_URL",
        full_name="Firstname Lastname",
        email_address="test@example.com",
        subject="NATURE OF ENQUIRY",
        service_name="ZENDESK_SERVICE_NAME",
        subdomain="ZENDESK_SUBDOMAIN",
        spam_control={"contents": "QUESTION"},
        sender={
            "email_address": "test@example.com",
            "country_code": "",
            "ip_address": None,
        },
    )
    mock_zendesk_form_action_class().save.assert_called_with(
        {
            "aaa_question": "QUESTION",
            "company_name": "Companyname",
            "company_post_code": "SW1A 2BL",
            "company_registration_number": "12345678",
            "company_turnover": "Below £85,000",
            "company_type": "Othertypeofbusiness",
            "company_type_category": "UK private or public limited company",
            "markets": "Andorra, Australia",
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "have_you_exported_before": "No",
            "do_you_have_a_product_you_want_to_export": "Yes",
            "positivity_for_growth": "Neutral",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            # noqa: E501
            "how_did_you_hear_about_this_service": "Search engine",
            "marketing_consent": False,
            "_custom_fields": [
                {"222": CompanyTurnoverChoices.BELOW_85000},
            ],
        }
    )


def test_zendesk_form_is_not_valid_wizard_raises_error(client, settings, mocker):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {}

    mock_zendesk_form_action_class = mocker.patch(
        "export_support.core.forms.ZendeskForm.action_class"
    )
    mock_zendesk_form_is_valid = mocker.patch(
        "export_support.core.forms.ZendeskForm.is_valid"
    )
    mock_zendesk_form_is_valid.return_value = False

    wizard_start_url = reverse("core:enquiry-wizard")
    response = client.get(wizard_start_url)
    assert response.status_code == 302

    enquiry_subject_url = get_step_url("enquiry-subject")
    assert response.url == enquiry_subject_url

    response = client.get(enquiry_subject_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_subject_wizard_step.html")
    response = client.post(
        enquiry_subject_url,
        get_form_data(
            "enquiry-subject",
            {
                "enquiry_subject": [
                    EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                    EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
                ]
            },
        ),
    )
    assert response.status_code == 302

    export_markets_url = get_step_url("export-markets")
    assert response.url == export_markets_url

    response = client.get(export_markets_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/export_markets_wizard_step.html")
    response = client.post(
        export_markets_url,
        get_form_data(
            "export-markets",
            {"markets": MARKET_MACHINE_READABLE_VALUES},
        ),
    )
    assert response.status_code == 302

    personal_details_url = get_step_url("personal-details")
    assert response.url == personal_details_url

    response = client.get(personal_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/personal_details_wizard_step.html")
    response = client.post(
        personal_details_url,
        get_form_data(
            "personal-details",
            {
                "first_name": "Firstname",
                "last_name": "Lastname",
                "email": "test@example.com",
                "on_behalf_of": OnBehalfOfChoices.OWN_COMPANY,
            },
        ),
    )
    assert response.status_code == 302

    business_type_url = get_step_url("business-type")
    assert response.url == business_type_url

    response = client.get(business_type_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/business_type_wizard_step.html")
    response = client.post(
        business_type_url,
        get_form_data(
            "business-type",
            {
                "business_type": BusinessTypeChoices.PRIVATE_OR_LIMITED,
            },
        ),
    )
    assert response.status_code == 302

    business_details_url = get_step_url("business-details")
    assert response.url == business_details_url

    response = client.get(business_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/business_details_wizard_step.html")
    response = client.post(
        business_details_url,
        get_form_data(
            "business-details",
            {
                "company_name": "Companyname",
                "company_post_code": "SW1A 2BL",
                "company_registration_number": "12345678",
                "have_you_exported_before": HaveYouExportedBeforeChoices.NO,
                "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
            },
        ),
    )
    assert response.status_code == 302

    business_additional_information_url = get_step_url(
        "business-additional-information"
    )
    assert response.url == business_additional_information_url

    response = client.get(business_additional_information_url)
    assert response.status_code == 200
    assertTemplateUsed(
        response, "core/business_additional_information_wizard_step.html"
    )
    response = client.post(
        business_additional_information_url,
        get_form_data(
            "business-additional-information",
            {
                "company_type": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
                "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
                "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
            },
        ),
    )
    assert response.status_code == 302

    sectors_url = get_step_url("sectors")
    assert response.url == sectors_url

    response = client.get(sectors_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/sectors_wizard_step.html")
    response = client.post(
        sectors_url,
        get_form_data(
            "sectors",
            {
                "sectors": [sector for sector in SECTORS_MAP.keys()],
                "other": "ANOTHER SECTOR",
            },
        ),
    )
    assert response.status_code == 302

    enquiry_details_url = get_step_url("enquiry-details")
    assert response.url == enquiry_details_url

    response = client.get(enquiry_details_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_details_wizard_step.html")
    response = client.post(
        enquiry_details_url,
        get_form_data(
            "enquiry-details",
            {
                "nature_of_enquiry": "NATURE OF ENQUIRY",
                "question": "QUESTION",
                "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
            },
        ),
    )
    assert response.status_code == 302

    done_url = get_step_url("done")
    assert response.url == done_url

    with pytest.raises(ValueError):
        response = client.get(done_url)

    mock_zendesk_form_is_valid.assert_called()
    mock_zendesk_form_action_class.assert_not_called()
    mock_zendesk_form_action_class().save.assert_not_called()


@pytest.fixture
def run_wizard_enquiry_subject(settings, mocker):
    def run(enquiry_subject):
        client = Client()

        settings.FORM_URL = "FORM_URL"
        settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
        settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"

        mocker.patch("export_support.core.forms.ZendeskForm.action_class")

        wizard_start_url = reverse("core:enquiry-wizard")
        response = client.get(wizard_start_url)
        assert response.status_code == 302

        enquiry_subject_url = get_step_url("enquiry-subject")
        assert response.url == enquiry_subject_url

        response = client.get(enquiry_subject_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/enquiry_subject_wizard_step.html")
        response = client.post(
            enquiry_subject_url,
            get_form_data(
                "enquiry-subject",
                {"enquiry_subject": enquiry_subject},
            ),
        )
        assert response.status_code == 302

        export_markets_url = get_step_url("export-markets")
        assert response.url == export_markets_url

        response = client.get(export_markets_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/export_markets_wizard_step.html")
        response = client.post(
            export_markets_url,
            get_form_data(
                "export-markets",
                {"markets": MARKET_MACHINE_READABLE_VALUES},
            ),
        )
        assert response.status_code == 302

        personal_details_url = get_step_url("personal-details")
        assert response.url == personal_details_url

        response = client.get(personal_details_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/personal_details_wizard_step.html")
        response = client.post(
            personal_details_url,
            get_form_data(
                "personal-details",
                {
                    "first_name": "Firstname",
                    "last_name": "Lastname",
                    "email": "test@example.com",
                    "on_behalf_of": "1",
                },
            ),
        )
        assert response.status_code == 302

        business_type_url = get_step_url("business-type")
        assert response.url == business_type_url

        response = client.get(business_type_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/business_type_wizard_step.html")
        response = client.post(
            business_type_url,
            get_form_data(
                "business-type",
                {
                    "business_type": BusinessTypeChoices.PRIVATE_OR_LIMITED,
                },
            ),
        )
        assert response.status_code == 302

        business_details_url = get_step_url("business-details")
        assert response.url == business_details_url

        response = client.get(business_details_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/business_details_wizard_step.html")
        response = client.post(
            business_details_url,
            get_form_data(
                "business-details",
                {
                    "company_name": "Companyname",
                    "company_post_code": "SW1A 2BL",
                    "company_registration_number": "12345678",
                    "have_you_exported_before": HaveYouExportedBeforeChoices.NO,
                    "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
                },
            ),
        )
        assert response.status_code == 302

        business_additional_information_url = get_step_url(
            "business-additional-information"
        )
        assert response.url == business_additional_information_url

        response = client.get(business_additional_information_url)
        assert response.status_code == 200
        assertTemplateUsed(
            response, "core/business_additional_information_wizard_step.html"
        )
        response = client.post(
            business_additional_information_url,
            get_form_data(
                "business-additional-information",
                {
                    "company_type": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
                    "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                    "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
                    "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
                },
            ),
        )
        assert response.status_code == 302

        sectors_url = get_step_url("sectors")
        assert response.url == sectors_url

        response = client.get(sectors_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/sectors_wizard_step.html")
        response = client.post(
            sectors_url,
            get_form_data(
                "sectors",
                {
                    "sectors": [sector for sector in SECTORS_MAP.keys()],
                    "other": "ANOTHER SECTOR",
                },
            ),
        )
        assert response.status_code == 302

        enquiry_details_url = get_step_url("enquiry-details")
        assert response.url == enquiry_details_url

        response = client.get(enquiry_details_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/enquiry_details_wizard_step.html")
        response = client.post(
            enquiry_details_url,
            get_form_data(
                "enquiry-details",
                {
                    "nature_of_enquiry": "NATURE OF ENQUIRY",
                    "question": "QUESTION",
                    "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
                },
            ),
        )
        assert response.status_code == 302

        done_url = get_step_url("done")
        assert response.url == done_url

        response = client.get(done_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/enquiry_contact_success.html")

        return response

    return run


@pytest.mark.django_db
def test_enquiry_subject_choices_context_data(run_wizard_enquiry_subject):
    response = run_wizard_enquiry_subject([EnquirySubjectChoices.SELLING_GOODS_ABROAD])
    ctx = response.context
    assert ctx["display_goods"]
    assert not ctx["display_services"]
    assert not ctx["display_subheadings"]

    response = run_wizard_enquiry_subject(
        [EnquirySubjectChoices.SELLING_SERVICES_ABROAD]
    )
    ctx = response.context
    assert not ctx["display_goods"]
    assert ctx["display_services"]
    assert not ctx["display_subheadings"]

    response = run_wizard_enquiry_subject(
        [
            EnquirySubjectChoices.SELLING_GOODS_ABROAD,
            EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
        ]
    )
    ctx = response.context
    assert ctx["display_goods"]
    assert ctx["display_services"]
    assert ctx["display_subheadings"]


@pytest.fixture
def run_wizard_enquiry_subject_guidance_url():
    def run(enquiry_subject):
        client = Client()

        wizard_start_url = reverse("core:enquiry-wizard")
        response = client.get(wizard_start_url)
        assert response.status_code == 302

        enquiry_subject_url = get_step_url("enquiry-subject")
        assert response.url == enquiry_subject_url

        response = client.get(enquiry_subject_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/enquiry_subject_wizard_step.html")
        response = client.post(
            enquiry_subject_url,
            get_form_data(
                "enquiry-subject",
                {"enquiry_subject": enquiry_subject},
            ),
        )
        assert response.status_code == 302

        export_markets_url = get_step_url("export-markets")
        assert response.url == export_markets_url

        response = client.get(export_markets_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/export_markets_wizard_step.html")

        return response

    return run


def test_enquiry_subject_guidance_url(run_wizard_enquiry_subject_guidance_url, mocker):
    response = run_wizard_enquiry_subject_guidance_url(
        [EnquirySubjectChoices.SELLING_GOODS_ABROAD]
    )
    ctx = response.context
    assert (
        ctx["guidance_url"]
        == f"{reverse('core:not-listed-market-export-enquiries')}?enquiry_subject=1"
    )

    response = run_wizard_enquiry_subject_guidance_url(
        [EnquirySubjectChoices.SELLING_SERVICES_ABROAD]
    )
    ctx = response.context
    assert (
        ctx["guidance_url"]
        == f"{reverse('core:not-listed-market-export-enquiries')}?enquiry_subject=2"
    )

    response = run_wizard_enquiry_subject_guidance_url(
        [
            EnquirySubjectChoices.SELLING_GOODS_ABROAD,
            EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
        ]
    )
    ctx = response.context
    assert (
        ctx["guidance_url"]
        == f"{reverse('core:not-listed-market-export-enquiries')}?enquiry_subject=1&enquiry_subject=2"
    )

    client = Client()

    wizard_start_url = reverse("core:enquiry-wizard")
    response = client.get(wizard_start_url)
    assert response.status_code == 302

    enquiry_subject_url = get_step_url("enquiry-subject")
    assert response.url == enquiry_subject_url

    response = client.get(enquiry_subject_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_subject_wizard_step.html")
    response = client.post(
        enquiry_subject_url,
        get_form_data(
            "enquiry-subject",
            {"enquiry_subject": [EnquirySubjectChoices.SELLING_GOODS_ABROAD]},
        ),
    )
    assert response.status_code == 302

    export_markets_url = get_step_url("export-markets")
    assert response.url == export_markets_url

    mock_is_valid = mocker.patch(
        "export_support.core.views.EnquirySubjectForm.is_valid"
    )
    mock_is_valid.return_value = False
    response = client.get(export_markets_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/export_markets_wizard_step.html")

    ctx = response.context
    assert (
        ctx["guidance_url"] == f"{reverse('core:not-listed-market-export-enquiries')}?"
    )
