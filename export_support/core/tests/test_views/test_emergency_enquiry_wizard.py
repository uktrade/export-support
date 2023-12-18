import logging

import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

logger = logging.getLogger(__name__)


def test_page_load_russia_ukraine(client):
    response = client.get(
        reverse(
            "core:ru-emergency-situation-wizard-step", kwargs={"step": "enquiry-form"}
        )
    )
    assert response.status_code == 200
    assertTemplateUsed(response, "core/emergency_enquiry_form_wizard_step.html")


def test_submit_russia_ukraine_form(client, settings, mocker):

    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {
        "company_name": "111",
        "company_post_code": "222",
        "sectors": "333",
    }

    mock_zendesk_form = mocker.patch(
        "export_support.core.forms.EmergencySituationZendeskForm.action_class"
    )

    response = client.post(
        reverse(
            "core:ru-emergency-situation-wizard-step", kwargs={"step": "enquiry-form"}
        ),
        {
            "emergency_situation_enquiry_wizard_view-current_step": "enquiry-form",
            "enquiry-form-full_name": "Jimmy Space",
            "enquiry-form-email": "jimmy.space@test.com",
            "enquiry-form-phone": "07786179011",
            "enquiry-form-company_name": "Golden Throne Inc.",
            "enquiry-form-company_post_code": "te51aa",
            "enquiry-form-sectors": [
                "advanced_engineering__ess_sector_l1",
                "chemicals__ess_sector_l1",
                "logistics__ess_sector_l1",
            ],
            "enquiry-form-other": "",
            "enquiry-form-question": "I have a question",
        },
    )

    assert response.status_code == 302
    assert response.url == "/russia-ukraine/done"

    response = client.get(
        reverse("core:ru-emergency-situation-wizard-step", kwargs={"step": "done"})
    )
    assert response.status_code == 200

    mock_zendesk_form.assert_called_with(
        form_url="FORM_URL",
        full_name="Jimmy Space",
        email_address="jimmy.space@test.com",
        subject="Russia/Ukraine Enquiry",
        service_name="ZENDESK_SERVICE_NAME",
        subdomain="ZENDESK_SUBDOMAIN",
        spam_control={"contents": "I have a question"},
        sender={
            "email_address": "jimmy.space@test.com",
            "country_code": "",
            "ip_address": None,
        },
    )
    mock_zendesk_form().save.assert_any_call(
        {
            "enquiry_subject": "Russia/Ukraine Enquiry",
            "markets": "Russia, Ukraine",
            "on_behalf_of": "-",
            "company_type": "-",
            "company_type_category": "-",
            "company_name": "Golden Throne Inc.",
            "company_post_code": "te51aa",
            "company_registration_number": "",
            "company_turnover": "",
            "number_of_employees": "",
            "sectors": "Advanced engineering, Chemicals, Logistics",
            "other_sector": "",
            "nature_of_enquiry": "",
            "aaa_question": "I have a question",
            "full_name": "Jimmy Space",
            "email": "jimmy.space@test.com",
            "how_did_you_hear_about_this_service": "-",
            "marketing_consent": False,
            "phone": "07786179011",
            "_custom_fields": [
                {"111": "Golden Throne Inc."},
                {"222": "te51aa"},
                {
                    "333": [
                        "advanced_engineering__ess_sector_l1",
                        "chemicals__ess_sector_l1",
                        "logistics__ess_sector_l1",
                    ]
                },
            ],
        }
    )


def test_page_load_israel_palestine(client):
    response = client.get(
        reverse(
            "core:ip-emergency-situation-wizard-step", kwargs={"step": "enquiry-form"}
        )
    )
    assert response.status_code == 200
    assertTemplateUsed(response, "core/emergency_enquiry_form_wizard_step.html")


