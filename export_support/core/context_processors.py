from django.conf import settings


def external_urls(request):
    urls_settings_keys = [
        "GOV_UK_EXPORT_GOODS_URL",
        "GOV_UK_IMPORT_GOODS_URL",
        "GREAT_OFFICE_FINDER_URL",
    ]

    return {key: getattr(settings, key) for key in urls_settings_keys}
