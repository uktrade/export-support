from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from export_support.gds import fields as gds_fields

from .consts import ENQUIRY_COUNTRY_CODES_TO_NAME_MAP, SECTORS


class EnquirySubjectChoices(models.IntegerChoices):
    SELLING_GOODS_ABROAD = 1, "Selling goods abroad"
    SELLING_SERVICES_ABROAD = 2, "Selling services abroad"


class EnquirySubjectForm(forms.Form):
    enquiry_subject = forms.TypedMultipleChoiceField(
        coerce=lambda choice: EnquirySubjectChoices(int(choice)),
        choices=EnquirySubjectChoices.choices,
        label="What is your enquiry about?",
        widget=gds_fields.CheckboxSelectMultiple,
    )

    def get_filter_data(self):
        enquiry_subject_value = self.cleaned_data["enquiry_subject"]

        filter_data = {
            "enquiry_subject": enquiry_subject_value,
        }

        return filter_data


class ExportCountriesForm(forms.Form):
    select_all = forms.BooleanField(
        label="Select all",
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "govuk-checkboxes__input"},
        ),
    )
    countries = forms.MultipleChoiceField(
        choices=[
            (code, country_name)
            for code, country_name in ENQUIRY_COUNTRY_CODES_TO_NAME_MAP.items()
        ],
        label="Which country are you selling to?",
        required=False,
        widget=gds_fields.CheckboxSelectMultiple,
    )

    def clean(self):
        cleaned_data = super().clean()

        has_select_all_selected = bool(cleaned_data["select_all"])
        has_countries_selected = any(cleaned_data["countries"])
        has_all_countries_selected = [
            code for code, _ in self.fields["countries"].choices
        ] == cleaned_data["countries"]

        if has_select_all_selected and has_all_countries_selected:
            return cleaned_data

        if not has_select_all_selected and not has_countries_selected:
            raise ValidationError(
                'You must select either "Select all" or some countries'
            )

        if has_select_all_selected and has_countries_selected:
            raise ValidationError(
                'You must select either "Select all" or some countries. Not both.'
            )

        return cleaned_data


class OnBehalfOfChoices(models.IntegerChoices):
    OWN_COMPANY = 1, "The business I own or work for"
    ANOTHER_COMPANY = 2, "I am asking on behalf of another company"
    NOT_A_COMPANY = 3, "This enquiry does not relate to a company"


class PersonalDetailsForm(forms.Form):
    first_name = forms.CharField(
        label="First name",
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    last_name = forms.CharField(
        label="Last name",
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    email = forms.EmailField(
        help_text="We'll only use this to send you a receipt",
        label="Email address",
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    on_behalf_of = forms.TypedChoiceField(
        coerce=lambda choice: OnBehalfOfChoices(int(choice)),
        choices=OnBehalfOfChoices.choices,
        label="Who is this enquiry for?",
        widget=gds_fields.RadioSelect,
    )


class CompanyTypeChoices(models.IntegerChoices):
    PRIVATE_OR_LIMITED = 1, "UK private or public limited company"
    OTHER = 2, "Other type of organisation"


class BusinessDetailsForm(forms.Form):
    company_type = forms.TypedChoiceField(
        coerce=lambda choice: CompanyTypeChoices(int(choice)),
        choices=CompanyTypeChoices.choices,
        label="Business type",
        widget=gds_fields.RadioSelect,
    )
    company_name = forms.CharField(
        label="Business name",
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_post_code = forms.CharField(
        label="Business post code",
        validators=[
            validators.RegexValidator(
                regex=r"^(([A-Z]{1,2}[0-9][A-Z0-9]?|ASCN|STHL|TDCU|BBND|[BFS]IQQ|PCRN|TKCA) ?[0-9][A-Z]{2}|BFPO ?[0-9]{1,4}|(KY[0-9]|MSR|VG|AI)[ -]?[0-9]{4}|[A-Z]{2} ?[0-9]{2}|GE ?CX|GIR ?0A{2}|SAN ?TA1)$",
                message="You need to add a valid postcode.",
            ),
        ],
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_registration_number = forms.CharField(
        label="Company Registration Number",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )


class CompanyTurnoverChoices(models.IntegerChoices):
    BELOW_85000 = 1, "Below £85,000"
    FROM_85000_TO_499999 = 2, "£85,000 to £499,999"
    FROM_500000_TO_49999999 = 3, "£500,000 to £49,999,999"
    OVER_50000000 = 4, "£50,000,000+"
    DO_NOT_KNOW = 5, "I do not know"
    PREFER_NOT_TO_SAY = 6, "I'd prefer not to say"


class NumberOfEmployeesChoices(models.IntegerChoices):
    FEWER_THAN_10 = 1, "Fewer than 10"
    FROM_10_TO_49 = 2, "10 - 49"
    FROM_50_TO_249 = 3, "50 - 249"
    OVER_250 = 4, "250 or more"
    DO_NOT_KNOW = 5, "I don't know"
    PREFER_NOT_TO_SAY = 6, "I'd prefer not to say"


class BusinessSizeForm(forms.Form):
    company_turnover = forms.ChoiceField(
        choices=[("", "Please select")] + CompanyTurnoverChoices.choices,
        label="Business turnover",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
            },
        ),
    )
    number_of_employees = forms.ChoiceField(
        choices=[("", "Please select")] + NumberOfEmployeesChoices.choices,
        label="Number of UK employees",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
            },
        ),
    )


class SectorsForm(forms.Form):
    sectors = forms.MultipleChoiceField(
        choices=[(slugify(sector), sector) for sector in SECTORS],
        label="Which industry or business area does your enquiry relate to?",
        required=False,
        widget=gds_fields.CheckboxSelectMultiple,
    )
    is_other = forms.BooleanField(
        label="Select all",
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "govuk-checkboxes__input"},
        ),
    )
    other = forms.CharField(
        label="Please specify",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-three-quarters",
            },
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        is_other = cleaned_data["is_other"]
        is_other_selected = bool(is_other)
        other = cleaned_data["other"]
        is_other_text_blank = not bool(other)

        if is_other_selected and is_other_text_blank:
            self.add_error("other", 'You must add text for "Other".')

        return cleaned_data


class EnquiryDetailsForm(forms.Form):
    nature_of_enquiry = forms.CharField(
        label="Please describe the good(s) or service(s) the enquiry is about",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input",
            },
        ),
    )
    question = forms.CharField(
        label="Your enquiry",
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": 10,
            },
        ),
    )
