from ...forms import DoYouHaveAProductYouWantToExportChoices, HaveYouExportedBeforeChoices, \
    SoloExporterDetailsForm


def test_get_zendesk_data():
    form = SoloExporterDetailsForm(
        {
            "company_name": "ACME",
            "company_post_code": "SW1A 2BL",
            "have_you_exported_before": HaveYouExportedBeforeChoices.NO,
            "do_you_have_a_product_you_want_to_export": DoYouHaveAProductYouWantToExportChoices.YES,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_name": "ACME",
        "company_post_code": "SW1A 2BL",
        "have_you_exported_before": "No",
        "do_you_have_a_product_you_want_to_export": "Yes",
    }
