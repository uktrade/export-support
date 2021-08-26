from django.http import JsonResponse
from django.views import View


class CompaniesSearchView(View):
    def get(self, request):
        return JsonResponse(
            {
                "results": [
                    {"name": "Oscorp", "postcode": "W1 2AB", "companyNumber": "12345"},
                    {
                        "name": "Stark Industries",
                        "postcode": "E2 3CD",
                        "companyNumber": "67890",
                    },
                    {
                        "name": "Damage Control",
                        "postcode": "S3 4EF",
                        "companyNumber": "98765",
                    },
                ]
            }
        )
