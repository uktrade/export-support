def no_index_middleware(get_response):
    def middleware(request):
        response = get_response(request)

        response["X-Robots-Tag"] = "noindex, nofollow"

        return response

    return middleware
