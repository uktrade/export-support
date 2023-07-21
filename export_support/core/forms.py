import logging

from directory_forms_api_client.forms import ZendeskAPIForm
from django import forms
from django.db import models
from django.utils.html import format_html

from export_support.gds import fields as gds_fields
from export_support.gds import forms as gds_forms

from .consts import COUNTRIES_MAP, SECTORS_MAP
from .validators import postcode_validator

logger = logging.getLogger(__name__)


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


class BaseForm(gds_forms.FormErrorMixin, forms.Form):
    def get_zendesk_data(self):
        return {}


class HaveYouExportedBeforeChoices(models.TextChoices):
    YES_LAST_YEAR = "in_the_last_year__ess_experience", "Yes, in the last year"
    YES_MORE_ONE_YEAR = (
        "more_than_a_year_ago__ess_experience",
        "Yes, more than a year ago",
    )
    NO = "not_exported__ess_experience", "No"


class DoYouHaveAProductYouWantToExportChoices(models.TextChoices):
    YES = "product_ready__ess_experience", "Yes"
    NO = "no_product_ready__ess_experience", "No"


class HaveYouExportedBeforeMixin(BaseForm):
    """Mixin class to provide the 'have_you_exported_before' and
    'do_you_have_a_product_you_want_to_export' fields and associated clean method.
    """

    have_you_exported_before = forms.TypedChoiceField(
        choices=HaveYouExportedBeforeChoices.choices,
        coerce=coerce_choice(HaveYouExportedBeforeChoices),
        error_messages={
            "required": "Select whether you have exported before",
        },
        label="Have you exported before?",
        widget=gds_fields.RadioSelect,
    )

    do_you_have_a_product_you_want_to_export = forms.TypedChoiceField(
        choices=DoYouHaveAProductYouWantToExportChoices.choices,
        coerce=coerce_choice(DoYouHaveAProductYouWantToExportChoices),
        label="Do you have a product you'd like to export?",
        widget=gds_fields.RadioSelect,
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get(
            "have_you_exported_before"
        ) == HaveYouExportedBeforeChoices.NO and not cleaned_data.get(
            "do_you_have_a_product_you_want_to_export"
        ):
            self.add_error(
                "do_you_have_a_product_you_want_to_export",
                "Select yes if you have a product you’d like to export",
            )

        return cleaned_data

    def get_zendesk_data(self):
        zendesk_data = super().get_zendesk_data()
        have_you_exported_before = self.cleaned_data["have_you_exported_before"].label

        if (
            self.cleaned_data["have_you_exported_before"].value
            == "not_exported__ess_experience"
        ):
            do_you_have_a_product_you_want_to_export = self.cleaned_data[
                "do_you_have_a_product_you_want_to_export"
            ].label
        else:
            do_you_have_a_product_you_want_to_export = ""

        zendesk_data.update(
            {
                "have_you_exported_before": have_you_exported_before,
                "do_you_have_a_product_you_want_to_export": do_you_have_a_product_you_want_to_export,
            }
        )

        return zendesk_data


class PositivityForGrowthChoices(models.TextChoices):
    VERY_POSITIVE = "very_positive__ess_positivity", "Very positive"
    QUITE_POSITIVE = "quite_positive__ess_positivity", "Quite positive"
    NEUTRAL = "neutral__ess_positivity", "Neutral"
    QUITE_NEGATIVE = "quite_negative__ess_positivity", "Quite negative"
    VERY_NEGATIVE = "very_negative__ess_positivity", "Very negative"


class PositivityForGrowthMixin(BaseForm):
    """Mixin class to provide the 'positivity_for_growth' field and associated clean method."""

    positivity_for_growth = forms.TypedChoiceField(
        choices=PositivityForGrowthChoices.choices,
        coerce=coerce_choice(PositivityForGrowthChoices),
        label="How positive do you feel about growing your business overseas?",
        widget=gds_fields.RadioSelect,
        error_messages={
            "required": "Select how positive you feel about growing your business overseas",
        },
    )

    def get_zendesk_data(self):
        zendesk_data = super().get_zendesk_data()
        positivity_for_growth = self.cleaned_data["positivity_for_growth"].label

        zendesk_data.update(
            {
                "positivity_for_growth": positivity_for_growth,
            }
        )

        return zendesk_data


class EnquirySubjectChoices(models.IntegerChoices):
    SELLING_GOODS_ABROAD = 1, "Selling goods abroad"
    SELLING_SERVICES_ABROAD = 2, "Selling services abroad"


class EnquirySubjectForm(gds_forms.FormErrorMixin, forms.Form):
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


class ExportCountriesForm(gds_forms.FormErrorMixin, forms.Form):
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
    no_specific_country = forms.BooleanField(
        label="My query is not related to a specific country",
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "govuk-checkboxes__input"},
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        has_select_all_selected = bool(cleaned_data["select_all"])

        has_no_specific_selected = bool(cleaned_data["no_specific_country"])

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

        if (
            has_select_all_selected
            and has_all_countries_selected
            and not has_no_specific_selected
        ):
            return cleaned_data

        # if has_no_specific_selected is true, we need to set the Zendesk identifiable code
        if (
            has_no_specific_selected
            and not has_select_all_selected
            and not has_countries_selected
        ):
            cleaned_data["countries"] = ["No specific country"]

        if (
            not has_select_all_selected
            and not has_countries_selected
            and not has_no_specific_selected
        ):
            self.add_error(
                "countries", "Select the country or countries you are selling to"
            )

        if (
            has_select_all_selected
            and has_countries_selected
            and not has_no_specific_selected
        ):
            self.add_error(
                "countries",
                'You must select either "Select all" or some countries not both',
            )

        if has_no_specific_selected and (
            has_select_all_selected or has_countries_selected
        ):
            self.add_error(
                "countries",
                "You must select either some countries or indicate no specific country not both",
            )

        return cleaned_data

    def get_zendesk_data(self):
        countries = self.cleaned_data["countries"]
        if "No specific country" not in countries:
            countries = [COUNTRIES_MAP[code] for code in countries]
        countries = ", ".join(countries)

        return {
            "countries": countries,
        }


class OnBehalfOfChoices(models.IntegerChoices):
    OWN_COMPANY = 1, "The business I own or work for (or in my own interest)"
    ANOTHER_COMPANY = 2, "I am asking on behalf of another business"


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


class BusinessTypeChoices(models.IntegerChoices):
    PRIVATE_OR_LIMITED = 1, "UK private or public limited company"
    OTHER = 2, "Other type of UK organisation"
    SOLE_TRADE_OR_PRIVATE_INDIVIDUAL = 3, "Sole trader or private individual"


class BusinessTypeForm(gds_forms.FormErrorMixin, forms.Form):
    business_type = forms.TypedChoiceField(
        coerce=coerce_choice(BusinessTypeChoices),
        choices=BusinessTypeChoices.choices,
        error_messages={
            "required": "Select the business type",
        },
        help_text="Understanding your business type will help us improve this service.",
        label="Business type",
        widget=gds_fields.RadioSelect,
    )

    def get_zendesk_data(self):
        business_type = self.cleaned_data["business_type"]

        return {
            "company_type_category": business_type.label,
        }


class BusinessDetailsForm(HaveYouExportedBeforeMixin):
    company_name = forms.CharField(
        error_messages={
            "required": "Enter the business name",
        },
        help_text="If your business name is not shown in the search results, then enter it manually.",
        label="Business name",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "organization",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_registration_number = forms.CharField(
        help_text=format_html(
            "Information about your company helps us to improve how we answer your query."
            "<span class='js-hidden'> Find your number using "
            "<a class='govuk-link' href='https://www.gov.uk/get-information-about-a-company' "
            "target='_blank'>Get information about a company<span class='govuk-visually-hidden'> "
            "(opens in new tab)</span></a>.</span>"
        ),
        label="Company Registration Number",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_post_code = forms.CharField(
        error_messages={
            "required": "Enter the business unit postcode",
        },
        help_text="Knowing where you are enquiring from means we can direct you to "
        "local support if appropriate. Enter a postcode for example SW1A 2DY.",
        label="Business unit postcode",
        validators=[postcode_validator],
        widget=forms.TextInput(
            attrs={
                "autocomplete": "postal-code",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )

    def clean_company_post_code(self):
        company_post_code = self.cleaned_data["company_post_code"]
        return company_post_code.upper()

    def get_zendesk_data(self):
        zendesk_data = super().get_zendesk_data()

        company_name = self.cleaned_data["company_name"]
        company_post_code = self.cleaned_data["company_post_code"]
        company_registration_number = self.cleaned_data["company_registration_number"]

        zendesk_data.update(
            {
                "company_name": company_name,
                "company_post_code": company_post_code,
                "company_registration_number": company_registration_number,
            }
        )
        return zendesk_data


class PrivateOrPublicCompanyTypeChoices(models.TextChoices):
    PRIVATE_LIMITED_COMPANY = (
        "private_limited_company__ess_organistation",
        "Private limited company",
    )
    PUBLIC_LIMITED_COMPANY = (
        "public_limited_company__ess_organistation",
        "Public limited company",
    )
    LIMITED_LIABILITY_PARTNERSHIP = (
        "__limited_liability_partnership__",
        "Limited liability partnership",
    )
    NOT_CURRENTLY_TRADING = (
        "not_trading_yet__ess_organistation",
        "Not currently trading",
    )
    CLOSED_BUSINESS = "closed_business__ess_organistation", "Closed business"
    OTHER = "__other__", "Other"


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


class BusinessAdditionalInformationForm(PositivityForGrowthMixin):
    company_type = forms.TypedChoiceField(
        coerce=coerce_choice(PrivateOrPublicCompanyTypeChoices),
        choices=[("", "Please select")] + PrivateOrPublicCompanyTypeChoices.choices,
        error_messages={
            "required": "Select the type of business",
        },
        label="Type of business",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
            },
        ),
    )
    other_type_of_business = forms.CharField(
        label='If "Other", please specify',
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_turnover = forms.TypedChoiceField(
        choices=[("", "Please select")] + CompanyTurnoverChoices.choices,
        coerce=coerce_choice(CompanyTurnoverChoices),
        error_messages={
            "required": "Select the UK business turnover",
        },
        help_text="Different levels of support may be available depending on the size of the business.",
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
        help_text="Knowing about the size of the business will help us direct you to the most suitable adviser.",
        label="Number of UK employees",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
            },
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        try:
            type_of_business = cleaned_data["company_type"]
        except KeyError:
            return cleaned_data

        other_type_of_business = cleaned_data["other_type_of_business"]
        if (
            type_of_business == PrivateOrPublicCompanyTypeChoices.OTHER
            and not other_type_of_business
        ):
            self.add_error(
                "other_type_of_business",
                "Enter the type of business",
            )

        return cleaned_data

    def get_zendesk_data(self):
        zendesk_data = super().get_zendesk_data()
        type_of_business = self.cleaned_data["company_type"]
        company_turnover = self.cleaned_data["company_turnover"].label
        number_of_employees = self.cleaned_data["number_of_employees"].label

        if type_of_business == PrivateOrPublicCompanyTypeChoices.OTHER:
            other_type_of_business = self.cleaned_data["other_type_of_business"]
            type_of_business = other_type_of_business
        else:
            type_of_business = type_of_business.label

        zendesk_data.update(
            {
                "company_type": type_of_business,
                "company_turnover": company_turnover,
                "number_of_employees": number_of_employees,
            }
        )
        return zendesk_data


class OrganisationDetailsForm(HaveYouExportedBeforeMixin):
    company_name = forms.CharField(
        error_messages={
            "required": "Enter the organisation name",
        },
        label="Organisation name",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "organization",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_registration_number = forms.CharField(
        help_text=format_html(
            "If your organisation is registered with Companies House, then its registration number"
            " will help us answer your query. "
            "<a class='govuk-link' href='https://www.gov.uk/get-information-about-a-company' "
            "target='_blank'>Look up a company registration number"
            "<span class='govuk-visually-hidden'> (opens in new tab)</span></a>."
        ),
        label="Company Registration Number",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_post_code = forms.CharField(
        error_messages={
            "required": "Enter the organisation unit postcode",
        },
        help_text="Knowing where you are enquiring from means we can direct you to local support "
        "if appropriate. Enter a postcode for example SW1A 2DY.",
        label="Organisation unit postcode",
        validators=[postcode_validator],
        widget=forms.TextInput(
            attrs={
                "autocomplete": "postal-code",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )

    def clean_company_post_code(self):
        company_post_code = self.cleaned_data["company_post_code"]
        return company_post_code.upper()

    def get_zendesk_data(self):
        zendesk_data = super().get_zendesk_data()

        company_name = self.cleaned_data["company_name"]
        company_registration_number = self.cleaned_data["company_registration_number"]
        company_post_code = self.cleaned_data["company_post_code"]

        zendesk_data.update(
            {
                "company_name": company_name,
                "company_registration_number": company_registration_number,
                "company_post_code": company_post_code,
            }
        )
        return zendesk_data


class OrganisationTypeChoices(models.TextChoices):
    CHARITY_OR_SOCIAL_ENTERPRISE = (
        "charity_social_enterprise__ess_organistation",
        "Charity / Social enterprise",
    )
    UNIVERSITY = "university__ess_organistation", "University"
    OTHER_EDUCATION_INSTITUTION = (
        "other_education_institution__ess_organistation",
        "Other education institution",
    )
    PARTNERSHIP = "partnership__ess_organistation", "Partnership"
    OTHER = "__other__", "Other"


class OrganisationAdditionalInformationForm(PositivityForGrowthMixin):
    company_type = forms.TypedChoiceField(
        coerce=coerce_choice(OrganisationTypeChoices),
        choices=[("", "Please select")] + OrganisationTypeChoices.choices,
        error_messages={
            "required": "Select the type of organisation",
        },
        label="Type of organisation",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
            },
        ),
    )
    other_type_of_organisation = forms.CharField(
        label='If "Other", please specify',
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_turnover = forms.TypedChoiceField(
        choices=[("", "Please select")] + CompanyTurnoverChoices.choices,
        coerce=coerce_choice(CompanyTurnoverChoices),
        error_messages={
            "required": "Select the UK turnover",
        },
        help_text="Different levels of support may be available depending on the size of the organisation.",
        label="UK turnover (last financial year)",
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
        help_text="Knowing about the size of the organisation will help us direct you to the most suitable adviser.",
        label="Number of UK employees",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
            },
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        try:
            type_of_organisation = cleaned_data["company_type"]
        except KeyError:
            return cleaned_data

        other_type_of_organisation = cleaned_data["other_type_of_organisation"]
        if (
            type_of_organisation == OrganisationTypeChoices.OTHER
            and not other_type_of_organisation
        ):
            self.add_error(
                "other_type_of_organisation",
                "Enter the type of organisation",
            )

        return cleaned_data

    def get_zendesk_data(self):
        zendesk_data = super().get_zendesk_data()
        type_of_organisation = self.cleaned_data["company_type"]
        company_turnover = self.cleaned_data["company_turnover"].label
        number_of_employees = self.cleaned_data["number_of_employees"].label

        if type_of_organisation == OrganisationTypeChoices.OTHER:
            other_type_of_organisation = self.cleaned_data["other_type_of_organisation"]
            type_of_organisation = other_type_of_organisation
        else:
            type_of_organisation = type_of_organisation.label

        zendesk_data.update(
            {
                "company_type": type_of_organisation,
                "company_turnover": company_turnover,
                "number_of_employees": number_of_employees,
            }
        )

        return zendesk_data


class SoloExporterDetailsForm(HaveYouExportedBeforeMixin):
    company_name = forms.CharField(
        error_messages={
            "required": "Enter the business name",
        },
        help_text="If you have a trading name, then enter it here.",
        label="Business name",
        required=False,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "organization",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_post_code = forms.CharField(
        error_messages={
            "required": "Enter the postcode",
        },
        help_text="Knowing where you are enquiring from means we can direct you to local support "
        "if appropriate. Enter a postcode for example SW1A 2DY.",
        label="Postcode",
        validators=[postcode_validator],
        widget=forms.TextInput(
            attrs={
                "autocomplete": "postal-code",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )

    def get_zendesk_data(self):
        zendesk_data = super().get_zendesk_data()
        company_name = self.cleaned_data["company_name"]
        company_post_code = self.cleaned_data["company_post_code"]

        zendesk_data.update(
            {
                "company_name": company_name,
                "company_post_code": company_post_code,
            }
        )
        return zendesk_data


class SoloExporterTypeChoices(models.TextChoices):
    SOLE_TRADER = "soletrader__ess_organistation", "Sole trader"
    PRIVATE_INDIVIDUAL = "__private_individual__", "Private individual"
    OTHER = "__other__", "Other"


class SoloExporterAdditionalInformationForm(PositivityForGrowthMixin):
    company_type = forms.TypedChoiceField(
        coerce=coerce_choice(SoloExporterTypeChoices),
        choices=[("", "Please select")] + SoloExporterTypeChoices.choices,
        error_messages={
            "required": "Select the type of exporter",
        },
        label="Type of exporter",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
            },
        ),
    )
    other_type_of_exporter = forms.CharField(
        label='If "Other", please specify',
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_turnover = forms.TypedChoiceField(
        choices=[("", "Please select")] + CompanyTurnoverChoices.choices,
        coerce=coerce_choice(CompanyTurnoverChoices),
        help_text="Select your business turnover for the last financial year (if applicable).",
        label="Business turnover",
        required=False,
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
            },
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        try:
            type_of_exporter = cleaned_data["company_type"]
        except KeyError:
            return cleaned_data

        other_type_of_exporter = cleaned_data["other_type_of_exporter"]
        if (
            type_of_exporter == SoloExporterTypeChoices.OTHER
            and not other_type_of_exporter
        ):
            self.add_error(
                "other_type_of_exporter",
                "Enter the type of exporter",
            )

        cleaned_data["number_of_employees"] = NumberOfEmployeesChoices.FEWER_THAN_10

        return cleaned_data

    def get_zendesk_data(self):
        zendesk_data = super().get_zendesk_data()
        type_of_exporter = self.cleaned_data["company_type"]
        number_of_employees = self.cleaned_data["number_of_employees"].label

        company_turnover = self.cleaned_data["company_turnover"]
        if isinstance(company_turnover, CompanyTurnoverChoices):
            company_turnover = company_turnover.label

        if type_of_exporter == SoloExporterTypeChoices.OTHER:
            other_type_of_exporter = self.cleaned_data["other_type_of_exporter"]
            type_of_exporter = other_type_of_exporter
        else:
            type_of_exporter = type_of_exporter.label

        zendesk_data.update(
            {
                "company_type": type_of_exporter,
                "company_turnover": company_turnover,
                "number_of_employees": number_of_employees,
            }
        )

        return zendesk_data


class SectorsForm(gds_forms.FormErrorMixin, forms.Form):
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


class HowDidYouHearAboutThisServiceChoices(models.TextChoices):
    SEARCH_ENGINE = "search_enging__ess_acquisition", "Search engine"
    LINKED_IN = "linkedin__ess_acquisition", "LinkedIn"
    TWITTER = "twitter__ess_acquisition", "Twitter"
    FACEBOOK = "facebook__ess_acquisition", "Facebook"
    RADIO_ADVERT = "radio_advert__ess_acquisition", "Radio advert"
    NGO = "ngo__ess_acquisition", "Non-government organisation - such as a trade body"
    NEWS_ARTICLE = "news_article__ess_acquisition", "News article"
    ONLINE_ADVERT = "online_advert__ess_acquisition", "Online advert"
    PRINT_ADVERT = "print_advert__ess_acquisition", "Print advert"
    OTHER = "other__ess_acquisition", "Other"


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
    how_did_you_hear_about_this_service = forms.TypedChoiceField(
        choices=[("", "Please select")] + HowDidYouHearAboutThisServiceChoices.choices,
        coerce=coerce_choice(HowDidYouHearAboutThisServiceChoices),
        error_messages={
            "required": "Select how you heard about this service",
        },
        label="How did you hear about this service?",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
            },
        ),
    )
    other_how_did_you_hear_about_this_service = forms.CharField(
        label='If "Other", please specify',
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input",
            },
        ),
    )
    email_consent = forms.BooleanField(
        label="I would like to receive additional information by email",
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "govuk-checkboxes__input"},
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        try:
            how_did_you_hear_about_this_service = cleaned_data[
                "how_did_you_hear_about_this_service"
            ]
        except KeyError:
            return cleaned_data

        is_how_did_you_hear_other_selected = (
            how_did_you_hear_about_this_service
            == HowDidYouHearAboutThisServiceChoices.OTHER
        )
        other_how_did_you_hear_about_this_service = cleaned_data[
            "other_how_did_you_hear_about_this_service"
        ].strip()

        if (
            is_how_did_you_hear_other_selected
            and not other_how_did_you_hear_about_this_service
        ):
            self.add_error(
                "other_how_did_you_hear_about_this_service",
                "Enter how you heard about this service",
            )

        return cleaned_data

    def get_zendesk_data(self):
        nature_of_enquiry = self.cleaned_data["nature_of_enquiry"]
        question = self.cleaned_data["question"]
        how_did_you_hear_about_this_service = self.cleaned_data[
            "how_did_you_hear_about_this_service"
        ]
        email_consent = self.cleaned_data["email_consent"]

        if (
            how_did_you_hear_about_this_service
            == HowDidYouHearAboutThisServiceChoices.OTHER
        ):
            other_how_did_you_hear_about_this_service = self.cleaned_data[
                "other_how_did_you_hear_about_this_service"
            ]
            how_did_you_hear_about_this_service = (
                other_how_did_you_hear_about_this_service
            )
        else:
            how_did_you_hear_about_this_service = (
                how_did_you_hear_about_this_service.label
            )

        return {
            "nature_of_enquiry": nature_of_enquiry,
            "question": question,
            "how_did_you_hear_about_this_service": how_did_you_hear_about_this_service,
            "marketing_consent": email_consent,
        }


class RussiaUkraineEnquiryForm(gds_forms.FormErrorMixin, forms.Form):
    full_name = forms.CharField(
        error_messages={
            "required": "Enter your full name",
        },
        label="Full name",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "given-name",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    company_name = forms.CharField(
        error_messages={
            "required": "Enter the business name",
        },
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
        help_text="If your business has multiple locations, enter the postcode for the business "
        "unit you are enquiring from.",
        label="Postcode",
        validators=[postcode_validator],
        widget=forms.TextInput(
            attrs={
                "autocomplete": "postal-code",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    email = forms.EmailField(
        error_messages={
            "required": "Enter your email address",
        },
        label="Email address",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "email",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
    phone = forms.RegexField(
        regex=r"[0-9]+$",
        max_length=(12),
        error_messages={
            "required": "Enter your telephone number",
            "invalid": "This value can only contain numbers",
        },
        label="Telephone",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "phone",
                "class": "govuk-input govuk-!-width-one-half",
            },
        ),
    )
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
    question = forms.CharField(
        error_messages={
            "required": "Enter your enquiry",
        },
        label="Your question",
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": 10,
            },
        ),
    )
    email_consent = forms.BooleanField(
        label="I would like to receive additional information by email",
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "govuk-checkboxes__input"},
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
        full_name = self.cleaned_data["full_name"]
        email = self.cleaned_data["email"]
        phone = self.cleaned_data["phone"]
        company_name = self.cleaned_data["company_name"]
        company_post_code = self.cleaned_data["company_post_code"]
        question = self.cleaned_data["question"]
        email_consent = self.cleaned_data["email_consent"]
        sectors = self.cleaned_data["sectors"]
        sectors = ", ".join(SECTORS_MAP[sector] for sector in sectors)
        other_sector = self.cleaned_data["other"]

        return {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "company_name": company_name,
            "company_post_code": company_post_code,
            "sectors": sectors,
            "other_sector": other_sector,
            "question": question,
            "email_consent": email_consent,
            "enquiry_subject": "-",
            "countries": "Russia, Ukraine",
            "on_behalf_of": "-",
            "company_type": "-",
            "company_type_category": "-",
            "how_did_you_hear_about_this_service": "-",
        }


class ZendeskForm(ZendeskAPIForm):
    FIELD_MAPPING = {
        "question": "aaa_question",
    }

    enquiry_subject = forms.CharField()
    countries = forms.CharField()
    on_behalf_of = forms.CharField()
    company_type = forms.CharField()
    company_type_category = forms.CharField()
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
    how_did_you_hear_about_this_service = forms.CharField()
    marketing_consent = forms.BooleanField(required=False)
    have_you_exported_before = forms.CharField(required=False)
    do_you_have_a_product_you_want_to_export = forms.CharField(required=False)
    positivity_for_growth = forms.CharField(required=False)

    _custom_fields = forms.JSONField(required=False)


class RussiaUkraineZendeskForm(ZendeskAPIForm):
    FIELD_MAPPING = {
        "question": "aaa_question",
    }

    enquiry_subject = forms.CharField()
    countries = forms.CharField()
    on_behalf_of = forms.CharField()
    company_type = forms.CharField()
    company_type_category = forms.CharField()
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
    how_did_you_hear_about_this_service = forms.CharField()
    marketing_consent = forms.BooleanField(required=False)
    phone = forms.CharField(required=False)
    _custom_fields = forms.JSONField(required=False)
