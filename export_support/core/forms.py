from django import forms
from django.db import models
from django.utils.safestring import mark_safe

from export_support.gds import fields as gds_fields


class EnquirySubjectChoices(models.IntegerChoices):
    SELLING_GOODS_ABROAD = 1, "Selling goods abroad"
    SELLING_SERVICES_ABROAD = 2, "Selling services abroad"


class EnquirySubjectForm(forms.Form):
    enquiry_subject = forms.TypedMultipleChoiceField(
        coerce=lambda choice: EnquirySubjectChoices(int(choice)),
        choices=EnquirySubjectChoices.choices,
        label="What is your enquiry about?",
        required=True,
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
        required=True,
        widget=gds_fields.RadioSelect,
    )

    def get_filter_data(self):
        return {}


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
