from rest_framework import viewsets, permissions, status, pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Client, AuditLog
from .serializers import ClientSerializer, AuditLogSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import os
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

class ClientPageNumberPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

    def get_page_size(self, request):
        size = super().get_page_size(request)
        print(f"[API][page_size] param page_size={request.query_params.get('page_size')} => utilisé: {size}")
        return size

@method_decorator(never_cache, name='dispatch')
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by('nom_client')
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut_general', 'date_creation', 'langue']
    search_fields = ['nom_client', 'sap_id', 'telephone']
    ordering_fields = ['date_creation', 'nom_client', 'statut_general']
    pagination_class = ClientPageNumberPagination

    def get_queryset(self):
        queryset = Client.objects.all().order_by('nom_client')
        region = self.request.query_params.get('region')
        ville = self.request.query_params.get('ville')
        if region:
            queryset = queryset.filter(region__iexact=region)
        if ville:
            queryset = queryset.filter(ville__iexact=ville)
        return queryset

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class MeUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not user.check_password(old_password):
            return Response({'old_password': 'Mot de passe actuel incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({'new_password': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Mot de passe changé avec succès.'})

class DeleteAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        user = request.user
        if user.image_profil:
            # Supprimer toutes les miniatures
            base_name = user.image_profil.name.rsplit('.', 1)[0]
            for size_name in ['small', 'medium', 'large']:
                thumb_name = base_name.replace('avatars/', f'avatars/thumbnails/{size_name}/') + '.jpg'
                storage = user.image_profil.storage
                if storage.exists(thumb_name):
                    storage.delete(thumb_name)
            user.image_profil.delete(save=False)
            user.image_profil = None
            user.save()
            return Response({'detail': 'Avatar supprimé.'})
        return Response({'detail': 'Aucun avatar à supprimer.'}, status=404)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Ajoute des claims personnalisés
        token['username'] = user.username
        token['role'] = user.role
        token['email'] = user.email
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
