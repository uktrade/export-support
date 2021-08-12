import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertTemplateUsed

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
                "company_type": "2",
                "type_of_organisation": "Typeoforganisation",
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
            "company_type": "Other type of UK organisation",
            "company_type_of_organisation": "Typeoforganisation",
            "countries": "Albania, Andorra, Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Kosovo, Latvia, Liechtenstein, Lithuania, Luxembourg, Malta, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, San Marino, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Vatican City",
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "Fewer than 10",
            "on_behalf_of": "The business I own or work for",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",
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
            "company_type_of_organisation": "",
            "countries": "Albania, Andorra, Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Kosovo, Latvia, Liechtenstein, Lithuania, Luxembourg, Malta, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, San Marino, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Vatican City",
            "email": "test@example.com",
            "enquiry_subject": "Selling goods abroad, Selling services abroad",
            "full_name": "Firstname Lastname",
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "number_of_employees": "",
            "on_behalf_of": "This enquiry does not relate to a (currently operating) business",
            "other_sector": "ANOTHER SECTOR",
            "sectors": "Advanced engineering, Aerospace, Agriculture, horticulture, fisheries and pets, Airports, Automotive, Chemicals, Construction, Consumer and retail, Creative industries, Defence, Education and training, Energy, Environment, Financial and professional services, Food and drink, Healthcare services, Logistics, Maritime, Medical devices and equipment, Mining, Pharmaceuticals and biotechnology, Railways, Security, Space, Sports economy, Technology and smart cities, Water",
        }
    )


def test_zendesk_form_is_not_valid_wizard_raises_error(client, settings, mocker):
    settings.FORM_URL = "FORM_URL"
    settings.ZENDESK_SERVICE_NAME = "ZENDESK_SERVICE_NAME"
    settings.ZENDESK_SUBDOMAIN = "ZENDESK_SUBDOMAIN"

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

        return response

    return run


def test_enquiry_subject_choices_context_data(run_wizard_enquiry_subject):
    response = run_wizard_enquiry_subject([1])
    ctx = response.context
    assert ctx["display_goods"] == True
    assert ctx["display_services"] == False
    assert ctx["display_subheadings"] == False

    response = run_wizard_enquiry_subject([2])
    ctx = response.context
    assert ctx["display_goods"] == False
    assert ctx["display_services"] == True
    assert ctx["display_subheadings"] == False

    response = run_wizard_enquiry_subject([1, 2])
    ctx = response.context
    assert ctx["display_goods"] == True
    assert ctx["display_services"] == True
    assert ctx["display_subheadings"] == True


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
    response = run_wizard_enquiry_subject_guidance_url([1])
    ctx = response.context
    assert (
        ctx["guidance_url"]
        == f"{reverse('core:non-eu-export-enquiries')}?enquiry_subject=1"
    )

    response = run_wizard_enquiry_subject_guidance_url([2])
    ctx = response.context
    assert (
        ctx["guidance_url"]
        == f"{reverse('core:non-eu-export-enquiries')}?enquiry_subject=2"
    )

    response = run_wizard_enquiry_subject_guidance_url([1, 2])
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
            {"enquiry_subject": ["1"]},
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
def run_wizard_export_countries():
    def run(export_countries_form_data):
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
                export_countries_form_data,
            ),
        )

        return response

    return run


def test_export_countries_validation(run_wizard_export_countries):
    response = run_wizard_export_countries(
        {
            "select_all": "1",
            "countries": ENQUIRY_COUNTRY_CODES,
        }
    )
    assert response.status_code == 302
    assert response.url == get_step_url("personal-details")

    response = run_wizard_export_countries({})
    assert response.status_code == 200
    assertFormError(
        response,
        "form",
        "countries",
        "Select the country or countries you are selling to",
    )

    response = run_wizard_export_countries(
        {
            "select_all": "1",
            "countries": ENQUIRY_COUNTRY_CODES[:1],
        }
    )
    assert response.status_code == 200
    assertFormError(
        response,
        "form",
        "countries",
        'You must select either "Select all" or some countries not both',
    )


@pytest.fixture
def run_wizard_sectors():
    def run(sectors_form_data):
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
                sectors_form_data,
            ),
        )

        return response

    return run


def test_sectors_validation(run_wizard_sectors):
    response = run_wizard_sectors({})
    assert response.status_code == 200
    assertFormError(
        response,
        "form",
        "sectors",
        "Select the industry or business area(s) your enquiry relates to",
    )


@pytest.fixture
def run_wizard_business_details():
    def run(business_details_form_data):
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
                business_details_form_data,
            ),
        )

        return response

    return run


def test_business_details_validation(run_wizard_business_details):
    response = run_wizard_business_details(
        {
            "company_name": "Companyname",
            "company_post_code": "SW1A 2BL",
        }
    )
    assert response.status_code == 200
    assertFormError(
        response,
        "form",
        "company_type",
        "Select the business type",
    )

    response = run_wizard_business_details(
        {
            "company_type": "2",
            "company_name": "Companyname",
            "company_post_code": "SW1A 2BL",
        }
    )
    assert response.status_code == 200
    assertFormError(
        response,
        "form",
        "type_of_organisation",
        "Enter the type of organisation",
    )

    response = run_wizard_business_details(
        {
            "company_type": "2",
            "company_name": "Companyname",
            "company_post_code": "SW1A 2BL",
            "type_of_organisation": "    ",
        }
    )
    assert response.status_code == 200
    assertFormError(
        response,
        "form",
        "type_of_organisation",
        "Enter the type of organisation",
    )
