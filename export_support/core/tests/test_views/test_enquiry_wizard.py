from enum import Enum

import pytest
import requests_mock
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from ...consts import ENQUIRY_COUNTRY_CODES
from ...forms import (
    SECTORS_MAP,
    BusinessTypeChoices,
    CompanyTurnoverChoices,
    EnquirySubjectChoices,
    HowDidYouHearAboutThisServiceChoices,
    NumberOfEmployeesChoices,
    OnBehalfOfChoices,
    PrivateOrPublicCompanyTypeChoices,
)

COUNTRY_MACHINE_READABLE_VALUES = list(ENQUIRY_COUNTRY_CODES.values())


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


def test_full_steps_wizard_success(client, settings, mocker):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {}
    settings.CONSENT_API_URL = "http://placeholder:8080/api/v1/person/"
    settings.CONSENT_API_METHOD = "POST"

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

    export_countries_url = get_step_url("export-countries")
    assert response.url == export_countries_url

    response = client.get(export_countries_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/export_countries_wizard_step.html")
    response = client.post(
        export_countries_url,
        get_form_data(
            "export-countries",
            {"countries": COUNTRY_MACHINE_READABLE_VALUES},
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
                "type_of_business": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
                "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
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
                "email_consent": True,
            },
        ),
    )
    assert response.status_code == 302

    done_url = get_step_url("done")
    assert response.url == done_url

    with requests_mock.mock() as m:
        # Mock the post request to the consent api
        adapter = m.post("http://placeholder:8080/api/v1/person/")
        response = client.get(done_url)

    assert response.status_code == 200
    assertTemplateUsed(response, "core/enquiry_contact_success.html")

    # Check the contents of the request to the consent api
    consent_request_content = adapter.last_request.json()
    assert consent_request_content["consents"] == ["email_marketing"]
    assert consent_request_content["email"] == "test@example.com"
    assert consent_request_content["key_type"] == "email"

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
            "countries": "Albania, Andorra, Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Kosovo, Latvia, Liechtenstein, Lithuania, Luxembourg, Malta, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, San Marino, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Vatican City",  # noqa: E501
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            "type_of_business": "Private limited company",
            "how_did_you_hear_about_this_service": "Search engine",
            "_custom_fields": None,
        }
    )


