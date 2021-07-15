from django import template
from django.conf import settings
from django.template import loader
from django.utils.safestring import mark_safe

register = template.Library()


def render_gtm_template(template_filename, gtm_id, gtm_auth):
    t = loader.get_template(template_filename)

    return t.render({"GTM_ID": gtm_id, "GTM_AUTH": gtm_auth})


@register.simple_tag()
def google_tag_manager():
    GTM_ID = getattr(settings, "GTM_ID", None)
    if not GTM_ID:
        return mark_safe("<!-- missing GTM id -->")

    GTM_AUTH = getattr(settings, "GTM_AUTH", None)
    if not GTM_AUTH:
        return mark_safe("<!-- missing GTM auth -->")

    return render_gtm_template("cookies/gtm.html", GTM_ID, GTM_AUTH)


@register.simple_tag()
def google_tag_manager_noscript():
    GTM_ID = getattr(settings, "GTM_ID", None)
    if not GTM_ID:
        return mark_safe("<!-- missing GTM id -->")

    GTM_AUTH = getattr(settings, "GTM_AUTH", None)
    if not GTM_AUTH:
        return mark_safe("<!-- missing GTM auth -->")

    return render_gtm_template("cookies/gtm_noscript.html", GTM_ID, GTM_AUTH)
