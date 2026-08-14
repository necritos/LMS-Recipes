from django.urls import path

from apps.site.api.public.views import PublicContactView, PublicNewsletterView, PublicSiteView

urlpatterns = [
    path("site/", PublicSiteView.as_view(), name="public-site"),
    path("contact/", PublicContactView.as_view(), name="public-contact"),
    path("newsletter/", PublicNewsletterView.as_view(), name="public-newsletter"),
]
