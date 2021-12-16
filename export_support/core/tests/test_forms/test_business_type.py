from ...forms import BusinessTypeChoices, BusinessTypeForm


def test_get_zendesk_data():
    form = BusinessTypeForm(
        {
            "business_type": BusinessTypeChoices.PRIVATE_OR_LIMITED,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {}
