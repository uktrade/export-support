from ...consts import ENQUIRY_COUNTRY_CODES
from ...forms import ExportCountriesForm

COUNTRY_MACHINE_READABLE_VALUES = list(ENQUIRY_COUNTRY_CODES.values()).sort()


def test_export_countries_validation_is_valid():
    form = ExportCountriesForm(
        {
            "select_all": True,
            "countries": [],
            "no_specific_country": False,
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
            "select_all": True,
            "countries": ["albania__ess_export"],
            "no_specific_country": False,
        }
    )
    assert not form.is_valid()
    assert form.errors == {
        "countries": ['You must select either "Select all" or some countries not both'],
    }


def test_export_countries_validation_select_all():
    form = ExportCountriesForm(
        {
            "select_all": True,
            "countries": COUNTRY_MACHINE_READABLE_VALUES,
            "no_specific_country": False,
        }
    )
    assert form.is_valid()


def test_export_countries_validation_invalid_country():
    form = ExportCountriesForm(
        {
            "select_all": True,
            "countries": ["invalid_country"],
            "no_specific_country": False,
        }
    )
    assert not form.is_valid()
    assert form.errors == {
        "countries": [
            "Select a valid choice. invalid_country is not one of the available choices."
        ],
    }


def test_export_countries_validation_no_specific_and_select_all_rejected():
    form = ExportCountriesForm(
        {
            "select_all": True,
            "countries": [],
            "no_specific_country": True,
        }
    )
    assert not form.is_valid()
    assert form.errors == {
        "countries": [
            "You must select either some countries or indicate no specific country not both"
        ],
    }


def test_export_countries_validation_no_specific_and_country_rejected():
    form = ExportCountriesForm(
        {
            "select_all": False,
            "countries": ["latvia__ess_export"],
            "no_specific_country": True,
        }
    )
    assert not form.is_valid()
    assert form.errors == {
        "countries": [
            "You must select either some countries or indicate no specific country not both"
        ],
    }


def test_no_specific_export_countries():
    form = ExportCountriesForm(
        {
            "select_all": False,
            "countries": [],
            "no_specific_country": True,
        }
    )
    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "countries": "No specific country",
    }


def test_get_zendesk_data():
    form = ExportCountriesForm(
        {
            "select_all": False,
            "countries": [
                "albania__ess_export",
                "cyprus__ess_export",
                "latvia__ess_export",
            ],
            "no_specific_country": False,
        }
    )
    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "countries": "Albania, Cyprus, Latvia",
    }
