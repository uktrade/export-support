from ...forms import (
    CompanyTurnoverChoices,
    HaveYouExportedBeforeChoices,
    PositivityForGrowthChoices,
    SoloExporterAdditionalInformationForm,
    SoloExporterTypeChoices,
)


def test_validation_type_of_business_required():
    form = SoloExporterAdditionalInformationForm(
        {
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "company_type": ["Select the type of exporter"],
    }


def test_validation_other_type_of_business_required_when_other_selected():
    form = SoloExporterAdditionalInformationForm(
        {
            "company_type": SoloExporterTypeChoices.OTHER,
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "have_you_exported_before": HaveYouExportedBeforeChoices.NO,
            "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "other_type_of_exporter": ["Enter the type of exporter"],
    }


def test_get_zendesk_data():
    form = SoloExporterAdditionalInformationForm(
        {
            "company_type": SoloExporterTypeChoices.SOLE_TRADER,
            "positivity_for_growth": PositivityForGrowthChoices.VERY_POSITIVE,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "Sole trader",
        "company_turnover": "",
        "number_of_employees": "Fewer than 10",
        "positivity_for_growth": "Very positive",
    }

    form = SoloExporterAdditionalInformationForm(
        {
            "company_type": SoloExporterTypeChoices.SOLE_TRADER,
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "Sole trader",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
        "positivity_for_growth": "Neutral",
    }

    form = SoloExporterAdditionalInformationForm(
        {
            "company_type": SoloExporterTypeChoices.OTHER,
            "other_type_of_exporter": "OTHER TYPE OF ORGANISATION",
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "positivity_for_growth": PositivityForGrowthChoices.QUITE_POSITIVE,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "OTHER TYPE OF ORGANISATION",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
        "positivity_for_growth": "Quite positive",
    }

    form = SoloExporterAdditionalInformationForm(
        {
            "company_type": SoloExporterTypeChoices.SOLE_TRADER,
            "other_type_of_exporter": "THIS IS IGNORED",
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "positivity_for_growth": PositivityForGrowthChoices.VERY_NEGATIVE,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "Sole trader",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
        "positivity_for_growth": "Very negative",
    }
