from ...forms import DoYouHaveAProductYouWantToExportChoices, HaveYouExportedBeforeChoices, \
    OrganisationDetailsForm


def test_get_zendesk_data():
    form = OrganisationDetailsForm(
        {
            "company_name": "ACME",
            "company_registration_number": "12345678",
            "company_post_code": "SW1A 2BL",
            "have_you_exported_before": HaveYouExportedBeforeChoices.NO,
            "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_name": "ACME",
        "company_registration_number": "12345678",
        "company_post_code": "SW1A 2BL",
        "have_you_exported_before": "No",
        "do_you_have_a_product_you_want_to_export": "Yes",
    }
