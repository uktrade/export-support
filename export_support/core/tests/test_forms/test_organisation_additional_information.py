from ...forms import (
    CompanyTurnoverChoices,
    NumberOfEmployeesChoices,
    OrganisationAdditionalInformationForm,
    OrganisationTypeChoices,
    PositivityForGrowthChoices,
)


def test_validation_type_of_business_required():
    form = OrganisationAdditionalInformationForm(
        {
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
            "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "company_type": ["Select the type of organisation"],
    }


def test_validation_other_type_of_business_required_when_other_selected():
    form = OrganisationAdditionalInformationForm(
        {
            "company_type": OrganisationTypeChoices.OTHER,
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
            "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "other_type_of_organisation": ["Enter the type of organisation"],
    }


def test_get_zendesk_data():
    form = OrganisationAdditionalInformationForm(
        {
            "company_type": OrganisationTypeChoices.CHARITY_OR_SOCIAL_ENTERPRISE,
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
            "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "Charity / Social enterprise",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
        "positivity_for_growth": "Neutral",
    }

    form = OrganisationAdditionalInformationForm(
        {
            "company_type": OrganisationTypeChoices.OTHER,
            "other_type_of_organisation": "OTHER TYPE OF ORGANISATION",
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
            "positivity_for_growth": PositivityForGrowthChoices.VERY_POSITIVE,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "OTHER TYPE OF ORGANISATION",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
        "positivity_for_growth": "Very positive",
    }

    form = OrganisationAdditionalInformationForm(
        {
            "company_type": OrganisationTypeChoices.CHARITY_OR_SOCIAL_ENTERPRISE,
            "other_type_of_organisation": "THIS IS IGNORED",
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
            "positivity_for_growth": PositivityForGrowthChoices.VERY_NEGATIVE,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "Charity / Social enterprise",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
        "positivity_for_growth": "Very negative",
    }
