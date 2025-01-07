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


def test_get_zendesk_data():
    form = EnquiryDetailsForm(
        {
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "question": "QUESTION",
            "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "nature_of_enquiry": "NATURE OF ENQUIRY",
        "question": "QUESTION",
        "how_did_you_hear_about_this_service": "Search engine",
        "marketing_consent": False,
    }

    form = EnquiryDetailsForm(
        {
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "question": "QUESTION",
            "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "nature_of_enquiry": "NATURE OF ENQUIRY",
        "question": "QUESTION",
        "how_did_you_hear_about_this_service": "Search engine",
        "marketing_consent": True,
    }

    form = EnquiryDetailsForm(
        {
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "question": "QUESTION",
            "marketing_consent": False,
            "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.OTHER,
            "other_how_did_you_hear_about_this_service": "HEARD FROM OTHER",
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "nature_of_enquiry": "NATURE OF ENQUIRY",
        "question": "QUESTION",
        "marketing_consent": False,
        "how_did_you_hear_about_this_service": "HEARD FROM OTHER",
    }

    form = EnquiryDetailsForm(
        {
            "nature_of_enquiry": "NATURE OF ENQUIRY",
            "question": "QUESTION",
            "marketing_consent": False,
            "how_did_you_hear_about_this_service": HowDidYouHearAboutThisServiceChoices.SEARCH_ENGINE,
            "other_how_did_you_hear_about_this_service": "Search engine",
        }
    )

    assert form.is_valid()
    assert form.get_zendesk_data() == {
        "nature_of_enquiry": "NATURE OF ENQUIRY",
        "question": "QUESTION",
        "marketing_consent": False,
        "how_did_you_hear_about_this_service": "Search engine",
    }
