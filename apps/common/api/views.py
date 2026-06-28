from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView


class PingView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=["Public"],
        summary="Health check API",
        responses={200: {"type": "object"}},
    )
    def get(self, request):
        return Response({"message": "pong", "service": "recetario-api"})
