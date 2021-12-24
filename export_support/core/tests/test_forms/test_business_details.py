from ...forms import BusinessDetailsForm


def test_get_zendesk_data():
    form = BusinessDetailsForm(
        {
            "company_name": "ACME",
            "company_post_code": "SW1A 2BL",
            "company_registration_number": "12345678",
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_name": "ACME",
        "company_post_code": "SW1A 2BL",
        "company_registration_number": "12345678",
    }
