from django.urls import path

from apps.commerce.api.me.views import MeCartItemView, MeCartView

urlpatterns = [
    path("cart/", MeCartView.as_view(), name="me-cart"),
    path("cart/items/<uuid:item_id>/", MeCartItemView.as_view(), name="me-cart-item"),
]
