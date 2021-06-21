from django.utils.cache import patch_cache_control


def no_index_middleware(get_response):
    def middleware(request):
        response = get_response(request)

        response["X-Robots-Tag"] = "noindex, nofollow"

        return response

    return middleware


def no_cache_middleware(get_response):
    def middleware(request):
        response = get_response(request)

        patch_cache_control(
            response, no_cache=True, no_store=True, must_revalidate=True, private=True
        )
        response["Pragma"] = "no-cache"

        return response

    return middleware
