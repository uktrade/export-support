from django.urls import path

from export_support.core import views

app_name = "core"
urlpatterns = [
    path("", views.EnquirySubjectFormView.as_view(), name="index"),
]
