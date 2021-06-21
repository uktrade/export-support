from django import forms
from django.db import models

from export_support.gds import fields as gds_fields


class EnquirySubjectChoices(models.IntegerChoices):
    SELLING_GOODS_ABROAD = 1, "Selling goods abroad"
    SELLING_SERVICES_ABROAD = 2, "Selling services abroad"
    IMPORTING_GOODS_TO_THE_UK = 3, "Importing goods to the UK"


class EnquirySubjectForm(forms.Form):
    enquiry_subject = forms.TypedMultipleChoiceField(
        coerce=lambda choice: EnquirySubjectChoices(int(choice)),
        choices=EnquirySubjectChoices.choices,
        label="What is your enquiry about?",
        required=True,
        widget=gds_fields.CheckboxSelectMultiple,
    )


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
