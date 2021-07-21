import time
import urllib

from django.conf import settings
from django.views.generic import TemplateView


class HealthCheckView(TemplateView):
    content_type = "text/xml"
    template_name = "healthcheck/healthcheck.xml"

    def get_context_data(self, **kwargs):
        """Adds status and response time to response context"""
        context = super().get_context_data(**kwargs)

        try:
            urllib.request.urlopen(settings.DIRECTORY_FORMS_API_HEALTHCHECK_URL)
        except Exception as e:
            raise Exception("Directory forms API healthcheck failed") from e

        context["status"] = "OK"
        # nearest approximation of a response time
        context["response_time"] = time.time() - self.request.start_time
        return context
