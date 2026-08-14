from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.selectors import get_active_language, resolve_language_code
from apps.commerce.api.me.serializers import (
    AddCartItemSerializer,
    CartSerializer,
    MePurchaseSerializer,
)
from apps.commerce.selectors import cart_for_user, purchases_for_user
from apps.commerce.services.cart_service import add_cart_item, clear_cart, remove_cart_item
from apps.common.permissions import IsAuthenticatedUser
from apps.site.selectors import get_site_settings


class MeCartView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def _payload(self, request):
        lang = get_active_language(code=resolve_language_code(request.query_params.get("lang")))
        cart = cart_for_user(user=request.user, language=lang)
        currency = get_site_settings().stripe_currency or "eur"
        return CartSerializer(cart, context={"currency": currency}).data

    @extend_schema(
        tags=["Me"],
        parameters=[OpenApiParameter("lang", str, description="Idioma de títulos (default: es)")],
    )
    def get(self, request):
        return Response({"data": self._payload(request), "meta": {}})

    @extend_schema(tags=["Me"], request=AddCartItemSerializer)
    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        add_cart_item(user=request.user, **serializer.validated_data)
        return Response(
            {"data": self._payload(request), "meta": {}}, status=status.HTTP_201_CREATED
        )

    @extend_schema(tags=["Me"])
    def delete(self, request):
        clear_cart(user=request.user)
        return Response({"data": self._payload(request), "meta": {}})


class MeCartItemView(APIView):
    permission_classes = [IsAuthenticatedUser]

    @extend_schema(tags=["Me"])
    def delete(self, request, item_id):
        remove_cart_item(user=request.user, item_id=item_id)
        lang = get_active_language(code=resolve_language_code(request.query_params.get("lang")))
        cart = cart_for_user(user=request.user, language=lang)
        currency = get_site_settings().stripe_currency or "eur"
        return Response(
            {"data": CartSerializer(cart, context={"currency": currency}).data, "meta": {}}
        )


class MePurchaseListView(ListAPIView):
    permission_classes = [IsAuthenticatedUser]
    serializer_class = MePurchaseSerializer

    @extend_schema(
        tags=["Me"],
        parameters=[OpenApiParameter("lang", str, description="Idioma de títulos (default: es)")],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        language = get_active_language(
            code=resolve_language_code(self.request.query_params.get("lang"))
        )
        return purchases_for_user(user=self.request.user, language=language)
