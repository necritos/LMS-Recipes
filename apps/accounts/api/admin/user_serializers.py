from rest_framework import serializers

from apps.accounts.models import UserAccount


class AdminUserAccountSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    auth_providers = serializers.SerializerMethodField()

    class Meta:
        model = UserAccount
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "status",
            "auth_providers",
            "email_verified_at",
            "last_login",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_full_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email

    def get_auth_providers(self, obj) -> list[str]:
        providers = ["email"]
        if obj.google_id:
            providers.append("google")
        return providers


class AdminUserAccountDetailSerializer(AdminUserAccountSerializer):
    purchases = serializers.SerializerMethodField()

    class Meta(AdminUserAccountSerializer.Meta):
        fields = AdminUserAccountSerializer.Meta.fields + ("purchases",)

    def get_purchases(self, obj) -> list:
        rows = obj.purchases.select_related("order", "course", "recipe")[:50]
        result = []
        for purchase in rows:
            result.append(
                {
                    "id": str(purchase.id),
                    "order_id": str(purchase.order_id),
                    "product_type": "course" if purchase.course_id else "recipe",
                    "product_id": str(purchase.course_id or purchase.recipe_id),
                    "created_at": purchase.created_at,
                }
            )
        return result
