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
        "company_type": ["Select the type of business"],
    }


def test_business_information_form_validation_other_type_of_business_required_when_other_selected():
    form = BusinessAdditionalInformationForm(
        {
            "company_type": PrivateOrPublicCompanyTypeChoices.OTHER,
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
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
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "Private limited company",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
    }

    form = BusinessAdditionalInformationForm(
        {
            "company_type": PrivateOrPublicCompanyTypeChoices.OTHER,
            "other_type_of_business": "OTHER TYPE OF BUSINESS",
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "OTHER TYPE OF BUSINESS",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
    }

    form = BusinessAdditionalInformationForm(
        {
            "company_type": PrivateOrPublicCompanyTypeChoices.PRIVATE_LIMITED_COMPANY,
            "other_type_of_business": "THIS IS IGNORED",
            "company_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "company_type": "Private limited company",
        "company_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
    }
