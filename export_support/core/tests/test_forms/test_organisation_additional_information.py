from ...forms import (
    CompanyTurnoverChoices,
    NumberOfEmployeesChoices,
    OrganisationAdditionalInformationForm,
    OrganisationTypeChoices,
)


def test_get_zendesk_data():
    form = OrganisationAdditionalInformationForm(
        {
            "type_of_organisation": OrganisationTypeChoices.CHARITY_OR_SOCIAL_ENTERPRISE,
            "organisation_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "type_of_organisation": "Charity / Social enterprise",
        "organisation_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
    }

    form = OrganisationAdditionalInformationForm(
        {
            "type_of_organisation": OrganisationTypeChoices.OTHER,
            "other_type_of_organisation": "OTHER TYPE OF ORGANISATION",
            "organisation_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "type_of_organisation": "OTHER TYPE OF ORGANISATION",
        "organisation_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
    }

    form = OrganisationAdditionalInformationForm(
        {
            "type_of_organisation": OrganisationTypeChoices.CHARITY_OR_SOCIAL_ENTERPRISE,
            "other_type_of_organisation": "THIS IS IGNORED",
            "organisation_turnover": CompanyTurnoverChoices.BELOW_85000,
            "number_of_employees": NumberOfEmployeesChoices.FEWER_THAN_10,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "type_of_organisation": "Charity / Social enterprise",
        "organisation_turnover": "Below £85,000",
        "number_of_employees": "Fewer than 10",
    }
