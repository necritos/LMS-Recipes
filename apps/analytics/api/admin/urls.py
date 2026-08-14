from django.urls import path

from apps.analytics.api.admin.views import AdminDashboardRevenueView, AdminDashboardView

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("dashboard/revenue/", AdminDashboardRevenueView.as_view(), name="admin-dashboard-revenue"),
]
