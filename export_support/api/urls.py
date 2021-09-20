from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("company-search/", views.CompaniesSearchView.as_view(), name="company-search"),
]
