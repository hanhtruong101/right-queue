from django.urls import path

from .views import ServiceListView


app_name = "service_catalogue"

urlpatterns = [
    path(
        "organizations/<slug:organization_slug>/services/",
        ServiceListView.as_view(),
        name="service-list",
    ),
]