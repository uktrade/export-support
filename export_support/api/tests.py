import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_companies_search(client, mocker):
    mock_search_companies = mocker.patch("export_support.api.views.search_companies")
    url = reverse("api:company-search")

    mock_search_companies.return_value = {}
    response = client.get(url)
    mock_search_companies.assert_not_called()
    assert response.json() == {"results": {}}

    mock_search_companies.return_value = {
        "testing": [1, 2, 3],
    }
    response = client.get(f"{url}?q=test")
    mock_search_companies.assert_called_with("test")
    assert response.json() == {"results": {"testing": [1, 2, 3]}}
