import time

from django.views.generic import TemplateView


class HealthCheckView(TemplateView):
    content_type = "text/xml"
    template_name = "healthcheck/healthcheck.xml"

    def get_context_data(self, **kwargs):
        """Adds status and response time to response context"""
        context = super().get_context_data(**kwargs)
        context["status"] = "OK"
        # nearest approximation of a response time
        context["response_time"] = time.time() - self.request.start_time
        return context
