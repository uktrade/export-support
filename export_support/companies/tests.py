from collections import namedtuple

from faker import Faker

from export_support.companies.search import search_companies

fake = Faker()


Company = namedtuple(
    "Company",
    [
        "name",
        "postal_code",
        "company_number",
        "company_status",
        "matches",
    ],
)


def _get_company(company_status="active", matches=None):
    if matches is None:
        matches = ["title"]
    if matches is False:
        matches = None
    return Company(
        name=fake.company(),
        postal_code=fake.postcode(),
        company_number=fake.random_int(),
        company_status=company_status,
        matches=matches,
    )


def _to_result(company):
    result = {
        "title": company.name,
        "address": {
            "postal_code": company.postal_code,
        },
        "company_number": company.company_number,
        "company_status": company.company_status,
    }

    if company.matches is not None:
        result["matches"] = company.matches

    return result


def _to_results(companies):
    return [_to_result(company) for company in companies]


def _to_items(companies):
    return [
        {
            "name": company.name,
            "postcode": company.postal_code,
            "companyNumber": company.company_number,
        }
        for company in companies
    ]


def test_search_companies_less_than_full_page_results(requests_mock):
    companies = [_get_company() for _ in range(2)]

    requests_mock.get(
        "https://api.companieshouse.gov.uk/search/companies?q=test&items_per_page=20&start_index=0",
        json={
            "items": _to_results(companies),
        },
    )

    items = search_companies("test")
    assert items == _to_items(companies)


def test_search_companies_full_page_results(requests_mock):
    companies = [_get_company() for _ in range(20)]

    requests_mock.get(
        "https://api.companieshouse.gov.uk/search/companies?q=test&items_per_page=20&start_index=0",
        json={
            "items": _to_results(companies),
        },
    )

    items = search_companies("test")
    assert items == _to_items(companies)


def test_search_companies_active_company_filtering(requests_mock):
    active = [_get_company()]
    inactive = [_get_company("inactive")]
    companies = active + inactive
    requests_mock.get(
        "https://api.companieshouse.gov.uk/search/companies?q=test&items_per_page=20&start_index=0",
        json={
            "items": _to_results(companies),
        },
    )

    items = search_companies("test")
    assert items == _to_items(active)


def test_search_companies_snippets_filtering(requests_mock):
    include_snippets = [
        _get_company(matches=["title"]),
        _get_company(matches=["address_snippet"]),
        _get_company(matches=["snippet", "address_snippet"]),
    ]
    exclude_snippets = [
        _get_company(matches=False),
        _get_company(matches=[]),
        _get_company(matches=["snippet"]),
    ]
    companies = include_snippets + exclude_snippets
    requests_mock.get(
        "https://api.companieshouse.gov.uk/search/companies?q=test&items_per_page=20&start_index=0",
        json={
            "items": _to_results(companies),
        },
    )

    items = search_companies("test")
    assert items == _to_items(include_snippets)


def test_search_companies_desired_results_after_filtering(requests_mock):
    first_page_active = [_get_company() for _ in range(10)]
    first_page_inactive = [_get_company(company_status="inactive") for _ in range(10)]
    first_page_results = first_page_active + first_page_inactive
    requests_mock.get(
        "https://api.companieshouse.gov.uk/search/companies?q=test&items_per_page=20&start_index=0",
        json={
            "items": _to_results(first_page_results),
        },
    )

    second_page_active = [_get_company() for _ in range(10)]
    second_page_inactive = [_get_company(company_status="inactive") for _ in range(10)]
    second_page_results = second_page_active + second_page_inactive
    requests_mock.get(
        "https://api.companieshouse.gov.uk/search/companies?q=test&items_per_page=20&start_index=20",
        json={
            "items": _to_results(second_page_results),
        },
    )

    items = search_companies("test")
    assert items == _to_items(first_page_active + second_page_active)
