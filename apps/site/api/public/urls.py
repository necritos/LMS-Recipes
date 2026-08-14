from django.urls import path

from apps.site.api.public.views import (
    PublicContactView,
    PublicGoogleOAuthConfigView,
    PublicNewsletterView,
    PublicSiteView,
)

urlpatterns = [
    path("site/", PublicSiteView.as_view(), name="public-site"),
    path("google-oauth/", PublicGoogleOAuthConfigView.as_view(), name="public-google-oauth"),
    path("contact/", PublicContactView.as_view(), name="public-contact"),
    path("newsletter/", PublicNewsletterView.as_view(), name="public-newsletter"),
]
