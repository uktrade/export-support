from django.urls import path

from . import views

app_name = "cookies"

urlpatterns = [
    path("", views.CookiesDetailsView.as_view(), name="cookies-details"),
    path(
        "/preferences",
        views.CookiesPreferencesView.as_view(),
        name="cookies-preferences",
    ),
]
