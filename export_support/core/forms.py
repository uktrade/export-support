import re

from directory_forms_api_client.forms import ZendeskAPIForm
from django import forms
from django.core import validators
from django.db import models
from django.utils.safestring import mark_safe

from export_support.gds import fields as gds_fields
from export_support.gds import forms as gds_forms

from .consts import COUNTRIES_MAP, SECTORS_MAP


def coerce_choice(enum):
    def identity(x):
        return x

    if issubclass(enum, models.IntegerChoices):
        coercer = int
    else:
        coercer = identity

    def _coerce(choice):
        return enum(coercer(choice))

    return _coerce


class EnquirySubjectChoices(models.IntegerChoices):
    SELLING_GOODS_ABROAD = 1, "Selling goods abroad"
    SELLING_SERVICES_ABROAD = 2, "Selling services abroad"


class EnquirySubjectForm(forms.Form):
    enquiry_subject = forms.TypedMultipleChoiceField(
        coerce=coerce_choice(EnquirySubjectChoices),
        choices=EnquirySubjectChoices.choices,
        error_messages={
            "required": "Select whether you are selling goods or services or both",
        },
        label="What is your enquiry about?",
        widget=gds_fields.CheckboxSelectMultiple,
    )

    def get_filter_data(self):
        enquiry_subject_value = self.cleaned_data["enquiry_subject"]

        filter_data = {
            "enquiry_subject": enquiry_subject_value,
        }

        return filter_data

    def get_zendesk_data(self):
        enquiry_subject = self.cleaned_data["enquiry_subject"]
        enquiry_subject = ", ".join(s.label for s in enquiry_subject)

        return {"enquiry_subject": enquiry_subject}


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
            (machine_value, country_name)
            for machine_value, country_name in COUNTRIES_MAP.items()
        ],
        label="Which country are you selling to?",
        required=False,
        widget=gds_fields.CheckboxSelectMultiple,
    )

    def clean(self):
        cleaned_data = super().clean()

        has_select_all_selected = bool(cleaned_data["select_all"])

        try:
            # In the case that this field has produced a validation error before
            # and therefore doesn't exist at this stage we can just bail out
            # as there's another error to display.
            has_countries_selected = any(cleaned_data["countries"])
        except KeyError:
            return cleaned_data

        has_all_countries_selected = [
            code for code, _ in self.fields["countries"].choices
        ] == cleaned_data["countries"]

        if has_select_all_selected and has_all_countries_selected:
            return cleaned_data

        if not has_select_all_selected and not has_countries_selected:
            self.add_error(
                "countries", "Select the country or countries you are selling to"
            )

        if has_select_all_selected and has_countries_selected:
            self.add_error(
                "countries",
                'You must select either "Select all" or some countries not both',
            )

        return cleaned_data

    def get_zendesk_data(self):
        countries = self.cleaned_data["countries"]
        countries = [COUNTRIES_MAP[code] for code in countries]
        countries = ", ".join(countries)

        return {
            "countries": countries,
        }


class OnBehalfOfChoices(models.IntegerChoices):
    OWN_COMPANY = 1, "The business I own or work for"
    ANOTHER_COMPANY = 2, "I am asking on behalf of another business"
    NOT_A_COMPANY = (
        3,
        "This enquiry does not relate to a (currently operating) business",
    )


