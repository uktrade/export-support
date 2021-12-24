from ...forms import OnBehalfOfChoices, PersonalDetailsForm


def test_get_zendesk_data():
    form = PersonalDetailsForm(
        {
            "email": "test@example.com",
            "first_name": "FIRST",
            "last_name": "LAST",
            "on_behalf_of": OnBehalfOfChoices.OWN_COMPANY,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "email": "test@example.com",
        "full_name": "FIRST LAST",
        "on_behalf_of": "The business I own or work for (or in my own interest)",
    }
