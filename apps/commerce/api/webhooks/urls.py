from django.urls import path

from apps.commerce.api.webhooks.views import StripeWebhookView

urlpatterns = [
    path("stripe/", StripeWebhookView.as_view(), name="webhooks-stripe"),
]
