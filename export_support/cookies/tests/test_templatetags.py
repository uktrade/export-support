from django.template import RequestContext, Template


def test_google_tag_manager(settings, rf):
    settings.GTM_ID = "GTM_ID"
    settings.GTM_AUTH = "GTM_AUTH"
    settings.GTM_PREVIEW = "GTM_PREVIEW"
    settings.GTM_COOKIES_WIN = "GTM_COOKIES_WIN"

    request = rf.get("/")

    t = Template("{% load gtm %}{% google_tag_manager %}")
    c = RequestContext(request, {})
    rendered = t.render(c)

    assert settings.GTM_ID in rendered
    assert settings.GTM_AUTH in rendered
    assert settings.GTM_PREVIEW in rendered
    assert settings.GTM_COOKIES_WIN in rendered


def test_google_tag_manager_only_gtm_id(settings, rf):
    settings.GTM_ID = "GTM_ID"

    request = rf.get("/")

    t = Template("{% load gtm %}{% google_tag_manager %}")
    c = RequestContext(request, {})
    rendered = t.render(c)

    assert settings.GTM_ID in rendered


def test_google_tag_manager_no_gtm_id(settings, rf):
    request = rf.get("/")

    t = Template("{% load gtm %}{% google_tag_manager %}")
    c = RequestContext(request, {})
    rendered = t.render(c)

    assert rendered == "<!-- missing GTM id -->"


def test_google_tag_manager_noscript(settings, rf):
    settings.GTM_ID = "GTM_ID"
    settings.GTM_AUTH = "GTM_AUTH"
    settings.GTM_PREVIEW = "GTM_PREVIEW"
    settings.GTM_COOKIES_WIN = "GTM_COOKIES_WIN"

    request = rf.get("/")

    t = Template("{% load gtm %}{% google_tag_manager_noscript %}")
    c = RequestContext(request, {})
    rendered = t.render(c)

    assert settings.GTM_ID in rendered
    assert settings.GTM_AUTH in rendered
    assert settings.GTM_PREVIEW in rendered
    assert settings.GTM_COOKIES_WIN in rendered


def test_google_tag_manager_noscript_only_gtm_id(settings, rf):
    settings.GTM_ID = "GTM_ID"

    request = rf.get("/")

    t = Template("{% load gtm %}{% google_tag_manager_noscript %}")
    c = RequestContext(request, {})
    rendered = t.render(c)

    assert settings.GTM_ID in rendered


def test_google_tag_manager_noscript_no_gtm_id(settings, rf):
    request = rf.get("/")

    t = Template("{% load gtm %}{% google_tag_manager_noscript %}")
    c = RequestContext(request, {})
    rendered = t.render(c)

    assert rendered == "<!-- missing GTM id -->"
