from ...forms import SoloExporterDetailsForm


def test_get_zendesk_data():
    form = SoloExporterDetailsForm(
        {
            "business_name": "ACME",
            "post_code": "SW1A 2BL",
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "business_name": "ACME",
        "post_code": "SW1A 2BL",
    }
