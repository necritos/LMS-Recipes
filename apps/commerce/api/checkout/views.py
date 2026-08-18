from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.selectors import resolve_language_code
from apps.commerce.api.me.serializers import CheckoutSessionSerializer
from apps.commerce.services.checkout_service import create_checkout_session
from apps.common.permissions import IsAuthenticatedUser


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticatedUser]

    @extend_schema(tags=["Checkout"], request=CheckoutSessionSerializer)
    def post(self, request):
        serializer = CheckoutSessionSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        lang = resolve_language_code(
            serializer.validated_data.get("lang") or request.query_params.get("lang")
        )
        payload = create_checkout_session(
            user=request.user,
            lang=lang,
            stripe_success_url=serializer.validated_data.get("stripe_success_url") or None,
            stripe_cancel_url=serializer.validated_data.get("stripe_cancel_url") or None,
        )
        return Response({"data": payload, "meta": {}})
