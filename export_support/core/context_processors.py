from django.conf import settings


def external_urls(request):
    urls_settings_keys = [
        "GOV_UK_EXPORT_GOODS_URL",
        "GREAT_OFFICE_FINDER_URL",
    ]

    return {key: getattr(settings, key) for key in urls_settings_keys}


def current_path(request):
    return {"current_path": request.get_full_path()}


def eecan_rollout_flag(request):
    return {"eecan_rollout_flag": settings.EECAN_ROLLOUT_FEATURE_FLAG}
