from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from ...consts import ENQUIRY_COUNTRY_CODES
from ...forms import SECTORS_MAP


def get_form_data(step_name, data):
    form_data = {
        "enquiry_wizard_view-current_step": step_name,
        **{
            f"{step_name}-{field_name}": field_value
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
            {"enquiry_subject": ["1", "2"]},
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
            {"countries": ENQUIRY_COUNTRY_CODES},
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
                "company_type": "1",
                "company_name": "Companyname",
                "company_post_code": "SW1A 2BL",
                "company_registration_number": "12345678",
            },
        ),
    )
    assert response.status_code == 302

    business_size_url = get_step_url("business-size")
    assert response.url == business_size_url

    response = client.get(business_size_url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/business_size_wizard_step.html")
    response = client.post(
        business_size_url,
        get_form_data(
            "business-size",
            {
                "company_turnover": "1",
                "number_of_employees": "1",
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
                "is_other": "1",
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
            "company_type": "UK private or public limited company",
            "countries": "Albania, Andorra, Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Kosovo, Latvia, Liechtenstein, Lithuania, Luxembourg, Malta, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, San Marino, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Vatican City",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",
        }
    )


def test_skip_business_details_wizard_success(client, settings, mocker):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"

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
            {"enquiry_subject": ["1", "2"]},
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
            {"countries": ENQUIRY_COUNTRY_CODES},
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
                "on_behalf_of": "3",
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
                "is_other": "1",
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
            "company_name": "",
            "company_post_code": "",
            "company_registration_number": "",
            "company_turnover": "",
            "company_type": "",
            "countries": "Albania, Andorra, Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Kosovo, Latvia, Liechtenstein, Lithuania, Luxembourg, Malta, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, San Marino, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Vatican City",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "",
            "on_behalf_of": "This enquiry does not relate to a business",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",
        }
    )
