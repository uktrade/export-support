from ...forms import EnquiryDetailsForm, HowDidYouHearAboutThisServiceChoices


def test_enquiry_details_validation_how_did_you_hear_required():
    form = EnquiryDetailsForm(
        {
            "nature_of_enquiry": "TEST",
            "question": "TEST",
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "how_did_you_hear_about_this_service": [
            "Select how you heard about this service"
        ],
    }


def test_enquiry_details_validation_how_did_you_hear_other_required():
    form = EnquiryDetailsForm(
        {
            "nature_of_enquiry": "TEST",
            "question": "TEST",
            "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.OTHER,
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "other_how_did_you_hear_about_this_service": [
            "Enter how you heard about this service"
        ],
    }
