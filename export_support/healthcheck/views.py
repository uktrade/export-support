import time

import requests
from django.conf import settings
from django.views.generic import TemplateView

from export_support.companies.search import _search_companies_house_api


class HealthCheckError(Exception):
    pass


class CheckDirectoryFormsApi:
    def __call__(self):
        response = requests.get(settings.DIRECTORY_FORMS_API_HEALTHCHECK_URL)
        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise HealthCheckError("Directory forms API healthcheck failed") from e


class CheckCompaniesHouseApi:
    def __call__(self):
        response = _search_companies_house_api("test", 0)
        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise HealthCheckError("Companies API healthcheck failed") from e


class BaseHealthCheckView(TemplateView):
    content_type = "text/xml"
    template_name = "healthcheck/healthcheck.xml"
    check = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.check()
        context["status"] = "OK"
        # nearest approximation of a response time
        context["response_time"] = time.time() - self.request.start_time
        return context


class CompaniesHouseHealthCheckView(BaseHealthCheckView):
    check = CheckCompaniesHouseApi()


class DirectoryFormsHealthCheckView(BaseHealthCheckView):
    check = CheckDirectoryFormsApi()
