from django import template
from django.conf import settings
from django.template import loader
from django.utils.safestring import mark_safe

register = template.Library()


def render_gtm_template(
    template_filename, request, gtm_id, gtm_auth, gtm_preview, gtm_cookies_win
):
    t = loader.get_template(template_filename)

    return t.render(
        {
            "request": request,
            "GTM_ID": gtm_id,
            "GTM_AUTH": gtm_auth,
            "GTM_PREVIEW": gtm_preview,
            "GTM_COOKIES_WIN": gtm_cookies_win,
        }
    )


@register.simple_tag(takes_context=True)
def google_tag_manager(context):
    GTM_ID = getattr(settings, "GTM_ID", None)
    if not GTM_ID:
        return mark_safe("<!-- missing GTM id -->")

    GTM_AUTH = getattr(settings, "GTM_AUTH", None)
    GTM_PREVIEW = getattr(settings, "GTM_PREVIEW", None)
    GTM_COOKIES_WIN = getattr(settings, "GTM_COOKIES_WIN", None)

    return render_gtm_template(
        "cookies/gtm.html",
        context["request"],
        GTM_ID,
        GTM_AUTH,
        GTM_PREVIEW,
        GTM_COOKIES_WIN,
    )


@register.simple_tag(takes_context=True)
def google_tag_manager_noscript(context):
    GTM_ID = getattr(settings, "GTM_ID", None)
    if not GTM_ID:
        return mark_safe("<!-- missing GTM id -->")

    GTM_AUTH = getattr(settings, "GTM_AUTH", None)
    GTM_PREVIEW = getattr(settings, "GTM_PREVIEW", None)
    GTM_COOKIES_WIN = getattr(settings, "GTM_COOKIES_WIN", None)

    return render_gtm_template(
        "cookies/gtm_noscript.html",
        context["request"],
        GTM_ID,
        GTM_AUTH,
        GTM_PREVIEW,
        GTM_COOKIES_WIN,
    )
