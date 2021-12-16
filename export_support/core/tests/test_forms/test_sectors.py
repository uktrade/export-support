from ...forms import SectorsForm


def test_sectors_validation():
    form = SectorsForm({})

    assert not form.is_valid()
    assert form.errors == {
        "sectors": ["Select the industry or business area(s) your enquiry relates to"],
    }


def test_get_zendesk_data():
    form = SectorsForm(
        {
            "sectors": [
                "advanced_engineering__ess_sector_l1",
                "chemicals__ess_sector_l1",
                "logistics__ess_sector_l1",
            ],
            "other": "OTHER SECTOR",
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "sectors": "Advanced engineering, Chemicals, Logistics",
        "other_sector": "OTHER SECTOR",
    }
