from .countries import get_country_name_from_code

ENQUIRY_COUNTRY_CODES = [
    "AL",
    "AD",
    "AT",
    "BE",
    "BA",
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
    "IS",
    "IE",
    "IL",
    "IT",
    "XK",
    "LV",
    "LI",
    "LT",
    "LU",
    "MT",
    "MC",
    "ME",
    "NL",
    "MK",
    "NO",
    "PL",
    "PT",
    "RO",
    "SM",
    "RS",
    "SK",
    "SI",
    "ES",
    "SE",
    "CH",
    "TR",
    "VA",
]

ENQUIRY_COUNTRY_CODES_TO_NAME_MAP = {
    code: get_country_name_from_code(code)
    for code in sorted(ENQUIRY_COUNTRY_CODES, key=get_country_name_from_code)
}

SECTORS = [
    "Advanced engineering",
    "Aerospace",
    "Agriculture, horticulture, fisheries and pets",
    "Airports",
    "Automotive",
    "Chemicals",
    "Construction",
    "Consumer and retail",
    "Creative industries",
    "Defence",
    "Education and training",
    "Energy",
    "Environment",
    "Financial and professional services",
    "Food and drink",
    "Healthcare services",
    "Maritime",
    "Medical devices and equipment",
    "Mining",
    "Pharmaceuticals and biotechnology",
    "Railways",
    "Security",
    "Space",
    "Sports economy",
    "Technology and smart cities",
    "Water",
]
