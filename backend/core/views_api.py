from rest_framework import viewsets, permissions, status, pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Client, AuditLog, Ville
from .serializers import ClientSerializer, AuditLogSerializer, UserSerializer, VilleSerializer
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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

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

    def perform_update(self, serializer):
        instance = serializer.instance
        instance._current_user = self.request.user  # Toujours positionner avant le save
        serializer.save(modifie_par_user=self.request.user)

    def perform_create(self, serializer):
        obj = serializer.save(
            cree_par_user=self.request.user,
            modifie_par_user=self.request.user
        )
        obj._current_user = self.request.user  # Toujours positionner avant le save d'audit
        obj.save()

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['table_name', 'record_id']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    def get_queryset(self):
        queryset = AuditLog.objects.all()
        # Filtrage automatique pour n'afficher que l'historique du client demandé (si précisé)
        record_id = self.request.query_params.get('record_id')
        table_name = self.request.query_params.get('table_name', 'Client')
        if record_id:
            queryset = queryset.filter(table_name=table_name, record_id=record_id)
        return queryset

class VilleViewSet(viewsets.ReadOnlyModelViewSet):
    """API pour lister les villes"""
    queryset = Ville.objects.all().order_by('nom')
    serializer_class = VilleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # désactive la pagination pour renvoyer toutes les villes

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

@api_view(['GET'])
@permission_classes([IsAdminUser])
def adoption_kpis(request):
    total = Client.objects.count()
    if total == 0:
        return Response({
            "pct_installed": 0,
            "pct_up_to_date": 0,
            "avg_days_to_install": None,
            "total": 0
        })
    installed = Client.objects.filter(app_installee=True).count()
    # Détection de la dernière version déployée
    latest_version = Client.objects.exclude(maj_app__isnull=True).order_by('-maj_app').values_list('maj_app', flat=True).first()
    up_to_date = Client.objects.filter(app_installee=True, maj_app=latest_version).count()
    # Date d'installation via audit log (si dispo)
    from core.models import AuditLog
    from django.db.models import Min
    delays = []
    install_logs = AuditLog.objects.filter(table_name='Client', champs_changes__app_installee__new=True)
    install_dates = install_logs.values('record_id').annotate(first_install=Min('timestamp'))
    for entry in install_dates:
        client = Client.objects.filter(id=entry['record_id']).first()
        if client and hasattr(client, 'date_creation') and client.date_creation and entry['first_install']:
            delta = (entry['first_install'].date() - client.date_creation.date()).days
            delays.append(delta)
    avg_days_to_install = sum(delays) / len(delays) if delays else None
    return Response({
        "pct_installed": round(installed / total * 100, 2),
        "pct_up_to_date": round(up_to_date / total * 100, 2),
        "avg_days_to_install": avg_days_to_install,
        "total": total
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def engagement_kpis(request):
    from django.db.models import Q
    total = Client.objects.count()
    if total == 0:
        return Response({
            "pct_relance_planifiee": 0,
            "pct_demande_aide": 0,
            "pct_clients_notifies": 0,
            "total": 0
        })
    relance = Client.objects.filter(relance_planifiee=True).count()
    demande_aide = Client.objects.filter(a_demande_aide=True).count()
    notifies = Client.objects.filter(notification_client=True).count()
    pct_relance_planifiee = round(relance / total * 100, 2)
    pct_demande_aide = round(demande_aide / total * 100, 2)
    pct_clients_notifies = round(notifies / total * 100, 2)
    return Response({
        "pct_relance_planifiee": pct_relance_planifiee,
        "pct_demande_aide": pct_demande_aide,
        "pct_clients_notifies": pct_clients_notifies,
        "total": total
    })
