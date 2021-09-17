from django.http import JsonResponse
from django.views import View

from export_support.companies.search import search_companies


class CompaniesSearchView(View):
    def get(self, request):
        query = request.GET.get("q")
        if query:
            results = search_companies(request.GET.get("q"))
        else:
            results = {}

        return JsonResponse(
            {
                "results": results,
            }
        )
