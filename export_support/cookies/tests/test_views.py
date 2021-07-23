from django.urls import reverse


def test_prev_page_allowed_path(client):
    url = reverse("cookies:cookies-preferences")
    response = client.get(f"{url}?from=/next-url/")
    assert response.status_code == 200
    assert response.context["prev_page"] == "/next-url/"

    url = reverse("cookies:cookies-preferences")
    response = client.get(f"{url}?from=http://testserver/next-url/")
    assert response.status_code == 200
    assert response.context["prev_page"] == "http://testserver/next-url/"


def test_prev_page_different_host(client, settings):
    url = reverse("cookies:cookies-preferences")
    response = client.get(f"{url}?from=http://not-the-same.com/next/")
    assert response.status_code == 200
    assert response.context["prev_page"] == "/"


def test_prev_page_different_scheme(client, settings):
    url = reverse("cookies:cookies-preferences")
    response = client.get(f"{url}?from=https://test-server/next/")
    assert response.status_code == 200
    assert response.context["prev_page"] == "/"
