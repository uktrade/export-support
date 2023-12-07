from .countries import get_country_name_from_code

ENQUIRY_COUNTRY_CODES = {
    "AD": "andorra__ess_export",
    "AE": "united_arab_emirates__ess_export",
    "AF": "afghanistan__ess_export",
    "AL": "albania__ess_export",
    "AM": "armenia__ess_export",
    "AO": "angola__ess_export",
    "AR": "argentina__ess_export",
    "AT": "austria__ess_export",
    "AU": "australia__ess_export",
    "AZ": "azerbaijan__ess_export",
    "BA": "bosnia_and_herzegovina__ess_export",
    "BB": "barbados__ess_export",
    "BD": "bangladesh__ess_export",
    "BE": "belgium__ess_export",
    "BF": "burkina_faso__ess_export",
    "BG": "bulgaria__ess_export",
    "BH": "bahrain__ess_export",
    "BI": "burundi__ess_export",
    "BJ": "benin__ess_export",
    "BN": "brunei__ess_export",
    "BO": "bolivia__ess_export",
    "BR": "brazil__ess_export",
    "BS": "the_bahamas__ess_export",
    "BT": "bhutan__ess_export",
    "BW": "botswana__ess_export",
    "BY": "belarus__ess_export",
    "BZ": "belize__ess_export",
    "CA": "canada__ess_export",
    "CD": "congo_democratic_republic__ess_export",
    "CF": "central_african_republic__ess_export",
    "CG": "congo__ess_export",
    "CH": "switzerland__ess_export",
    "CI": "ivory_coast__ess_export",
    "CL": "chile__ess_export",
    "CM": "cameroon__ess_export",
    "CN": "china__ess_export",
    "CO": "colombia__ess_export",
    "CR": "costa_rica__ess_export",
    "CU": "cuba__ess_export",
    "CV": "cape_verde__ess_export",
    "CY": "cyprus__ess_export",
    "CZ": "czechia__ess_export",
    "DE": "germany__ess_export",
    "DJ": "djibouti__ess_export",
    "DK": "denmark__ess_export",
    "DM": "dominica__ess_export",
    "DO": "dominican_republic__ess_export",
    "DZ": "algeria__ess_export",
    "EC": "ecuador__ess_export",
    "EE": "estonia__ess_export",
    "EG": "egypt__ess_export",
    "ER": "eritrea__ess_export",
    "ES": "spain__ess_export",
    "ET": "ethiopia__ess_export",
    "FI": "finland__ess_export",
    "FJ": "fiji__ess_export",
    "FM": "micronesia__ess_export",
    "FR": "france__ess_export",
    "GA": "gabon__ess_export",
    "GD": "grenada__ess_export",
    "GE": "georgia__ess_export",
    "GH": "ghana__ess_export",
    "GM": "the_gambia__ess_export",
    "GN": "guinea__ess_export",
    "GQ": "equatorial_guinea__ess_export",
    "GR": "greece__ess_export",
    "GT": "guatemala__ess_export",
    "GW": "guinea_bissau__ess_export",
    "GY": "guyana__ess_export",
    "HN": "honduras__ess_export",
    "HR": "croatia__ess_export",
    "HT": "haiti__ess_export",
    "HU": "hungary__ess_export",
    "ID": "indonesia__ess_export",
    "IE": "ireland__ess_export",
    "IL": "israel__ess_export",
    "IN": "india__ess_export",
    "IQ": "iraq__ess_export",
    "IR": "iran__ess_export",
    "IS": "iceland__ess_export",
    "IT": "italy__ess_export",
    "JM": "jamaica__ess_export",
    "JO": "jordan__ess_export",
    "JP": "japan__ess_export",
    "KE": "kenya__ess_export",
    "KG": "kyrgyzstan__ess_export",
    "KH": "cambodia__ess_export",
    "KI": "kiribati__ess_export",
    "KM": "comoros__ess_export",
    "KN": "st_kitts_and_nevis__ess_export",
    "KP": "north_korea__ess_export",
    "KR": "south_korea__ess_export",
    "KW": "kuwait__ess_export",
    "KZ": "kazakhstan__ess_export",
    "LA": "laos__ess_export",
    "LB": "lebanon__ess_export",
    "LC": "st_lucia__ess_export",
    "LI": "liechtenstein__ess_export",
    "LK": "sri_lanka__ess_export",
    "LR": "liberia__ess_export",
    "LS": "lesotho__ess_export",
    "LT": "lithuania__ess_export",
    "LU": "luxembourg__ess_export",
    "LV": "latvia__ess_export",
    "LY": "libya__ess_export",
    "MA": "morocco__ess_export",
    "MC": "monaco__ess_export",
    "MD": "moldova__ess_export",
    "ME": "montenegro__ess_export",
    "MG": "madagascar__ess_export",
    "MH": "marshall_islands__ess_export",
    "MK": "north_macedonia__ess_export",
    "ML": "mali__ess_export",
    "MM": "myanmar__ess_export",
    "MN": "mongolia__ess_export",
    "MR": "mauritania__ess_export",
    "MT": "malta__ess_export",
    "MU": "mauritius__ess_export",
    "MV": "maldives__ess_export",
    "MW": "malawi__ess_export",
    "MX": "mexico__ess_export",
    "MY": "malaysia__ess_export",
    "MZ": "mozambique__ess_export",
    "NA": "namibia__ess_export",
    "NE": "niger__ess_export",
    "NG": "nigeria__ess_export",
    "NI": "nicaragua__ess_export",
    "NL": "netherland__ess_export",
    "NO": "norway__ess_export",
    "NP": "nepal__ess_export",
    "NR": "nauru__ess_export",
    "NZ": "new_zealand__ess_export",
    "OM": "oman__ess_export",
    "PA": "panama__ess_export",
    "PE": "peru__ess_export",
    "PG": "papua_new_guinea__ess_export",
    "PH": "philippines__ess_export",
    "PK": "pakistan__ess_export",
    "PL": "poland__ess_export",
    "PT": "portugal__ess_export",
    "PY": "paraguay__ess_export",
    "PW": "palau__ess_export",
    "QA": "qatar__ess_export",
    "RO": "romania__ess_export",
    "RS": "serbia__ess_export",
    "RU": "russia__ess_export",
    "RW": "rwanda__ess_export",
    "SA": "saudi_arabia__ess_export",
    "SB": "solomon_islands__ess_export",
    "SC": "seychelles__ess_export",
    "SD": "sudan__ess_export",
    "SE": "sweden__ess_export",
    "SG": "singapore__ess_export",
    "SI": "slovenia__ess_export",
    "SK": "slovakia__ess_export",
    "SL": "sierra_leone__ess_export",
    "SM": "san_marino__ess_export",
    "SN": "senegal__ess_export",
    "SO": "somalia__ess_export",
    "SR": "suriname__ess_export",
    "SS": "south_sudan__ess_export",
    "ST": "sao_tome_and_principe__ess_export",
    "SV": "el_salvador__ess_export",
    "SY": "syria__ess_export",
    "SZ": "eswatini__ess_export",
    "TD": "chad__ess_export",
    "TG": "togo__ess_export",
    "TH": "thailand__ess_export",
    "TJ": "tajikistan__ess_export",
    "TL": "east_timor__ess_export",
    "TM": "turkmenistan__ess_export",
    "TN": "unisia__ess_export",
    "TO": "tonga__ess_export",
    "TR": "turkey__ess_export",
    "TT": "trinidad_and_tobago__ess_export",
    "TV": "tuvalu__ess_export",
    "TZ": "tanzania__ess_export",
    "UA": "ukraine__ess_export",
    "UG": "uganda__ess_export",
    "US": "united_states__ess_export",
    "UY": "uruguay__ess_export",
    "UZ": "uzbekistan__ess_export",
    "VA": "vatican_city__ess_export",
    "VC": "st_vincent__ess_export",
    "VE": "venezuela__ess_export",
    "VN": "vietnam__ess_export",
    "VU": "vanuatu__ess_export",
    "WS": "samoa__ess_export",
    "XK": "kosovo__ess_export",
    "YE": "yemen__ess_export",
    "ZA": "south_africa__ess_export",
    "ZM": "zambia__ess_export",
    "ZW": "zimbabwe__ess_export",
}

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

EMERGENCY_SITUATION_COUNTRIES = {
    "israel-palestine": {
        "country_list": "Israel, Occupied Palestinian Territories",
        "subject_title": "Israel/Palestine Enquiry",
    },
    "russia-ukraine": {
        "country_list": "Russia, Ukraine",
        "subject_title": "Russia/Ukraine Enquiry",
    },
}
