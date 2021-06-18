from django import template
from django.conf import settings
from django.template import loader
from django.utils.safestring import mark_safe

register = template.Library()


def render_gtm_template(template_filename, gtm_container_id):
    t = loader.get_template(template_filename)

    return t.render({"GTM_CONTAINER_ID": gtm_container_id})


@register.simple_tag()
def google_tag_manager():
    GA_GTM_ID = getattr(settings, "GA_GTM_ID", None)
    if not GA_GTM_ID:
        return mark_safe("<!-- missing GTM container id -->")

    return render_gtm_template("cookies/gtm.html", GA_GTM_ID)


@register.simple_tag()
def google_tag_manager_noscript():
    GA_GTM_ID = getattr(settings, "GA_GTM_ID", None)
    if not GA_GTM_ID:
        return mark_safe("<!-- missing GTM container id -->")

    return render_gtm_template("cookies/gtm_noscript.html", GA_GTM_ID)
