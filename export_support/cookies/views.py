from django.views.generic import TemplateView


class CookiesPreferencesView(TemplateView):
    template_name = "cookies/preferences.html"


class CookiesDetailsView(TemplateView):
    template_name = "cookies/cookies.html"
