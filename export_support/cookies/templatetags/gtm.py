from django import template
from django.conf import settings
from django.template import loader
from django.utils.safestring import mark_safe

register = template.Library()


def render_gtm_template(template_filename, request, gtm_id, gtm_auth):
    t = loader.get_template(template_filename)

    return t.render({"request": request, "GTM_ID": gtm_id, "GTM_AUTH": gtm_auth})


@register.simple_tag(takes_context=True)
def google_tag_manager(context):
    GTM_ID = getattr(settings, "GTM_ID", None)
    if not GTM_ID:
        return mark_safe("<!-- missing GTM id -->")

    GTM_AUTH = getattr(settings, "GTM_AUTH", None)
    if not GTM_AUTH:
        return mark_safe("<!-- missing GTM auth -->")

    return render_gtm_template("cookies/gtm.html", context["request"], GTM_ID, GTM_AUTH)


@register.simple_tag(takes_context=True)
def google_tag_manager_noscript(context):
    GTM_ID = getattr(settings, "GTM_ID", None)
    if not GTM_ID:
        return mark_safe("<!-- missing GTM id -->")

    GTM_AUTH = getattr(settings, "GTM_AUTH", None)
    if not GTM_AUTH:
        return mark_safe("<!-- missing GTM auth -->")

    return render_gtm_template(
        "cookies/gtm_noscript.html", context["request"], GTM_ID, GTM_AUTH
    )
