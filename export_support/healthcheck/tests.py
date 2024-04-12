import pytest
from django.urls import reverse
from requests_mock import ANY as ANY_URL

from .views import HealthCheckError


def test_healthcheck_success(client, settings, mocker, requests_mock):
    mock_middleware_time = mocker.patch("export_support.healthcheck.middleware.time")
    start_time = 123456788.0
    mock_middleware_time.time.return_value = start_time

    mock_view_time = mocker.patch("export_support.healthcheck.views.time")
    now = 123456789.0
    mock_view_time.time.return_value = now

    directory_forms_api_healthcheck_url = "http://example.com/healthcheck"
    settings.DIRECTORY_FORMS_API_HEALTHCHECK_URL = "http://example.com/healthcheck"
    requests_mock.get(directory_forms_api_healthcheck_url)

    requests_mock.get("https://api.companieshouse.gov.uk/search/companies")

    url = reverse("healthcheck:companies-house")
    response = client.get(url)

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/xml"
    assert response.content == bytes(
        f"""<pingdom_http_custom_check>
    <status>OK</status>
    <response_time>{now - start_time}</response_time>
</pingdom_http_custom_check>
""".encode(
            "utf-8"
        )
    )


def test_healthcheck_directory_forms_api_failure(client, settings, requests_mock):
    requests_mock.get(ANY_URL)

    directory_forms_api_healthcheck_url = (
        "http://example.com/healthcheck/directory-forms"
    )
    settings.DIRECTORY_FORMS_API_HEALTHCHECK_URL = (
        "http://example.com/healthcheck/directory-forms"
    )
    requests_mock.get(directory_forms_api_healthcheck_url, status_code=404)

    url = reverse("healthcheck:directory-forms")
    with pytest.raises(HealthCheckError):
        client.get(url)


def test_healthcheck_companies_house_failure(client, requests_mock):
    requests_mock.get(ANY_URL)

    companies_house_url = "https://api.companieshouse.gov.uk/search/companies"

    requests_mock.get(companies_house_url, status_code=404)
    url = reverse("healthcheck:companies-house")
    with pytest.raises(HealthCheckError):
        client.get(url)

    requests_mock.get(companies_house_url, status_code=403)
    url = reverse("healthcheck:companies-house")
    with pytest.raises(HealthCheckError):
        client.get(url)
