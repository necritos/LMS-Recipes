from django.utils import timezone
from rest_framework import serializers

from apps.catalog.api.serializers_helpers import get_active_translation
from apps.commerce.models import CartItem, Purchase
from apps.commerce.services.cart_service import cart_total


class AddCartItemSerializer(serializers.Serializer):
    course_id = serializers.UUIDField(required=False)
    recipe_id = serializers.UUIDField(required=False)


class CartItemSerializer(serializers.ModelSerializer):
    product_type = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ("id", "product_type", "product_id", "slug", "title", "price", "created_at")

    def _product(self, obj):
        return obj.course or obj.recipe

    def get_product_type(self, obj) -> str:
        return "course" if obj.course_id else "recipe"

    def get_product_id(self, obj) -> str:
        return str(self._product(obj).id)

    def get_slug(self, obj) -> str:
        return self._product(obj).slug

    def get_title(self, obj) -> str:
        return get_active_translation(self._product(obj), "title") or self._product(obj).slug

    def get_price(self, obj) -> str:
        return str(self._product(obj).price)


class CartSerializer(serializers.Serializer):
    def to_representation(self, cart):
        items = cart.items.all()
        return {
            "id": str(cart.id),
            "items": CartItemSerializer(items, many=True, context=self.context).data,
            "total": str(cart_total(cart)),
            "currency": self.context.get("currency", "eur"),
        }


class CheckoutSessionSerializer(serializers.Serializer):
    lang = serializers.CharField(required=False, allow_blank=True, default="es")
    stripe_success_url = serializers.URLField(required=False, allow_blank=True)
    stripe_cancel_url = serializers.URLField(required=False, allow_blank=True)


class MePurchaseSerializer(serializers.ModelSerializer):
    product_type = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    purchased_at = serializers.DateTimeField(source="created_at", read_only=True)
    expires_at = serializers.SerializerMethodField()
    is_lifetime = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    order_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Purchase
        fields = (
            "id",
            "order_id",
            "product_type",
            "product_id",
            "slug",
            "title",
            "price",
            "purchased_at",
            "expires_at",
            "is_lifetime",
            "is_active",
        )

    def _product(self, obj):
        return obj.course or obj.recipe

    def get_product_type(self, obj) -> str:
        return "course" if obj.course_id else "recipe"

    def get_product_id(self, obj) -> str | None:
        product = self._product(obj)
        return str(product.id) if product else None

    def get_slug(self, obj) -> str | None:
        product = self._product(obj)
        return product.slug if product else None

    def get_title(self, obj) -> str:
        product = self._product(obj)
        if product is None:
            return ""
        return get_active_translation(product, "title") or product.slug

    def get_price(self, obj) -> str | None:
        for item in obj.order.items.all():
            if item.course_id == obj.course_id and item.recipe_id == obj.recipe_id:
                return str(item.unit_price)
        product = self._product(obj)
        return str(product.price) if product else None

    def get_expires_at(self, obj):
        return obj.access_grant.expires_at if obj.access_grant_id else None

    def get_is_lifetime(self, obj) -> bool:
        grant = obj.access_grant
        return bool(grant and grant.expires_at is None)

    def get_is_active(self, obj) -> bool:
        grant = obj.access_grant
        if grant is None or grant.is_revoked:
            return False
        return grant.expires_at is None or grant.expires_at > timezone.now()
