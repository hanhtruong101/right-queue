from django.urls import path
from .views import ServiceRequestListCreateView

app_name = "cases"

urlpatterns = [
    path(
        "organizations/<slug:organization_slug>/requests/",
        ServiceRequestListCreateView.as_view(),
        name="service-request-create",
    )
]