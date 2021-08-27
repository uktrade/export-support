import base64
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

ITEMS_PER_PAGE = 20
DESIRED_NUM_RESULTS = 20

SEARCH_URL = "https://api.companieshouse.gov.uk/search/companies?q={}&items_per_page={}&start_index={}".format(
    "{query}",
    ITEMS_PER_PAGE,
    "{start_index}",
)
TOKEN = base64.b64encode(bytes(settings.COMPANIES_HOUSE_TOKEN, "utf-8")).decode("utf-8")


def search_companies_house_api(query, start_index):
    headers = {"Authorization": f"Basic {TOKEN}"}
    url = SEARCH_URL.format(query=query, start_index=start_index)
    return requests.get(url, headers=headers)


def get_result(item):
    address = item.get("address", {})
    return {
        "name": item["title"],
        "postcode": address.get("postal_code"),
        "companyNumber": item["company_number"],
    }


def filter_active_companies(items):
    return [item for item in items if item["company_status"] == "active"]


def exclude_snippet_results(items):
    return [
        item
        for item in items
        if "title" in item["matches"] or "address_snippet" in item["matches"]
    ]


def search_companies(query):
    start_index = 0
    items = []

    while len(items) < DESIRED_NUM_RESULTS:
        response = search_companies_house_api(query, start_index)
        results = response.json()

        filtered_items = results["items"]
        if not filtered_items:
            break

        filtered_items = filter_active_companies(filtered_items)
        filtered_items = exclude_snippet_results(filtered_items)
        filtered_items = [get_result(item) for item in filtered_items]

        items += filtered_items
        start_index += ITEMS_PER_PAGE

    return items
