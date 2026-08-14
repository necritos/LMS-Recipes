from rest_framework import serializers

from apps.catalog.api.serializers_helpers import get_active_translation
from apps.commerce.models import CartItem
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
