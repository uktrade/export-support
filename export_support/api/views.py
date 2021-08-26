from django.http import JsonResponse
from django.views import View

from export_support.companies.search import search_companies


class CompaniesSearchView(View):
    def get(self, request):
        results = search_companies(request.GET.get("q"))

        return JsonResponse(
            {
                "results": results,
            }
        )
