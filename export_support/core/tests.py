from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed


def test_index_view(client):
    response = client.get(reverse("core:index"))
    assert response.status_code == 302
    assert response.url == reverse("core:enquiry-wizard")


def test_privacy_view(client):
    response = client.get(reverse("core:privacy"))
    assert response.status_code == 200
    assertTemplateUsed(response, "core/privacy.html")
