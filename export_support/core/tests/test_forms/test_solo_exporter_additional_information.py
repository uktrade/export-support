from ...forms import (
    CompanyTurnoverChoices,
    SoloExporterAdditionalInformationForm,
    SoloExporterTypeChoices,
)


def test_validation_type_of_business_required():
    form = SoloExporterAdditionalInformationForm(
        {
            "organisation_turnover": CompanyTurnoverChoices.BELOW_85000,
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "type_of_exporter": ["Select the type of exporter"],
    }


def test_validation_other_type_of_business_required_when_other_selected():
    form = SoloExporterAdditionalInformationForm(
        {
            "type_of_exporter": SoloExporterTypeChoices.OTHER,
            "organisation_turnover": CompanyTurnoverChoices.BELOW_85000,
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "other_type_of_exporter": ["Enter the type of exporter"],
    }


def test_get_zendesk_data():
    form = SoloExporterAdditionalInformationForm(
        {
            "type_of_exporter": SoloExporterTypeChoices.SOLE_TRADER,
            "business_turnover": CompanyTurnoverChoices.BELOW_85000,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "type_of_business": "Sole trader",
        "company_turnover": "Below £85,000",
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
        "type_of_business": "OTHER TYPE OF ORGANISATION",
        "company_turnover": "Below £85,000",
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
        "type_of_business": "Sole trader",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
    }
