from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsStaffUser
from apps.site.api.serializers import (
    AdminBunnySettingsSerializer,
    AdminContactMessageSerializer,
    AdminContactReadSerializer,
    AdminMailchimpSettingsSerializer,
    AdminNewsletterSerializer,
    AdminSiteSettingsSerializer,
    AdminSliderSerializer,
    AdminStartButtonSerializer,
    AdminStripeSettingsSerializer,
    AdminTestimonialSerializer,
)
from apps.site.models import (
    ContactMessage,
    HomeSlider,
    NewsletterSubscriber,
    StartButton,
    Testimonial,
)
from apps.site.selectors import (
    admin_contact_messages,
    admin_newsletter_subscribers,
    get_site_settings,
)
from apps.site.services.content_service import (
    create_slider,
    create_start_button,
    create_testimonial,
    delete_slider,
    delete_start_button,
    delete_testimonial,
    update_slider,
    update_start_button,
    update_testimonial,
)
from apps.site.services.inbox_service import set_contact_read
from apps.site.services.mailchimp_service import (
    delete_newsletter_subscriber,
    list_interest_categories,
    upsert_newsletter_member,
)
from apps.site.services.settings_service import (
    update_bunny_settings,
    update_mailchimp_settings,
    update_site_settings,
    update_stripe_settings,
)


class AdminSiteSettingsView(APIView):
    permission_classes = [IsStaffUser]

    @extend_schema(tags=["Admin — Site"])
    def get(self, request):
        settings = get_site_settings()
        serializer = AdminSiteSettingsSerializer(settings)
        return Response({"data": serializer.data, "meta": {}})

    @extend_schema(tags=["Admin — Site"], request=AdminSiteSettingsSerializer)
    def patch(self, request):
        serializer = AdminSiteSettingsSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        settings = update_site_settings(fields=serializer.validated_data)
        output = AdminSiteSettingsSerializer(settings)
        return Response({"data": output.data, "meta": {}})


class AdminBunnySettingsView(APIView):
    permission_classes = [IsStaffUser]

    @extend_schema(tags=["Admin — Site"])
    def get(self, request):
        settings = get_site_settings()
        serializer = AdminBunnySettingsSerializer(settings)
        return Response({"data": serializer.data, "meta": {}})

    @extend_schema(tags=["Admin — Site"], request=AdminBunnySettingsSerializer)
    def patch(self, request):
        serializer = AdminBunnySettingsSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        settings = update_bunny_settings(fields=serializer.validated_data)
        output = AdminBunnySettingsSerializer(settings)
        return Response({"data": output.data, "meta": {}})


class AdminStripeSettingsView(APIView):
    permission_classes = [IsStaffUser]

    @extend_schema(tags=["Admin — Site"])
    def get(self, request):
        settings = get_site_settings()
        serializer = AdminStripeSettingsSerializer(settings)
        return Response({"data": serializer.data, "meta": {}})

    @extend_schema(tags=["Admin — Site"], request=AdminStripeSettingsSerializer)
    def patch(self, request):
        serializer = AdminStripeSettingsSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        settings = update_stripe_settings(fields=serializer.validated_data)
        output = AdminStripeSettingsSerializer(settings)
        return Response({"data": output.data, "meta": {}})


class AdminMailchimpSettingsView(APIView):
    permission_classes = [IsStaffUser]

    @extend_schema(tags=["Admin — Site"])
    def get(self, request):
        settings = get_site_settings()
        serializer = AdminMailchimpSettingsSerializer(settings)
        return Response({"data": serializer.data, "meta": {}})

    @extend_schema(tags=["Admin — Site"], request=AdminMailchimpSettingsSerializer)
    def patch(self, request):
        serializer = AdminMailchimpSettingsSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        settings = update_mailchimp_settings(fields=serializer.validated_data)
        output = AdminMailchimpSettingsSerializer(settings)
        return Response({"data": output.data, "meta": {}})


class AdminMailchimpInterestsView(APIView):
    permission_classes = [IsStaffUser]

    @extend_schema(tags=["Admin — Site"])
    def get(self, request):
        categories = list_interest_categories()
        return Response({"data": {"categories": categories}, "meta": {}})


