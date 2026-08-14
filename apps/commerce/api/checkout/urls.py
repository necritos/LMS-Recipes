from django.urls import path

from apps.commerce.api.checkout.views import CreateCheckoutSessionView

urlpatterns = [
    path(
        "create-session/",
        CreateCheckoutSessionView.as_view(),
        name="checkout-create-session",
    ),
]
