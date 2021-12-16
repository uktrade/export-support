from ...forms import (
    BusinessAdditionalInformationForm,
    CompanyTurnoverChoices,
    NumberOfEmployeesChoices,
    PrivateOrPublicCompanyTypeChoices,
)


def test_business_information_form_validation_type_of_business_required():
    form = BusinessAdditionalInformationForm(
        {
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "type_of_business": ["Select the type of business"],
    }


def test_business_information_form_validation_other_type_of_business_required_when_other_selected():
    form = BusinessAdditionalInformationForm(
        {
            "type_of_business": PrivateOrPublicCompanyTypeChoices.OTHER,
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "other_type_of_business": ["Enter the type of business"],
    }