@extend_schema_view(
    list=extend_schema(tags=["Admin — Site"]),
    retrieve=extend_schema(tags=["Admin — Site"]),
    create=extend_schema(tags=["Admin — Site"]),
    update=extend_schema(tags=["Admin — Site"]),
    partial_update=extend_schema(tags=["Admin — Site"]),
    destroy=extend_schema(tags=["Admin — Site"]),
)
class AdminSliderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = AdminSliderSerializer
    queryset = HomeSlider.objects.prefetch_related("translations__language").all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slider = create_slider(**serializer.validated_data)
        output = self.get_serializer(slider)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        slider = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        slider = update_slider(slider=slider, **serializer.validated_data)
        output = self.get_serializer(slider)
        return Response(output.data)

    def perform_destroy(self, instance):
        delete_slider(slider=instance)


@extend_schema_view(
    list=extend_schema(tags=["Admin — Site"]),
    retrieve=extend_schema(tags=["Admin — Site"]),
    create=extend_schema(tags=["Admin — Site"]),
    update=extend_schema(tags=["Admin — Site"]),
    partial_update=extend_schema(tags=["Admin — Site"]),
    destroy=extend_schema(tags=["Admin — Site"]),
)
class AdminStartButtonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = AdminStartButtonSerializer
    queryset = StartButton.objects.prefetch_related("translations__language").all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        button = create_start_button(**serializer.validated_data)
        output = self.get_serializer(button)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        button = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        button = update_start_button(button=button, **serializer.validated_data)
        output = self.get_serializer(button)
        return Response(output.data)

    def perform_destroy(self, instance):
        delete_start_button(button=instance)


@extend_schema_view(
    list=extend_schema(tags=["Admin — Site"]),
    retrieve=extend_schema(tags=["Admin — Site"]),
    create=extend_schema(tags=["Admin — Site"]),
    update=extend_schema(tags=["Admin — Site"]),
    partial_update=extend_schema(tags=["Admin — Site"]),
    destroy=extend_schema(tags=["Admin — Site"]),
)
class AdminTestimonialViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    serializer_class = AdminTestimonialSerializer
    queryset = Testimonial.objects.prefetch_related("translations__language").all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = create_testimonial(**serializer.validated_data)
        output = self.get_serializer(item)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        item = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        item = update_testimonial(testimonial=item, **serializer.validated_data)
        output = self.get_serializer(item)
        return Response(output.data)

    def perform_destroy(self, instance):
        delete_testimonial(testimonial=instance)


@extend_schema_view(
    list=extend_schema(
        tags=["Admin — Site"],
        parameters=[
            OpenApiParameter("is_read", bool, description="Filtrar leídos / no leídos"),
        ],
    ),
    retrieve=extend_schema(tags=["Admin — Site"]),
    partial_update=extend_schema(tags=["Admin — Site"]),
    destroy=extend_schema(tags=["Admin — Site"]),
)
class AdminContactMessageViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsStaffUser]
    serializer_class = AdminContactMessageSerializer
    queryset = ContactMessage.objects.all()
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        raw = self.request.query_params.get("is_read")
        is_read = None
        if raw is not None:
            is_read = raw.lower() in {"true", "1", "yes"}
        return admin_contact_messages(is_read=is_read)

    def partial_update(self, request, *args, **kwargs):
        serializer = AdminContactReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = set_contact_read(
            message=self.get_object(),
            is_read=serializer.validated_data["is_read"],
        )
        output = AdminContactMessageSerializer(message)
        return Response(output.data)


@extend_schema_view(
    list=extend_schema(
        tags=["Admin — Site"],
        parameters=[
            OpenApiParameter("search", str, description="Filtrar por email o nombre"),
            OpenApiParameter(
                "mailchimp_status",
                str,
                description="pending, synced, failed o skipped",
            ),
        ],
    ),
    retrieve=extend_schema(tags=["Admin — Site"]),
    destroy=extend_schema(tags=["Admin — Site"]),
)
class AdminNewsletterViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsStaffUser]
    serializer_class = AdminNewsletterSerializer
    queryset = NewsletterSubscriber.objects.all()

    def get_queryset(self):
        search = self.request.query_params.get("search", "").strip()
        mailchimp_status = self.request.query_params.get("mailchimp_status", "").strip()
        return admin_newsletter_subscribers(search=search, mailchimp_status=mailchimp_status)

    def perform_destroy(self, instance):
        delete_newsletter_subscriber(subscriber=instance)

    @extend_schema(tags=["Admin — Site"])
    @action(detail=True, methods=["post"], url_path="resync")
    def resync(self, request, pk=None):
        subscriber = upsert_newsletter_member(subscriber=self.get_object())
        output = AdminNewsletterSerializer(subscriber)
        return Response({"data": output.data, "meta": {}})
