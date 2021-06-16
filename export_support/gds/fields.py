from django import forms


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "gds/forms/fields/checkbox_select_multiple.html"
