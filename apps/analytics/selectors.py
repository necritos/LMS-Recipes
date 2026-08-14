from datetime import date, datetime, timedelta
from decimal import Decimal

from django.db.models import Count, Max, Q, QuerySet, Sum
from django.db.models.functions import Coalesce, TruncDate, TruncMonth, TruncWeek
from django.utils import timezone

from apps.commerce.models import Order, OrderItem
from apps.common.exceptions import BusinessError

ZERO = Decimal("0.00")


def paid_orders() -> QuerySet[Order]:
    return Order.objects.filter(status=Order.Status.PAID, paid_at__isnull=False)


def resolve_period(period: str | None) -> str:
    key = (period or "month").strip().lower()
    if key not in {"day", "week", "month", "all"}:
        raise BusinessError(
            "PERIOD_INVALID",
            "period debe ser day, week, month o all.",
            http_status=422,
        )
    return key


def period_bounds(period: str) -> tuple[datetime | None, datetime]:
    now = timezone.now()
    local = timezone.localtime(now)
    start_of_day = local.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "day":
        return start_of_day, now
    if period == "week":
        return start_of_day - timedelta(days=6), now
    if period == "month":
        return start_of_day.replace(day=1), now
    return None, now


def _money(value) -> str:
    if value is None:
        value = ZERO
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return str(value.quantize(ZERO))


def _filter_period(qs: QuerySet, start: datetime | None, end: datetime) -> QuerySet:
    qs = qs.filter(paid_at__lte=end)
    if start is not None:
        qs = qs.filter(paid_at__gte=start)
    return qs


def dashboard_summary(*, period: str, recent_limit: int, top_limit: int) -> dict:
    start, end = period_bounds(period)
    all_paid = paid_orders()
    period_paid = _filter_period(all_paid, start, end)

    all_agg = all_paid.aggregate(
        revenue=Coalesce(Sum("total"), ZERO),
        orders=Count("id"),
    )
    period_agg = period_paid.aggregate(
        revenue=Coalesce(Sum("total"), ZERO),
        orders=Count("id"),
    )
    pending = Order.objects.filter(status=Order.Status.PENDING).count()
    customers = all_paid.values("user_id").distinct().count()

    return {
        "currency": "eur",
        "period": {
            "key": period,
            "from": start.isoformat() if start else None,
            "to": end.isoformat(),
        },
        "totals": {
            "revenue_all_time": _money(all_agg["revenue"]),
            "revenue_period": _money(period_agg["revenue"]),
            "orders_paid_all_time": all_agg["orders"],
            "orders_paid_period": period_agg["orders"],
            "orders_pending": pending,
            "customers_with_purchases": customers,
        },
        "recent_orders": recent_paid_orders(limit=recent_limit),
        "top_products": top_products(limit=top_limit, start=start, end=end),
    }


def recent_paid_orders(*, limit: int) -> list[dict]:
    orders = (
        paid_orders().select_related("user").prefetch_related("items").order_by("-paid_at")[:limit]
    )
    result = []
    for order in orders:
        result.append(
            {
                "id": str(order.id),
                "total": _money(order.total),
                "currency": order.currency,
                "paid_at": order.paid_at.isoformat() if order.paid_at else None,
                "customer_email": order.customer_email or order.user.email,
                "user_id": str(order.user_id),
                "items": [
                    {
                        "title": item.title,
                        "unit_price": _money(item.unit_price),
                        "product_type": "course" if item.course_id else "recipe",
                        "product_id": str(item.course_id or item.recipe_id)
                        if (item.course_id or item.recipe_id)
                        else None,
                    }
                    for item in order.items.all()
                ],
            }
        )
    return result


def top_products(*, limit: int, start: datetime | None, end: datetime) -> list[dict]:
    items = OrderItem.objects.filter(
        order__status=Order.Status.PAID,
        order__paid_at__isnull=False,
        order__paid_at__lte=end,
    )
    if start is not None:
        items = items.filter(order__paid_at__gte=start)

    rows = []
    for product_type, id_field, slug_field, lookup in (
        ("course", "course_id", "course__slug", Q(course__isnull=False)),
        ("recipe", "recipe_id", "recipe__slug", Q(recipe__isnull=False)),
    ):
        grouped = (
            items.filter(lookup)
            .values(id_field, slug_field)
            .annotate(
                units=Count("id"),
                revenue=Coalesce(Sum("unit_price"), ZERO),
                title=Max("title"),
            )
        )
        for row in grouped:
            product_id = row[id_field]
            rows.append(
                {
                    "product_type": product_type,
                    "product_id": str(product_id) if product_id else None,
                    "slug": row.get(slug_field),
                    "title": row["title"],
                    "units": row["units"],
                    "revenue": _money(row["revenue"]),
                }
            )
    rows.sort(key=lambda item: (Decimal(item["revenue"]), item["units"]), reverse=True)
    return rows[:limit]


def resolve_granularity(value: str | None) -> str:
    key = (value or "day").strip().lower()
    if key not in {"day", "week", "month"}:
        raise BusinessError(
            "GRANULARITY_INVALID",
            "granularity debe ser day, week o month.",
            http_status=422,
        )
    return key


def _bucket_date_key(bucket) -> str:
    if isinstance(bucket, datetime):
        if timezone.is_aware(bucket):
            bucket = timezone.localtime(bucket)
        return bucket.date().isoformat()
    if isinstance(bucket, date):
        return bucket.isoformat()
    return str(bucket)


def revenue_series(*, granularity: str, start: datetime, end: datetime) -> dict:
    trunc = {"day": TruncDate, "week": TruncWeek, "month": TruncMonth}[granularity]
    qs = (
        _filter_period(paid_orders(), start, end)
        .annotate(bucket=trunc("paid_at"))
        .values("bucket")
        .annotate(revenue=Coalesce(Sum("total"), ZERO), orders=Count("id"))
        .order_by("bucket")
    )
    points = []
    for row in qs:
        bucket = row["bucket"]
        if bucket is None:
            continue
        points.append(
            {
                "date": _bucket_date_key(bucket),
                "revenue": _money(row["revenue"]),
                "orders": row["orders"],
            }
        )

    return {
        "currency": "eur",
        "granularity": granularity,
        "from": start.isoformat(),
        "to": end.isoformat(),
        "points": points,
    }


def series_bounds(*, granularity: str, days: int | None) -> tuple[datetime, datetime]:
    now = timezone.now()
    local = timezone.localtime(now).replace(hour=0, minute=0, second=0, microsecond=0)
    if granularity == "day":
        span = days if days and days > 0 else 30
        start = local - timedelta(days=span - 1)
    elif granularity == "week":
        span = days if days and days > 0 else 84
        start = local - timedelta(days=span - 1)
    else:
        start = local.replace(day=1)
        for _ in range(11):
            month = start.month - 1
            year = start.year
            if month == 0:
                month = 12
                year -= 1
            start = start.replace(year=year, month=month, day=1)
    return start, now
