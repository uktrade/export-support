from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from ...forms import EnquirySubjectChoices


def test_index_view(client):
    response = client.get(reverse("core:index"))
    assert response.status_code == 302
    assert response.url == reverse("core:enquiry-wizard")


def test_privacy_view(client):
    response = client.get(reverse("core:privacy"))
    assert response.status_code == 200
    assertTemplateUsed(response, "core/privacy.html")


def test_non_eu_export_enquiries_view(client):
    url = reverse("core:non-eu-export-enquiries")
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "core/non_eu_export_enquiries.html")
    ctx = response.context
    assert ctx["should_display_sub_headings"]
    assert ctx["should_display_export_goods"]
    assert ctx["should_display_export_services"]
    assert ctx["heading"] == "Sell goods and services abroad"

    url = reverse("core:non-eu-export-enquiries")
    response = client.get(
        f"{url}?enquiry_subject={EnquirySubjectChoices.SELLING_GOODS_ABROAD}"
    )
    assert response.status_code == 200
    assertTemplateUsed(response, "core/non_eu_export_enquiries.html")
    ctx = response.context
    assert not ctx["should_display_sub_headings"]
    assert ctx["should_display_export_goods"]
    assert not ctx["should_display_export_services"]
    assert ctx["heading"] == "Sell goods abroad"

    url = reverse("core:non-eu-export-enquiries")
    response = client.get(
        f"{url}?enquiry_subject={EnquirySubjectChoices.SELLING_SERVICES_ABROAD}"
    )
    assert response.status_code == 200
    assertTemplateUsed(response, "core/non_eu_export_enquiries.html")
    ctx = response.context
    assert not ctx["should_display_sub_headings"]
    assert not ctx["should_display_export_goods"]
    assert ctx["should_display_export_services"]
    assert ctx["heading"] == "Sell services abroad"

    url = reverse("core:non-eu-export-enquiries")
    response = client.get(
        f"{url}?enquiry_subject={EnquirySubjectChoices.SELLING_GOODS_ABROAD}&enquiry_subject={EnquirySubjectChoices.SELLING_SERVICES_ABROAD}"  # noqa: E501
    )
    assert response.status_code == 200
    assertTemplateUsed(response, "core/non_eu_export_enquiries.html")
    ctx = response.context
    assert ctx["should_display_sub_headings"]
    assert ctx["should_display_export_goods"]
    assert ctx["should_display_export_services"]
    assert ctx["heading"] == "Sell goods and services abroad"
