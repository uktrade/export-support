from django import forms


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "gds/forms/fields/checkbox_select_multiple.html"


class RadioSelect(forms.RadioSelect):
    template_name = "gds/forms/fields/radio_select.html"


class TextInput(forms.TextInput):
    template_name = "gds/forms/fields/text_input.html"


class EmailInput(forms.EmailInput):
    template_name = "gds/forms/fields/email_input.html"


class Textarea(forms.Textarea):
    template_name = "gds/forms/fields/textarea.html"
