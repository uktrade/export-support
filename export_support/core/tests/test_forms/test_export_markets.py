from ...consts import ENQUIRY_MARKET_CODES
from ...forms import ExportMarketsForm

MARKET_MACHINE_READABLE_VALUES = list(ENQUIRY_MARKET_CODES.values()).sort()


def test_export_markets_validation_is_valid():
    form = ExportMarketsForm(
        {
            "select_all": True,
            "markets": [],
            "no_specific_market": False,
        }
    )
    assert form.is_valid()


def test_export_markets_validation_no_markets_selected():
    form = ExportMarketsForm({})
    assert not form.is_valid()
    assert form.errors == {
        "markets": ["Select the market or markets you are selling to"],
    }


def test_export_markets_validation_select_all_mutually_exclusive_from_markets():
    form = ExportMarketsForm(
        {
            "select_all": True,
            "markets": ["albania__ess_export"],
            "no_specific_market": False,
        }
    )
    assert not form.is_valid()
    assert form.errors == {
        "markets": ['You must select either "Select all" or some markets not both'],
    }


def test_export_markets_validation_select_all():
    form = ExportMarketsForm(
        {
            "select_all": True,
            "markets": MARKET_MACHINE_READABLE_VALUES,
            "no_specific_market": False,
        }
    )
    assert form.is_valid()


def test_export_markets_validation_invalid_market():
    form = ExportMarketsForm(
        {
            "select_all": True,
            "markets": ["invalid_market"],
            "no_specific_market": False,
        }
    )
    assert not form.is_valid()
    assert form.errors == {
        "markets": [
            "Select a valid choice. invalid_market is not one of the available choices."
        ],
    }


def test_export_markets_validation_no_specific_and_select_all_rejected():
    form = ExportMarketsForm(
        {
            "select_all": True,
            "markets": [],
            "no_specific_market": True,
        }
    )
    assert not form.is_valid()
    assert form.errors == {
        "markets": [
            "You must select either some markets or indicate no specific market not both"
        ],
    }


def test_export_markets_validation_no_specific_and_market_rejected():
    form = ExportMarketsForm(
        {
            "select_all": False,
            "markets": ["latvia__ess_export"],
            "no_specific_market": True,
        }
    )
    assert not form.is_valid()
    assert form.errors == {
        "markets": [
            "You must select either some markets or indicate no specific market not both"
        ],
    }


def test_no_specific_export_markets():
    form = ExportMarketsForm(
        {
            "select_all": False,
            "markets": [],
            "no_specific_market": True,
        }
    )
    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "markets": "No specific market",
    }


def test_get_zendesk_data():
    form = ExportMarketsForm(
        {
            "select_all": False,
            "markets": [
                "albania__ess_export",
                "cyprus__ess_export",
                "latvia__ess_export",
            ],
            "no_specific_market": False,
        }
    )
    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "markets": "Albania, Cyprus, Latvia",
    }
