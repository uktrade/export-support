from django import forms

from ..forms import FormErrorMixin


class MixedInFormWithoutClasses(FormErrorMixin, forms.Form):
    char_field = forms.CharField()
    boolean_field = forms.BooleanField()


class MixedInFormWithClasses(FormErrorMixin, forms.Form):
    char_field = forms.CharField(widget=forms.TextInput(attrs={"class": "special"}))
    boolean_field = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "special"})
    )


def test_form_error_mixin():
    form = MixedInFormWithoutClasses(
        data={
            "char_field": "foo",
            "boolean_field": True,
        }
    )
    assert form.is_valid()
    assert form.fields["char_field"].widget.attrs.get("class") is None
    assert form.fields["boolean_field"].widget.attrs.get("class") is None

    form = MixedInFormWithoutClasses(data={})
    assert not form.is_valid()
    assert form.fields["char_field"].widget.attrs["class"] == "govuk-input--error"
    assert form.fields["boolean_field"].widget.attrs.get("class") is None

    form = MixedInFormWithClasses(
        data={
            "char_field": "foo",
            "boolean_field": True,
        }
    )
    assert form.is_valid()
    assert form.fields["char_field"].widget.attrs["class"] == "special"
    assert form.fields["boolean_field"].widget.attrs["class"] == "special"

    form = MixedInFormWithClasses(data={})
    assert not form.is_valid()
    assert (
        form.fields["char_field"].widget.attrs["class"] == "special govuk-input--error"
    )
    assert form.fields["boolean_field"].widget.attrs["class"] == "special"
