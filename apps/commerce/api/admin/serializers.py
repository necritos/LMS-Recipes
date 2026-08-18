from rest_framework import serializers

from apps.commerce.models import PaymentAttempt


class AdminPaymentAttemptSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    order_status = serializers.CharField(source="order.status", read_only=True)
    items = serializers.SerializerMethodField()

    class Meta:
        model = PaymentAttempt
        fields = (
            "id",
            "outcome",
            "amount",
            "currency",
            "customer_email",
            "user",
            "order_id",
            "order_status",
            "items",
            "stripe_session_id",
            "stripe_payment_intent",
            "stripe_event_id",
            "stripe_event_type",
            "failure_code",
            "failure_message",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_user(self, obj) -> dict:
        user = obj.user
        full_name = f"{user.first_name} {user.last_name}".strip() or user.email
        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": full_name,
        }

    def get_items(self, obj) -> list:
        items = []
        for item in obj.order.items.all():
            items.append(
                {
                    "title": item.title,
                    "unit_price": str(item.unit_price),
                    "product_type": "course" if item.course_id else "recipe",
                    "product_id": str(item.course_id or item.recipe_id),
                }
            )
        return items
