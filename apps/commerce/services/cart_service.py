from decimal import Decimal

from django.db import transaction

from apps.catalog.constants import PublishStatus
from apps.catalog.models import Course, Recipe
from apps.commerce.models import Cart, CartItem
from apps.common.exceptions import BusinessError


def get_or_create_cart(*, user) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def _published_course(course_id) -> Course:
    course = Course.objects.filter(pk=course_id, status=PublishStatus.PUBLISHED).first()
    if course is None:
        raise BusinessError(
            "PRODUCT_NOT_AVAILABLE",
            "El curso no está disponible.",
            http_status=422,
        )
    return course


def _published_recipe(recipe_id) -> Recipe:
    recipe = Recipe.objects.filter(pk=recipe_id, status=PublishStatus.PUBLISHED).first()
    if recipe is None:
        raise BusinessError(
            "PRODUCT_NOT_AVAILABLE",
            "La receta no está disponible.",
            http_status=422,
        )
    return recipe


@transaction.atomic
def add_cart_item(*, user, course_id=None, recipe_id=None) -> CartItem:
    if bool(course_id) == bool(recipe_id):
        raise BusinessError(
            "CART_ITEM_INVALID",
            "Indica exactamente un course_id o recipe_id.",
            http_status=422,
        )
    cart = get_or_create_cart(user=user)
    if course_id:
        course = _published_course(course_id)
        if CartItem.objects.filter(cart=cart, course=course).exists():
            raise BusinessError(
                "ITEM_ALREADY_IN_CART",
                "Este curso ya está en el carrito.",
                http_status=409,
            )
        return CartItem.objects.create(cart=cart, course=course)
    recipe = _published_recipe(recipe_id)
    if CartItem.objects.filter(cart=cart, recipe=recipe).exists():
        raise BusinessError(
            "ITEM_ALREADY_IN_CART",
            "Esta receta ya está en el carrito.",
            http_status=409,
        )
    return CartItem.objects.create(cart=cart, recipe=recipe)


@transaction.atomic
def remove_cart_item(*, user, item_id) -> None:
    cart = get_or_create_cart(user=user)
    item = cart.items.filter(pk=item_id).first()
    if item is None:
        raise BusinessError("CART_ITEM_NOT_FOUND", "Ítem no encontrado.", http_status=404)
    item.delete()


@transaction.atomic
def clear_cart(*, user) -> None:
    cart = get_or_create_cart(user=user)
    cart.items.all().delete()


def cart_total(cart: Cart) -> Decimal:
    total = Decimal("0.00")
    for item in cart.items.select_related("course", "recipe"):
        product = item.course or item.recipe
        total += product.price
    return total
