from ...forms import (
    CompanyTurnoverChoices,
    SoloExporterAdditionalInformationForm,
    SoloExporterTypeChoices,
)


def test_get_zendesk_data():
    form = SoloExporterAdditionalInformationForm(
        {
            "type_of_exporter": SoloExporterTypeChoices.SOLE_TRADER,
            "business_turnover": CompanyTurnoverChoices.BELOW_85000,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "type_of_exporter": "Sole trader",
        "business_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
    }

    form = SoloExporterAdditionalInformationForm(
        {
            "type_of_exporter": SoloExporterTypeChoices.OTHER,
            "other_type_of_exporter": "OTHER TYPE OF ORGANISATION",
            "business_turnover": CompanyTurnoverChoices.BELOW_85000,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "type_of_exporter": "OTHER TYPE OF ORGANISATION",
        "business_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
    }

    form = SoloExporterAdditionalInformationForm(
        {
            "type_of_exporter": SoloExporterTypeChoices.SOLE_TRADER,
            "other_type_of_exporter": "THIS IS IGNORED",
            "business_turnover": CompanyTurnoverChoices.BELOW_85000,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "type_of_exporter": "Sole trader",
        "business_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
    }
