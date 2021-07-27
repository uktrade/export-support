import pytest
from django.urls import reverse


def test_healthcheck_success(client, settings, mocker):
    mock_urllib = mocker.patch("export_support.healthcheck.views.urllib")
    mock_urllib.request.urlopen.return_value = None

    mock_middleware_time = mocker.patch("export_support.healthcheck.middleware.time")
    start_time = 123456788.0
    mock_middleware_time.time.return_value = start_time

    mock_view_time = mocker.patch("export_support.healthcheck.views.time")
    now = 123456789.0
    mock_view_time.time.return_value = now

    settings.DIRECTORY_FORMS_API_HEALTHCHECK_URL = "http://example.com/healthcheck"

    url = reverse("healthcheck:healthcheck")
    response = client.get(url)

    assert mock_urllib.request.urlopen.called_with(
        settings.DIRECTORY_FORMS_API_HEALTHCHECK_URL
    )

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


def test_healthcheck_directory_forms_api_failure(client, settings, mocker):
    mock_urllib = mocker.patch("export_support.healthcheck.views.urllib")
    mock_urllib.request.urlopen.side_effect = Exception

    settings.DIRECTORY_FORMS_API_HEALTHCHECK_URL = "http://example.com/healthcheck"

    url = reverse("healthcheck:healthcheck")
    with pytest.raises(Exception):
        client.get(url)

    assert mock_urllib.request.urlopen.called_with(
        settings.DIRECTORY_FORMS_API_HEALTHCHECK_URL
    )
