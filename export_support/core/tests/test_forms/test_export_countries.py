from ...consts import ENQUIRY_COUNTRY_CODES
from ...forms import ExportCountriesForm

COUNTRY_MACHINE_READABLE_VALUES = list(ENQUIRY_COUNTRY_CODES.values())


def test_export_countries_validation_is_valid():
    form = ExportCountriesForm(
        {
            "select_all": "1",
            "countries": COUNTRY_MACHINE_READABLE_VALUES,
        }
    )
    assert form.is_valid()


def test_export_countries_validation_no_countries_selected():
    form = ExportCountriesForm({})
    assert not form.is_valid()
    assert form.errors == {
        "countries": ["Select the country or countries you are selling to"],
    }


def test_export_countries_validation_select_all_mutually_exclusive_from_countries():
    form = ExportCountriesForm(
        {
            "select_all": "1",
            "countries": COUNTRY_MACHINE_READABLE_VALUES[:1],
        }
    )
    assert not form.is_valid()
    assert form.errors == {
        "countries": ['You must select either "Select all" or some countries not both'],
    }


def test_export_countries_validation_invalid_country():
    form = ExportCountriesForm(
        {
            "select_all": "1",
            "countries": ["invalid_country"],
        }
    )
    assert not form.is_valid()
    assert form.errors == {
        "countries": [
            "Select a valid choice. invalid_country is not one of the available choices."
        ],
    }
