from ...forms import OrganisationDetailsForm


def test_get_zendesk_data():
    form = OrganisationDetailsForm(
        {
            "company_name": "ACME",
            "company_registration_number": "12345678",
            "company_post_code": "SW1A 2BL",
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_name": "ACME",
        "company_registration_number": "12345678",
        "company_post_code": "SW1A 2BL",
    }
