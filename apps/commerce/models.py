from decimal import Decimal

from django.db import models

from apps.accounts.models import UserAccount
from apps.catalog.models import Course, Recipe
from apps.common.models import TimeStampedModel, UUIDModel
from apps.content.models import AccessGrant


class Cart(UUIDModel, TimeStampedModel):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name="cart")

    def __str__(self) -> str:
        return f"cart {self.user.email}"


class CartItem(UUIDModel, TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="cart_items", null=True, blank=True
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="cart_items", null=True, blank=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(course__isnull=False, recipe__isnull=True)
                    | models.Q(course__isnull=True, recipe__isnull=False)
                ),
                name="cart_item_one_product",
            ),
            models.UniqueConstraint(
                fields=["cart", "course"],
                condition=models.Q(course__isnull=False),
                name="uniq_cart_course",
            ),
            models.UniqueConstraint(
                fields=["cart", "recipe"],
                condition=models.Q(recipe__isnull=False),
                name="uniq_cart_recipe",
            ),
        ]
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"cart-item {self.pk}"


class Order(UUIDModel, TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        PAID = "paid", "Pagado"
        FAILED = "failed", "Fallido"
        CANCELED = "canceled", "Cancelado"

    user = models.ForeignKey(UserAccount, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    currency = models.CharField(max_length=3, default="eur")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    stripe_session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    customer_email = models.EmailField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"order {self.pk} {self.status}"


class PaymentAttempt(UUIDModel, TimeStampedModel):
    class Outcome(models.TextChoices):
        STARTED = "started", "Iniciado"
        SUCCEEDED = "succeeded", "Correcto"
        FAILED = "failed", "Fallido"
        EXPIRED = "expired", "Expirado"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payment_attempts")
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="payment_attempts")
    outcome = models.CharField(max_length=20, choices=Outcome.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="eur")
    customer_email = models.EmailField(blank=True)
    stripe_session_id = models.CharField(max_length=255, blank=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    stripe_event_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_event_type = models.CharField(max_length=120, blank=True)
    failure_code = models.CharField(max_length=80, blank=True)
    failure_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"payment {self.outcome} {self.pk}"


class OrderItem(UUIDModel, TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, related_name="order_items", null=True, blank=True
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.SET_NULL, related_name="order_items", null=True, blank=True
    )
    title = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    access_days = models.PositiveIntegerField(null=True, blank=True)
    is_lifetime = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.title


class Purchase(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="purchases")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="purchases")
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, related_name="purchases", null=True, blank=True
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.SET_NULL, related_name="purchases", null=True, blank=True
    )
    access_grant = models.ForeignKey(
        AccessGrant,
        on_delete=models.SET_NULL,
        related_name="purchases",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"purchase {self.pk}"


class StripeEvent(UUIDModel, TimeStampedModel):
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=120)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-processed_at"]

    def __str__(self) -> str:
        return self.event_id
