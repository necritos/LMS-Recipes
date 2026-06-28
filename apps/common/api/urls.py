from django.urls import path

from apps.common.api.views import PingView

urlpatterns = [
    path("public/ping/", PingView.as_view(), name="public-ping"),
]
