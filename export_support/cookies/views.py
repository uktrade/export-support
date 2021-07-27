from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import TemplateView


class CookiesPreferencesView(TemplateView):
    template_name = "cookies/preferences.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        prev_page = self.request.GET.get("from")
        url_is_safe = url_has_allowed_host_and_scheme(
            url=prev_page,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )
        if prev_page and url_is_safe:
            ctx["prev_page"] = prev_page
        else:
            ctx["prev_page"] = "/"

        return ctx


class CookiesDetailsView(TemplateView):
    template_name = "cookies/cookies.html"
