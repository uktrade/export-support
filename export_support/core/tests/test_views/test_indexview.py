import pytest
from django.test import override_settings
from django.urls import reverse

from export_support.core.models import FormTypeCounter


# test invex view
@pytest.mark.django_db
@override_settings(AB_TESTING_ENABLED=False)
def test_indexview_ab_disabled(client):
    # when ab is disabled the form counters should be ignored

    response = client.get(reverse("core:index"))
    assert response.status_code == 302
    assert response.url == reverse("core:enquiry-wizard")

    counter_count = FormTypeCounter.objects.count()
    assert counter_count == 0

    response = client.get(reverse("core:index"))
    assert response.status_code == 302
    assert response.url == reverse("core:enquiry-wizard")


@pytest.mark.django_db
@override_settings(AB_TESTING_ENABLED=True)
def test_indexview_ab_enabled(client):
    # when ab testing is enabled the form should match
    # the correct form type

    counter_count = FormTypeCounter.objects.count()
    assert counter_count == 0

    response = client.get(reverse("core:index"))
    assert response.status_code == 302
    assert response.url == reverse("core:enquiry-wizard")

    form_counters = FormTypeCounter.objects.all()
    assert form_counters.count() == 1
    assert form_counters[0].form_type == "long"

    response = client.get(reverse("core:index"))
    assert response.status_code == 302
    assert response.url == reverse("core:enquiry-wizard-short")

    form_counters = FormTypeCounter.objects.all()
    assert form_counters.count() == 2
    assert form_counters[1].form_type == "short"

    response = client.get(reverse("core:index"))
    assert response.status_code == 302
    assert response.url == reverse("core:enquiry-wizard")

    form_counters = FormTypeCounter.objects.all()
    assert form_counters.count() == 3
    assert form_counters[2].form_type == "long"
