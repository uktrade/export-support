import base64
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SEARCH_URL = (
    "https://api.companieshouse.gov.uk/search/companies?q={query}&items_per_page=20"
)
TOKEN = base64.b64encode(bytes(settings.COMPANIES_HOUSE_TOKEN, "utf-8")).decode("utf-8")


def search_companies_house_api(query):
    headers = {"Authorization": f"Basic {TOKEN}"}
    return requests.get(SEARCH_URL.format(query=query), headers=headers)


def get_result(item):
    address = item.get("address", {})
    return {
        "name": item["title"],
        "postcode": address.get("postal_code"),
        "companyNumber": item["company_number"],
    }


def search_companies(query):
    response = search_companies_house_api(query)
    results = response.json()

    logger.info(results)
    filtered_results = [
        get_result(item)
        for item in results["items"]
        if item["company_status"] == "active"
    ]

    return filtered_results
