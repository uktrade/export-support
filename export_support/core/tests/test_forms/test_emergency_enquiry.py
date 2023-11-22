from django.test import TestCase

from ...forms import EmergencySituationEnquiryForm


class EmergencySituationFormTestCase(TestCase):
    def setUp(self):
        self.test_form_dict = {
            "full_name": "John Enquirytest",
            "company_name": "John Company",
            "company_post_code": "te51in",
            "email": "John.Enquirytest@test.com",
            "phone": "07786179011",
            "sectors": [
                "advanced_engineering__ess_sector_l1",
                "chemicals__ess_sector_l1",
                "logistics__ess_sector_l1",
            ],
            "other": "",
            "question": "I have a question",
        }

    def test_valid_form_entry(self):
        form = EmergencySituationEnquiryForm(self.test_form_dict)

        assert form.is_valid()
        assert form.get_zendesk_data() == {
            "full_name": "John Enquirytest",
            "email": "John.Enquirytest@test.com",
            "phone": "07786179011",
            "company_name": "John Company",
            "company_post_code": "te51in",
            "sectors": "Advanced engineering, Chemicals, Logistics",
            "other_sector": "",
            "question": "I have a question",
            "on_behalf_of": "-",
            "company_type": "-",
            "company_type_category": "-",
            "how_did_you_hear_about_this_service": "-",
        }

    def test_valid_form_entry_other_sectors_used(self):
        self.test_form_dict["sectors"] = []
        self.test_form_dict["other"] = "Magic Trick Sales"
        form = EmergencySituationEnquiryForm(self.test_form_dict)

        assert form.is_valid()
        assert form.get_zendesk_data() == {
            "full_name": "John Enquirytest",
            "email": "John.Enquirytest@test.com",
            "phone": "07786179011",
            "company_name": "John Company",
            "company_post_code": "te51in",
            "sectors": "",
            "other_sector": "Magic Trick Sales",
            "question": "I have a question",
            "on_behalf_of": "-",
            "company_type": "-",
            "company_type_category": "-",
            "how_did_you_hear_about_this_service": "-",
        }

    def test_valid_form_entry_other_sectors_used_with_sector_list(self):
        self.test_form_dict["other"] = "Magic Trick Sales"
        form = EmergencySituationEnquiryForm(self.test_form_dict)

        assert form.is_valid()
        assert form.get_zendesk_data() == {
            "full_name": "John Enquirytest",
            "email": "John.Enquirytest@test.com",
            "phone": "07786179011",
            "company_name": "John Company",
            "company_post_code": "te51in",
            "sectors": "Advanced engineering, Chemicals, Logistics",
            "other_sector": "Magic Trick Sales",
            "question": "I have a question",
            "on_behalf_of": "-",
            "company_type": "-",
            "company_type_category": "-",
            "how_did_you_hear_about_this_service": "-",
        }

    def test_invalid_form_missing_name(self):
        self.test_form_dict["full_name"] = ""
        form = EmergencySituationEnquiryForm(self.test_form_dict)

        assert not form.is_valid()
        assert form.errors == {
            "full_name": ["Enter your full name"],
        }

    def test_invalid_form_missing_email(self):
        self.test_form_dict["email"] = ""
        form = EmergencySituationEnquiryForm(self.test_form_dict)

        assert not form.is_valid()
        assert form.errors == {
            "email": ["Enter your email address"],
        }

    def test_invalid_form_missing_phone_number(self):
        self.test_form_dict["phone"] = ""
        form = EmergencySituationEnquiryForm(self.test_form_dict)

        assert not form.is_valid()
        assert form.errors == {
            "phone": ["Enter your telephone number"],
        }

    def test_invalid_form_phone_not_numbers(self):
        self.test_form_dict["phone"] = "077breakme"
        form = EmergencySituationEnquiryForm(self.test_form_dict)

        assert not form.is_valid()
        assert form.errors == {
            "phone": ["This value can only contain numbers"],
        }

    def test_invalid_form_missing_business_name(self):
        self.test_form_dict["company_name"] = ""
        form = EmergencySituationEnquiryForm(self.test_form_dict)

        assert not form.is_valid()
        assert form.errors == {
            "company_name": ["Enter the business name"],
        }

    def test_invalid_form_missing_postcode(self):
        self.test_form_dict["company_post_code"] = ""
        form = EmergencySituationEnquiryForm(self.test_form_dict)

        assert not form.is_valid()
        assert form.errors == {
            "company_post_code": ["Enter the business unit postcode"],
        }

    def test_invalid_form_invalid_postcode(self):
        self.test_form_dict["company_post_code"] = "fakepostcode"
        form = EmergencySituationEnquiryForm(self.test_form_dict)

        assert not form.is_valid()
        assert form.errors == {
            "company_post_code": ["Enter a valid postcode"],
        }

    def test_invalid_form_missing_sectors_and_other(self):
        self.test_form_dict["sectors"] = []
        form = EmergencySituationEnquiryForm(self.test_form_dict)

        assert not form.is_valid()
        assert form.errors == {
            "sectors": [
                "Select the industry or business area(s) your enquiry relates to"
            ],
        }

    def test_invalid_form_missing_question(self):
        self.test_form_dict["question"] = ""
        form = EmergencySituationEnquiryForm(self.test_form_dict)

        assert not form.is_valid()
        assert form.errors == {
            "question": ["Enter your enquiry"],
        }