def test_full_steps_wizard_success_custom_fields(client, settings, mocker):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {
        "company_turnover": "111",
        "enquiry_subject": "222",
        "countries": "333",
        "company_registration_number": "444",
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

    export_countries_url = get_step_url("export-countries")
    assert response.url == export_countries_url

    response = client.get(export_countries_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/export_countries_wizard_step.html")
    response = client.post(
        export_countries_url,
        get_form_data(
            "export-countries",
            {"countries": COUNTRY_MACHINE_READABLE_VALUES},
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
                "type_of_business": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
                "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
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
            "countries": "Albania, Andorra, Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Kosovo, Latvia, Liechtenstein, Lithuania, Luxembourg, Malta, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, San Marino, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Vatican City",  # noqa: E501
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            "type_of_business": "Private limited company",
            "how_did_you_hear_about_this_service": "Search engine",
            "_custom_fields": [
                {
                    "222": [
                        EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                        EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
                    ]
                },
                {
                    "333": [
                        "albania__ess_export",
                        "andorra__ess_export",
                        "austria__ess_export",
                        "belgium__ess_export",
                        "bosnia_and_herzegovina__ess_export",
                        "bulgaria__ess_export",
                        "croatia__ess_export",
                        "cyprus__ess_export",
                        "czechia__ess_export",
                        "denmark__ess_export",
                        "estonia__ess_export",
                        "finland__ess_export",
                        "france__ess_export",
                        "germany__ess_export",
                        "greece__ess_export",
                        "hungary__ess_export",
                        "iceland__ess_export",
                        "ireland__ess_export",
                        "israel__ess_export",
                        "italy__ess_export",
                        "kosovo__ess_export",
                        "latvia__ess_export",
                        "liechtenstein__ess_export",
                        "lithuania__ess_export",
                        "luxembourg__ess_export",
                        "malta__ess_export",
                        "monaco__ess_export",
                        "montenegro__ess_export",
                        "netherland__ess_export",
                        "north_macedonia__ess_export",
                        "norway__ess_export",
                        "poland__ess_export",
                        "portugal__ess_export",
                        "romania__ess_export",
                        "san_marino__ess_export",
                        "serbia__ess_export",
                        "slovakia__ess_export",
                        "slovenia__ess_export",
                        "spain__ess_export",
                        "sweden__ess_export",
                        "switzerland__ess_export",
                        "turkey__ess_export",
                        "vatican_city__ess_export",
                    ]
                },
                {"444": "12345678"},
                {"111": CompanyTurnoverChoices.BELOW_85000},
            ],
        }
    )


def test_zendesk_form_is_not_valid_wizard_raises_error(client, settings, mocker):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {}
    settings.CONSENT_API_URL = "http://placeholder:8080/api/v1/person/"
    settings.CONSENT_API_METHOD = "POST"

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

    export_countries_url = get_step_url("export-countries")
    assert response.url == export_countries_url

    response = client.get(export_countries_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/export_countries_wizard_step.html")
    response = client.post(
        export_countries_url,
        get_form_data(
            "export-countries",
            {"countries": COUNTRY_MACHINE_READABLE_VALUES},
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
                "type_of_business": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
                "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
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

        export_countries_url = get_step_url("export-countries")
        assert response.url == export_countries_url

        response = client.get(export_countries_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/export_countries_wizard_step.html")
        response = client.post(
            export_countries_url,
            get_form_data(
                "export-countries",
                {"countries": COUNTRY_MACHINE_READABLE_VALUES},
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
                    "type_of_business": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
                    "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                    "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
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

        export_countries_url = get_step_url("export-countries")
        assert response.url == export_countries_url

        response = client.get(export_countries_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/export_countries_wizard_step.html")

        return response

    return run


def test_enquiry_subject_guidance_url(run_wizard_enquiry_subject_guidance_url, mocker):
    response = run_wizard_enquiry_subject_guidance_url(
        [EnquirySubjectChoices.SELLING_GOODS_ABROAD]
    )
    ctx = response.context
    assert (
        ctx["guidance_url"]
        == f"{reverse('core:non-eu-export-enquiries')}?enquiry_subject=1"
    )

    response = run_wizard_enquiry_subject_guidance_url(
        [EnquirySubjectChoices.SELLING_SERVICES_ABROAD]
    )
    ctx = response.context
    assert (
        ctx["guidance_url"]
        == f"{reverse('core:non-eu-export-enquiries')}?enquiry_subject=2"
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
        == f"{reverse('core:non-eu-export-enquiries')}?enquiry_subject=1&enquiry_subject=2"
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

    export_countries_url = get_step_url("export-countries")
    assert response.url == export_countries_url

    mock_is_valid = mocker.patch(
        "export_support.core.views.EnquirySubjectForm.is_valid"
    )
    mock_is_valid.return_value = False
    response = client.get(export_countries_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/export_countries_wizard_step.html")

    ctx = response.context
    assert ctx["guidance_url"] == f"{reverse('core:non-eu-export-enquiries')}?"


@pytest.fixture
def run_business_additional_information():
    def run(business_additional_information_form_data, client):
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

        export_countries_url = get_step_url("export-countries")
        assert response.url == export_countries_url

        response = client.get(export_countries_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/export_countries_wizard_step.html")
        response = client.post(
            export_countries_url,
            get_form_data(
                "export-countries",
                {"countries": COUNTRY_MACHINE_READABLE_VALUES},
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
                business_additional_information_form_data,
            ),
        )

        return response

    return run


@pytest.fixture
def run_business_additional_information_full(run_business_additional_information):
    def run(business_additional_information_form_data, client):
        response = run_business_additional_information(
            business_additional_information_form_data, client
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

        return response

    return run


def test_business_additional_information_type_of_business_other_zendesk_output(
    run_business_additional_information_full, settings, mocker
):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {}

    mock_zendesk_form_action_class = mocker.patch(
        "export_support.core.forms.ZendeskForm.action_class"
    )

    client = Client()
    run_business_additional_information_full(
        {
            "type_of_business": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
            "other_type_of_business": "This is ignored",
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
        },
        client=client,
    )

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
            "countries": "Albania, Andorra, Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Kosovo, Latvia, Liechtenstein, Lithuania, Luxembourg, Malta, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, San Marino, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Vatican City",  # noqa: E501
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            "type_of_business": "Private limited company",
            "how_did_you_hear_about_this_service": "Search engine",
            "_custom_fields": None,
        }
    )

    mock_zendesk_form_action_class.reset()
    mock_zendesk_form_action_class().save.reset()

    client = Client()
    run_business_additional_information_full(
        {
            "type_of_business": PrivateOrPublicCompanyTypeChoices.OTHER,
            "other_type_of_business": "Another business type",
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
        },
        client=client,
    )

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
            "countries": "Albania, Andorra, Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Kosovo, Latvia, Liechtenstein, Lithuania, Luxembourg, Malta, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, San Marino, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Vatican City",  # noqa: E501
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            "type_of_business": "Another business type",
            "how_did_you_hear_about_this_service": "Search engine",
            "_custom_fields": None,
        }
    )


@pytest.fixture
def run_wizard_enquiry_details():
    def run(enquiry_details_form_data, client):
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

        export_countries_url = get_step_url("export-countries")
        assert response.url == export_countries_url

        response = client.get(export_countries_url)
        assert response.status_code == 200
        assertTemplateUsed(response, "core/export_countries_wizard_step.html")
        response = client.post(
            export_countries_url,
            get_form_data(
                "export-countries",
                {"countries": COUNTRY_MACHINE_READABLE_VALUES},
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
                    "type_of_business": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
                    "company_turnover": CompanyTurnoverChoices.BELOW_85000,
                    "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
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
                enquiry_details_form_data,
            ),
        )

        return response

    return run


def test_enquiry_details_how_did_you_hear_other_zendesk_output(
    run_wizard_enquiry_details, settings, mocker
):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {}

    mock_zendesk_form_action_class = mocker.patch(
        "export_support.core.forms.ZendeskForm.action_class"
    )

    client = Client()
    response = run_wizard_enquiry_details(
        {
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "question": "QUESTION",
            "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
            "other_how_did_you_hear_about_this_service": "This is ignored",
        },
        client=client,
    )
    assert response.status_code == 302

    done_url = get_step_url("done")
    response = client.get(done_url)

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
            "countries": "Albania, Andorra, Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Kosovo, Latvia, Liechtenstein, Lithuania, Luxembourg, Malta, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, San Marino, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Vatican City",  # noqa: E501
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            "type_of_business": "Private limited company",
            "how_did_you_hear_about_this_service": "Search engine",
            "_custom_fields": None,
        }
    )

    mock_zendesk_form_action_class.reset()
    mock_zendesk_form_action_class().save.reset()

    client = Client()
    response = run_wizard_enquiry_details(
        {
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "question": "QUESTION",
            "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.OTHER,
            "other_how_did_you_hear_about_this_service": "Other service I heard this from",
        },
        client=client,
    )
    assert response.status_code == 302

    done_url = get_step_url("done")
    response = client.get(done_url)

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
            "countries": "Albania, Andorra, Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Kosovo, Latvia, Liechtenstein, Lithuania, Luxembourg, Malta, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, San Marino, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Vatican City",  # noqa: E501
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for (or in my own interest)",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",  # noqa: E501
            "type_of_business": "Private limited company",
            "how_did_you_hear_about_this_service": "Other service I heard this from",
            "_custom_fields": None,
        }
    )
