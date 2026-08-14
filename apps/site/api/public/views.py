from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.site.api.serializers import (
    ContactCreateSerializer,
    NewsletterSubscribeSerializer,
    PublicSiteSerializer,
)
from apps.site.selectors import (
    get_site_settings,
    public_sliders,
    public_start_buttons,
    public_testimonials,
)
from apps.site.services.inbox_service import create_contact_message, subscribe_newsletter


class PublicSiteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["Public — Site"])
    def get(self, request):
        settings = get_site_settings()
        payload = {
            "about": {"title": settings.about_title, "html": settings.about_html},
            "contact_info": {
                "phone_1": settings.phone_1,
                "phone_2": settings.phone_2,
                "email": settings.contact_email,
            },
            "social": {
                "instagram": settings.social_instagram,
                "tiktok": settings.social_tiktok,
                "facebook": settings.social_facebook,
                "pinterest": settings.social_pinterest,
            },
            "sliders": public_sliders(),
            "start_buttons": public_start_buttons(),
            "testimonials": public_testimonials(),
        }
        serializer = PublicSiteSerializer(payload, context={"request": request})
        return Response({"data": serializer.data, "meta": {}})


class PublicContactView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["Public — Site"], request=ContactCreateSerializer)
    def post(self, request):
        serializer = ContactCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_contact_message(**serializer.validated_data)
        return Response(
            {"data": {"message": "Mensaje enviado correctamente."}, "meta": {}},
            status=status.HTTP_201_CREATED,
        )


class PublicNewsletterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["Public — Site"], request=NewsletterSubscribeSerializer)
    def post(self, request):
        serializer = NewsletterSubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscribe_newsletter(**serializer.validated_data)
        return Response(
            {"data": {"message": "Suscripción registrada."}, "meta": {}},
            status=status.HTTP_201_CREATED,
        )
