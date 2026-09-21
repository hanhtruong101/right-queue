from django.urls import path
from .views import ServiceRequestCreateView

app_name = "cases"

urlpatterns = [
    path(
        "organizations/<slug:organization_slug>/requests/",
        ServiceRequestCreateView.as_view(),
        name="service-request-create",
    )
]