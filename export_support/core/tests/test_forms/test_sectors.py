from ...forms import SectorsForm


def test_sectors_validation():
    form = SectorsForm({})

    assert not form.is_valid()
    assert form.errors == {
        "sectors": ["Select the industry or business area(s) your enquiry relates to"],
    }
