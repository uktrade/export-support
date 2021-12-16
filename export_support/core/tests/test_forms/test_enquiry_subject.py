from ...forms import EnquirySubjectChoices, EnquirySubjectForm


def test_get_zendesk_data():
    form = EnquirySubjectForm(
        {
            "enquiry_subject": [
                EnquirySubjectChoices.SELLING_GOODS_ABROAD,
                EnquirySubjectChoices.SELLING_SERVICES_ABROAD,
            ]
        }
    )

    assert form.is_valid()
    zendesk_data = form.get_zendesk_data()
    assert zendesk_data == {
        "enquiry_subject": "Selling goods abroad, Selling services abroad"
    }