class PersonalDetailsForm(gds_forms.FormErrorMixin, forms.Form):
    first_name = forms.CharField(
        error_messages={
            "required": "Enter your first name",
        },
        label="First name",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "given-name",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    last_name = forms.CharField(
        error_messages={
            "required": "Enter your last name",
        },
        label="Last name",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "family-name",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    email = forms.EmailField(
        error_messages={
            "required": "Enter your email address",
        },
        help_text="We'll only use this to send you a receipt",
        label="Email address",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "email",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    on_behalf_of = forms.TypedChoiceField(
        coerce=coerce_choice(OnBehalfOfChoices),
        choices=OnBehalfOfChoices.choices,
        error_messages={
            "required": "Select who this enquiry is for",
        },
        label="Who is this enquiry for?",
        widget=gds_fields.RadioSelect,
    )

    def get_zendesk_data(self):
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        email = self.cleaned_data["email"]
        on_behalf_of = self.cleaned_data["on_behalf_of"].label

        return {
            "email": email,
            "full_name": f"{first_name} {last_name}",
            "on_behalf_of": on_behalf_of,
        }


class CompanyTypeChoices(models.IntegerChoices):
    PRIVATE_OR_LIMITED = 1, "UK private or public limited company"
    OTHER = 2, "Other type of UK organisation"


class BusinessDetailsForm(gds_forms.FormErrorMixin, forms.Form):
    company_type = forms.TypedChoiceField(
        coerce=coerce_choice(CompanyTypeChoices),
        choices=CompanyTypeChoices.choices,
        error_messages={
            "required": "Select the business type",
        },
        help_text="Understanding your business type will help us improve this service.",
        label="Business type",
        widget=gds_fields.RadioSelect,
    )
    type_of_organisation = forms.CharField(
        label="Type of organisation",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input",
            },
        ),
    )
    company_name = forms.CharField(
        error_messages={
            "required": "Enter the business name",
        },
        help_text="Knowing details about your business will help us direct you to the right team for help.",
        label="Business name",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "organization",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_post_code = forms.CharField(
        error_messages={
            "required": "Enter the business unit postcode",
        },
        help_text="Knowing where you are enquiring from means we can direct you to local support if appropriate. Enter a postcode for example SW1A 2DY.",  # noqa: E501
        label="Business unit postcode",
        validators=[
            validators.RegexValidator(
                regex=re.compile(
                    r"^(([A-Z]{1,2}[0-9][A-Z0-9]?|ASCN|STHL|TDCU|BBND|[BFS]IQQ|PCRN|TKCA) ?[0-9][A-Z]{2}|BFPO ?[0-9]{1,4}|(KY[0-9]|MSR|VG|AI)[ -]?[0-9]{4}|[A-Z]{2} ?[0-9]{2}|GE ?CX|GIR ?0A{2}|SAN ?TA1)$",  # noqa: E501
                    re.IGNORECASE,
                ),
                message="Enter a valid postcode",
            ),
        ],
        widget=forms.TextInput(
            attrs={
                "autocomplete": "postal-code",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_registration_number = forms.CharField(
        help_text=mark_safe(
            "Information about your company helps us to improve how we answer your query. Find your number using <a class='govuk-link' href='https://www.gov.uk/get-information-about-a-company' target='_blank'>Get information about a company</a>."  # noqa: E501
        ),
        label="Company Registration Number",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )

    def clean_company_post_code(self):
        company_post_code = self.cleaned_data["company_post_code"]
        return company_post_code.upper()

    def clean(self):
        cleaned_data = super().clean()

        try:
            company_type = self.cleaned_data["company_type"]
        except KeyError:
            return cleaned_data

        company_type = self.cleaned_data["company_type"]
        type_of_organisation = self.cleaned_data["type_of_organisation"]

        is_other_company_type = company_type == CompanyTypeChoices.OTHER
        is_type_organisation_blank = not type_of_organisation.strip()

        if is_other_company_type and is_type_organisation_blank:
            self.add_error(
                "type_of_organisation",
                "Enter the type of organisation",
            )

        return cleaned_data

    def get_zendesk_data(self):
        company_type = self.cleaned_data["company_type"].label
        type_of_organisation = self.cleaned_data["type_of_organisation"]
        company_name = self.cleaned_data["company_name"]
        company_post_code = self.cleaned_data["company_post_code"]
        company_registration_number = self.cleaned_data["company_registration_number"]

        return {
            "company_type": company_type,
            "company_type_of_organisation": type_of_organisation,
            "company_name": company_name,
            "company_post_code": company_post_code,
            "company_registration_number": company_registration_number,
        }


class CompanyTurnoverChoices(models.TextChoices):
    BELOW_85000 = "0_85000__ess_turnover_1", "Below £85,000"
    FROM_85000_TO_499999 = "85000_499999__ess_turnover_1", "£85,000 to £499,999"
    FROM_500000_TO_49999999 = (
        "500000_49999999__ess_turnover_1",
        "£500,000 to £49,999,999",
    )
    OVER_50000000 = "50000000__ess_turnover_1", "£50,000,000+"
    DO_NOT_KNOW = "dont_know__ess_turnover_1", "I don't know"
    PREFER_NOT_TO_SAY = "not_given__ess_turnover_1", "I'd prefer not to say"


class NumberOfEmployeesChoices(models.TextChoices):
    FEWER_THAN_10 = "0_10__ess_num_of_employees_1", "Fewer than 10"
    FROM_10_TO_49 = "10_49__ess_num_of_employees_1", "10 - 49"
    FROM_50_TO_249 = "50_249__ess_num_of_employees_1", "50 - 249"
    OVER_250 = "250__ess_num_of_employees_1", "250 or more"
    DO_NOT_KNOW = "unknown__ess_num_of_employees_1", "I don't know"
    PREFER_NOT_TO_SAY = (
        "prefer_not_to_say__ess_num_of_employees_1",
        "I'd prefer not to say",
    )


class BusinessSizeForm(forms.Form):
    company_turnover = forms.TypedChoiceField(
        choices=[("", "Please select")] + CompanyTurnoverChoices.choices,
        coerce=coerce_choice(CompanyTurnoverChoices),
        error_messages={
            "required": "Select the UK business turnover",
        },
        help_text="Different levels of support may be available depending on the size of the business.",
        label="UK business turnover (last financial year)",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
            },
        ),
    )
    number_of_employees = forms.TypedChoiceField(
        choices=[("", "Please select")] + NumberOfEmployeesChoices.choices,
        coerce=coerce_choice(NumberOfEmployeesChoices),
        error_messages={
            "required": "Select the number of UK employees",
        },
        help_text="Knowing about the size of the business will help us direct you to the most suitable adviser.",
        label="Number of UK employees",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
            },
        ),
    )

    def get_zendesk_data(self):
        company_turnover = self.cleaned_data["company_turnover"].label
        number_of_employees = self.cleaned_data["number_of_employees"].label

        return {
            "company_turnover": company_turnover,
            "number_of_employees": number_of_employees,
        }


class SectorsForm(forms.Form):
    sectors = forms.MultipleChoiceField(
        choices=SECTORS_MAP.items(),
        label="Which industry or business area does your enquiry relate to?",
        required=False,
        widget=gds_fields.CheckboxSelectMultiple,
    )
    other = forms.CharField(
        label="Other industry or business area",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input",
            },
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        has_sectors = bool(cleaned_data["sectors"])
        other = cleaned_data["other"]

        if not has_sectors and not other:
            self.add_error(
                "sectors",
                "Select the industry or business area(s) your enquiry relates to",
            )

        return cleaned_data

    def get_zendesk_data(self):
        sectors = self.cleaned_data["sectors"]
        sectors = ", ".join(SECTORS_MAP[sector] for sector in sectors)
        other_sector = self.cleaned_data["other"]

        return {
            "sectors": sectors,
            "other_sector": other_sector,
        }


class EnquiryDetailsForm(gds_forms.FormErrorMixin, forms.Form):
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
        error_messages={
            "required": "Enter your enquiry",
        },
        label="Your enquiry",
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": 10,
            },
        ),
    )

    def get_zendesk_data(self):
        nature_of_enquiry = self.cleaned_data["nature_of_enquiry"]
        question = self.cleaned_data["question"]

        return {
            "nature_of_enquiry": nature_of_enquiry,
            "question": question,
        }


class ZendeskForm(ZendeskAPIForm):
    FIELD_MAPPING = {
        "question": "aaa_question",
    }

    enquiry_subject = forms.CharField()
    countries = forms.CharField()
    on_behalf_of = forms.CharField()
    company_type = forms.CharField(required=False)
    company_type_of_organisation = forms.CharField(required=False)
    company_name = forms.CharField(required=False)
    company_post_code = forms.CharField(required=False)
    company_registration_number = forms.CharField(required=False)
    company_turnover = forms.CharField(required=False)
    number_of_employees = forms.CharField(required=False)
    sectors = forms.CharField(required=False)
    other_sector = forms.CharField(required=False)
    nature_of_enquiry = forms.CharField(required=False)
    aaa_question = forms.CharField()
    full_name = forms.CharField()
    email = forms.CharField()
    _custom_fields = forms.JSONField(required=False)
