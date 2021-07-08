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
        has_all_countries_selected = [
            code for code, _ in self.fields["countries"].choices
        ] == cleaned_data["countries"]

        if has_select_all_selected and has_all_countries_selected:
            return

        if not has_select_all_selected and not has_countries_selected:
            raise ValidationError(
                'You must select either "Select all" or some countries'
            )

        if has_select_all_selected and has_countries_selected:
            raise ValidationError(
                'You must select either "Select all" or some countries. Not both.'
            )


class OnBehalfOfChoices(models.IntegerChoices):
    OWN_COMPANY = 1, "The company I own or work for"
    ANOTHER_COMPANY = 2, "I am asking on behalf of another company"
    NOT_A_COMPANY = 3, "This enquiry does not relate to a company"


class PersonalDetailsForm(forms.Form):
    first_name = forms.CharField(
        label="First name",
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            }
        ),
    )
    last_name = forms.CharField(
        label="Last name",
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            }
        ),
    )
    email = forms.EmailField(
        label="Email address",
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input govuk-!-width-one-half",
            }
        ),
    )
    on_behalf_of = forms.TypedChoiceField(
        coerce=lambda choice: ExportDestinationChoices(int(choice)),
        choices=OnBehalfOfChoices.choices,
        label="Who is this enquiry for?",
        widget=gds_fields.RadioSelect,
    )
