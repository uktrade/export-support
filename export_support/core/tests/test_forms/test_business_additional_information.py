from ...forms import (
    BusinessAdditionalInformationForm,
    CompanyTurnoverChoices,
    NumberOfEmployeesChoices,
    PositivityForGrowthChoices,
    PrivateOrPublicCompanyTypeChoices,
)


def test_business_information_form_validation():
    form = BusinessAdditionalInformationForm({})

    assert not form.is_valid()
    assert form.errors == {
        "company_type": ["Select the type of business"],
        "company_turnover": ["Select the UK business turnover"],
        "number_of_employees": ["Select the number of UK employees"],
        "positivity_for_growth": [
            "Select how positive you feel about growing your business overseas"
        ],
    }


def test_business_information_form_validation_other_type_of_business_required_when_other_selected():
    form = BusinessAdditionalInformationForm(
        {
            "company_type": PrivateOrPublicCompanyTypeChoices.OTHER,
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
            "positivity_for_growth": PositivityForGrowthChoices.VERY_POSITIVE,
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "other_type_of_business": ["Enter the type of business"],
    }


def test_get_zendesk_data():
    form = BusinessAdditionalInformationForm(
        {
            "company_type": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
            "positivity_for_growth": PositivityForGrowthChoices.VERY_POSITIVE,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "Private limited company",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
        "positivity_for_growth": "Very positive",
    }

    form = BusinessAdditionalInformationForm(
        {
            "company_type": PrivateOrPublicCompanyTypeChoices.OTHER,
            "other_type_of_business": "OTHER TYPE OF BUSINESS",
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
            "positivity_for_growth": PositivityForGrowthChoices.NEUTRAL,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "OTHER TYPE OF BUSINESS",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
        "positivity_for_growth": "Neutral",
    }

    form = BusinessAdditionalInformationForm(
        {
            "company_type": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
            "other_type_of_business": "THIS IS IGNORED",
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
            "positivity_for_growth": PositivityForGrowthChoices.VERY_NEGATIVE,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "Private limited company",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
        "positivity_for_growth": "Very negative",
    }
