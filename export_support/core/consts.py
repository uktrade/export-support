from django.conf import settings

from .countries import get_country_name_from_code

ORIGINAL_ENQUIRY_COUNTRY_CODES = {
    "AL": "albania__ess_export",
    "AD": "andorra__ess_export",
    "AT": "austria__ess_export",
    "BE": "belgium__ess_export",
    "BA": "bosnia_and_herzegovina__ess_export",
    "BG": "bulgaria__ess_export",
    "HR": "croatia__ess_export",
    "CY": "cyprus__ess_export",
    "CZ": "czechia__ess_export",
    "DK": "denmark__ess_export",
    "EE": "estonia__ess_export",
    "FI": "finland__ess_export",
    "FR": "france__ess_export",
    "DE": "germany__ess_export",
    "GR": "greece__ess_export",
    "HU": "hungary__ess_export",
    "IS": "iceland__ess_export",
    "IE": "ireland__ess_export",
    "IL": "israel__ess_export",
    "IT": "italy__ess_export",
    "XK": "kosovo__ess_export",
    "LV": "latvia__ess_export",
    "LI": "liechtenstein__ess_export",
    "LT": "lithuania__ess_export",
    "LU": "luxembourg__ess_export",
    "MT": "malta__ess_export",
    "MC": "monaco__ess_export",
    "ME": "montenegro__ess_export",
    "NL": "netherlands__ess_export",
    "MK": "north_macedonia__ess_export",
    "NO": "norway__ess_export",
    "PL": "poland__ess_export",
    "PT": "portugal__ess_export",
    "RO": "romania__ess_export",
    "SM": "san_marino__ess_export",
    "RS": "serbia__ess_export",
    "SK": "slovakia__ess_export",
    "SI": "slovenia__ess_export",
    "ES": "spain__ess_export",
    "SE": "sweden__ess_export",
    "CH": "switzerland__ess_export",
    "TR": "turkey__ess_export",
    "VA": "vatican_city__ess_export",
}

EECAN_ENQUIRY_COUNTRY_CODES = {
    "AM": "armenia__ess_export",
    "AZ": "azerbaijan__ess_export",
    "BY": "belarus__ess_export",
    "GE": "georgia__ess_export",
    "KZ": "kazakhstan__ess_export",
    "KG": "kyrgyzstan__ess_export",
    "MD": "moldova__ess_export",
    "MN": "mongolia__ess_export",
    "RU": "russia__ess_export",
    "TJ": "tajikistan__ess_export",
    "TM": "turkmenistan__ess_export",
    "UA": "ukraine__ess_export",
    "UZ": "uzbekistan__ess_export",
}

ENQUIRY_COUNTRY_CODES = {**ORIGINAL_ENQUIRY_COUNTRY_CODES}

if settings.EECAN_ROLLOUT_FEATURE_FLAG:
    ENQUIRY_COUNTRY_CODES = {**ENQUIRY_COUNTRY_CODES, **EECAN_ENQUIRY_COUNTRY_CODES}

COUNTRIES_MAP = {
    machine_readable_value: get_country_name_from_code(code)
    for code, machine_readable_value in sorted(
        ENQUIRY_COUNTRY_CODES.items(), key=lambda x: get_country_name_from_code(x[0])
    )
}

SECTORS_MAP = {
    "advanced_engineering__ess_sector_l1": "Advanced engineering",
    "aerospace__ess_sector_l1": "Aerospace",
    "agriculture_horticulture_fisheries_and_pets__ess_sector_l1": "Agriculture, horticulture, fisheries and pets",
    "airports__ess_sector_l1": "Airports",
    "automotive__ess_sector_l1": "Automotive",
    "chemicals__ess_sector_l1": "Chemicals",
    "construction__ess_sector_l1": "Construction",
    "consumer_and_retail__ess_sector_l1": "Consumer and retail",
    "creative_industries__ess_sector_l1": "Creative industries",
    "defence__ess_sector_l1": "Defence",
    "education_and_training__ess_sector_l1": "Education and training",
    "energy__ess_sector_l1": "Energy",
    "environment__ess_sector_l1": "Environment",
    "financial_and_professional_services__ess_sector_l1": "Financial and professional services",
    "food_and_drink__ess_sector_l1": "Food and drink",
    "healthcare_services__ess_sector_l1": "Healthcare services",
    "logistics__ess_sector_l1": "Logistics",
    "maritime__ess_sector_l1": "Maritime",
    "medical_devices_and_equipment__ess_sector_l1": "Medical devices and equipment",
    "mining__ess_sector_l1": "Mining",
    "pharmaceuticals_and_biotechnology__ess_sector_l1": "Pharmaceuticals and biotechnology",
    "railways__ess_sector_l1": "Railways",
    "security__ess_sector_l1": "Security",
    "space__ess_sector_l1": "Space",
    "sports_economy__ess_sector_l1": "Sports economy",
    "technology_and_smart_cities__ess_sector_l1": "Technology and smart cities",
    "water__ess_sector_l1": "Water",
}
