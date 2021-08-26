import base64

import requests
from django.conf import settings

SEARCH_URL = (
    "https://api.companieshouse.gov.uk/search/companies?q={query}&items_per_page=20"
)
TOKEN = base64.b64encode(bytes(settings.COMPANIES_HOUSE_TOKEN, "utf-8")).decode("utf-8")


def search_companies_house_api(query):
    headers = {"Authorization": f"Basic {TOKEN}"}
    return requests.get(SEARCH_URL.format(query=query), headers=headers)


def search_companies(query):
    response = search_companies_house_api(query)
    results = response.json()

    return [
        {
            "name": item["title"],
            "postcode": item["address"]["postal_code"],
            "companyNumber": item["company_number"],
        }
        for item in results["items"]
    ]
