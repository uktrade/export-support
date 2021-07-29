from django import forms


class FormErrorMixin:
    def add_error(self, field, error):
        super().add_error(field, error)

        field = self.fields[field]
        if not isinstance(field, forms.CharField):
            return

        try:
            field.widget.attrs["class"] += " govuk-input--error"
        except KeyError:
            field.widget.attrs["class"] = "govuk-input--error"
