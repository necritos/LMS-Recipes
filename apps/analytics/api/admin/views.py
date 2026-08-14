from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.selectors import (
    dashboard_summary,
    resolve_granularity,
    resolve_period,
    revenue_series,
    series_bounds,
)
from apps.common.exceptions import BusinessError
from apps.common.permissions import IsStaffUser


def _int_query(request, name: str, default: int, *, min_value: int, max_value: int) -> int:
    raw = request.query_params.get(name)
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise BusinessError(
            "QUERY_INVALID",
            f"{name} debe ser un entero.",
            http_status=422,
        ) from exc
    return max(min_value, min(max_value, value))


class AdminDashboardView(APIView):
    permission_classes = [IsStaffUser]

    @extend_schema(
        tags=["Admin — Analytics"],
        parameters=[
            OpenApiParameter("period", str, description="day | week | month | all (default month)"),
            OpenApiParameter(
                "recent_limit", int, description="Órdenes recientes (1–50, default 10)"
            ),
            OpenApiParameter("top_limit", int, description="Top productos (1–20, default 5)"),
        ],
    )
    def get(self, request):
        period = resolve_period(request.query_params.get("period"))
        payload = dashboard_summary(
            period=period,
            recent_limit=_int_query(request, "recent_limit", 10, min_value=1, max_value=50),
            top_limit=_int_query(request, "top_limit", 5, min_value=1, max_value=20),
        )
        return Response({"data": payload, "meta": {}})


class AdminDashboardRevenueView(APIView):
    permission_classes = [IsStaffUser]

    @extend_schema(
        tags=["Admin — Analytics"],
        parameters=[
            OpenApiParameter("granularity", str, description="day | week | month (default day)"),
            OpenApiParameter("days", int, description="Ventana hacia atrás (default 30 en day)"),
        ],
    )
    def get(self, request):
        granularity = resolve_granularity(request.query_params.get("granularity"))
        days = None
        raw_days = request.query_params.get("days")
        if raw_days not in (None, ""):
            days = _int_query(request, "days", 30, min_value=1, max_value=366)
        start, end = series_bounds(granularity=granularity, days=days)
        payload = revenue_series(granularity=granularity, start=start, end=end)
        return Response({"data": payload, "meta": {}})
