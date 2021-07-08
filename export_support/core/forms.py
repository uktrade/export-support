from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.safestring import mark_safe

from export_support.gds import fields as gds_fields

from .consts import EU_COUNTRY_CODES_TO_NAME_MAP


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


class ExportDestinationChoices(models.IntegerChoices):
    EU = 1, "Selling from the UK to an EU country"
    NON_EU = 2, "Selling from the UK to a non-EU country"


class ExportDestinationForm(forms.Form):
    export_destination = forms.TypedChoiceField(
        coerce=lambda choice: ExportDestinationChoices(int(choice)),
        choices=ExportDestinationChoices.choices,
        label="Where are you selling to?",
        widget=gds_fields.RadioSelect,
    )

    def get_filter_data(self):
        return {}


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
            for code, country_name in EU_COUNTRY_CODES_TO_NAME_MAP.items()
        ],
        label="Which country are you selling to?",
        required=False,
        widget=gds_fields.CheckboxSelectMultiple,
    )

    def clean(self):
        cleaned_data = super().clean()

        has_select_all_selected = bool(cleaned_data["select_all"])
        has_countries_selected = any(cleaned_data["countries"])

        if not has_select_all_selected and not has_countries_selected:
            raise ValidationError(
                'You must select either "Select all" or some countries'
            )

        if has_select_all_selected and has_countries_selected:
            raise ValidationError(
                'You must select either "Select all" or some countries. Not both.'
            )


class EnquiryContactForm(forms.Form):
    # Personal details
    first_name = forms.CharField(
        label="First name",
        widget=gds_fields.TextInput,
    )
    last_name = forms.CharField(
        label="Last name",
        widget=gds_fields.TextInput,
    )
    email = forms.EmailField(
        label="Email",
        widget=gds_fields.EmailInput,
    )

    # Business details
    company_type = forms.ChoiceField(
        choices=(
            (
                "UK private or public limited company",
                "UK private or public limited company",
            ),
            ("Other type of UK organisation", "Other type of UK organisation"),
        ),
        label="Company type",
        widget=gds_fields.RadioSelect,
    )
    company_or_organisation_name = forms.CharField(
        label="Company or Organisation name",
        widget=gds_fields.TextInput,
    )
    company_registration_number = forms.CharField(
        label=mark_safe(
            'Company Registration Number CRN <span class="gds-form__label__optional">(optional)</span>'
        ),
        required=False,
        widget=gds_fields.TextInput,
    )

    # Comment
    comment = forms.CharField(
        label="Tell us how we can help",
        help_text=mark_safe(
            'Provide as much detail as possible below to help us better understand your enquiry. <strong class="gds-form__help_text__warning">Please do not share any commercially sensitive information</strong>.'
        ),
        widget=gds_fields.Textarea,
    )
