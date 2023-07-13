from ...forms import (
    BusinessDetailsForm,
    DoYouHaveAProductYouWantToExportChoices,
    HaveYouExportedBeforeChoices,
)


def test_get_zendesk_data():
    form = BusinessDetailsForm(
        {
            "company_name": "ACME",
            "company_post_code": "SW1A 2BL",
            "company_registration_number": "12345678",
            "have_you_exported_before": HaveYouExportedBeforeChoices.YES_LAST_YEAR,
            "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_name": "ACME",
        "company_post_code": "SW1A 2BL",
        "company_registration_number": "12345678",
        "have_you_exported_before": HaveYouExportedBeforeChoices.YES_LAST_YEAR,
        "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
    }
