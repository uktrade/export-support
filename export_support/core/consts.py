from .countries import get_country_name_from_code

EU_COUNTRY_CODES = [
    "AT",
    "BE",
    "BG",
    "HR",
    "CY",
    "CZ",
    "DK",
    "EE",
    "FI",
    "FR",
    "DE",
    "GR",
    "HU",
    "IE",
    "IT",
    "LV",
    "LT",
    "LU",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SK",
    "ES",
    "SE",
]

EU_COUNTRY_CODES_TO_NAME_MAP = {
    code: get_country_name_from_code(code) for code in EU_COUNTRY_CODES
}
