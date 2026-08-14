from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.commerce.services.webhook_service import parse_stripe_event, process_stripe_event


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(tags=["Webhooks"], auth=None)
    def post(self, request):
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        event = parse_stripe_event(payload=request.body, sig_header=sig_header)
        result = process_stripe_event(event)
        return Response({"data": result, "meta": {}})
