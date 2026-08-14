from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.site.api.admin.views import (
    AdminBunnySettingsView,
    AdminContactMessageViewSet,
    AdminMailchimpInterestsView,
    AdminMailchimpSettingsView,
    AdminNewsletterViewSet,
    AdminSiteSettingsView,
    AdminSliderViewSet,
    AdminStartButtonViewSet,
    AdminStripeSettingsView,
    AdminTestimonialViewSet,
)

router = DefaultRouter()
router.register("site/sliders", AdminSliderViewSet, basename="admin-sliders")
router.register("site/start-buttons", AdminStartButtonViewSet, basename="admin-start-buttons")
router.register("site/testimonials", AdminTestimonialViewSet, basename="admin-testimonials")
router.register("contact", AdminContactMessageViewSet, basename="admin-contact")
router.register("newsletter", AdminNewsletterViewSet, basename="admin-newsletter")

urlpatterns = [
    path("site/settings/", AdminSiteSettingsView.as_view(), name="admin-site-settings"),
    path("site/bunny/", AdminBunnySettingsView.as_view(), name="admin-site-bunny"),
    path("site/stripe/", AdminStripeSettingsView.as_view(), name="admin-site-stripe"),
    path("site/mailchimp/", AdminMailchimpSettingsView.as_view(), name="admin-site-mailchimp"),
    path(
        "site/mailchimp/interests/",
        AdminMailchimpInterestsView.as_view(),
        name="admin-site-mailchimp-interests",
    ),
    path("", include(router.urls)),
]