def test_submit_israel_palestine_form(client, settings, mocker):

    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"
    settings.ZENDESK_CUSTOM_FIELD_MAPPING = {
        "company_name": "111",
        "company_post_code": "222",
        "sectors": "333",
    }

    mock_zendesk_form = mocker.patch(
        "export_support.core.forms.EmergencySituationZendeskForm.action_class"
    )

    response = client.post(
        reverse(
            "core:ip-emergency-situation-wizard-step", kwargs={"step": "enquiry-form"}
        ),
        {
            "emergency_situation_enquiry_wizard_view-current_step": "enquiry-form",
            "enquiry-form-full_name": "Jimmy Space",
            "enquiry-form-email": "jimmy.space@test.com",
            "enquiry-form-phone": "07786179011",
            "enquiry-form-company_name": "Golden Throne Inc.",
            "enquiry-form-company_post_code": "te51aa",
            "enquiry-form-sectors": [
                "advanced_engineering__ess_sector_l1",
                "chemicals__ess_sector_l1",
                "logistics__ess_sector_l1",
            ],
            "enquiry-form-other": "",
            "enquiry-form-question": "I have a question",
        },
    )

    assert response.status_code == 302
    assert response.url == "/israel-palestine/done"

    response = client.get(
        reverse("core:ip-emergency-situation-wizard-step", kwargs={"step": "done"})
    )
    assert response.status_code == 200

    mock_zendesk_form.assert_called_with(
        form_url="FORM_URL",
        full_name="Jimmy Space",
        email_address="jimmy.space@test.com",
        subject="Israel/Palestine Enquiry",
        service_name="ZENDESK_SERVICE_NAME",
        subdomain="ZENDESK_SUBDOMAIN",
        spam_control={"contents": "I have a question"},
        sender={
            "email_address": "jimmy.space@test.com",
            "country_code": "",
            "ip_address": None,
        },
    )
    mock_zendesk_form().save.assert_any_call(
        {
            "enquiry_subject": "Israel/Palestine Enquiry",
            "markets": "Israel, Occupied Palestinian Territories",
            "on_behalf_of": "-",
            "company_type": "-",
            "company_type_category": "-",
            "company_name": "Golden Throne Inc.",
            "company_post_code": "te51aa",
            "company_registration_number": "",
            "company_turnover": "",
            "number_of_employees": "",
            "sectors": "Advanced engineering, Chemicals, Logistics",
            "other_sector": "",
            "nature_of_enquiry": "",
            "aaa_question": "I have a question",
            "full_name": "Jimmy Space",
            "email": "jimmy.space@test.com",
            "how_did_you_hear_about_this_service": "-",
            "marketing_consent": False,
            "phone": "07786179011",
            "_custom_fields": [
                {"111": "Golden Throne Inc."},
                {"222": "te51aa"},
                {
                    "333": [
                        "advanced_engineering__ess_sector_l1",
                        "chemicals__ess_sector_l1",
                        "logistics__ess_sector_l1",
                    ]
                },
            ],
        }
    )


def test_zendesk_form_invalid(client, settings, mocker):

    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"

    mock_zendesk_form = mocker.patch(
        "export_support.core.forms.EmergencySituationZendeskForm.action_class"
    )

    mock_zendesk_form_is_valid = mocker.patch(
        "export_support.core.forms.EmergencySituationZendeskForm.is_valid"
    )

    mock_zendesk_form_is_valid.return_value = False

    response = client.post(
        reverse(
            "core:ip-emergency-situation-wizard-step", kwargs={"step": "enquiry-form"}
        ),
        {
            "emergency_situation_enquiry_wizard_view-current_step": "enquiry-form",
            "enquiry-form-full_name": "Jimmy Space",
            "enquiry-form-email": "jimmy.space@test.com",
            "enquiry-form-phone": "07786179011",
            "enquiry-form-company_name": "Golden Throne Inc.",
            "enquiry-form-company_post_code": "te51aa",
            "enquiry-form-sectors": [
                "advanced_engineering__ess_sector_l1",
                "chemicals__ess_sector_l1",
                "logistics__ess_sector_l1",
            ],
            "enquiry-form-other": "",
            "enquiry-form-question": "I have a question",
        },
    )

    assert response.status_code == 302
    assert response.url == "/israel-palestine/done"

    with pytest.raises(ValueError):
        response = client.get(
            reverse("core:ip-emergency-situation-wizard-step", kwargs={"step": "done"})
        )

    mock_zendesk_form_is_valid.assert_called()
    mock_zendesk_form.assert_not_called()
    mock_zendesk_form().save.assert_not_called()
