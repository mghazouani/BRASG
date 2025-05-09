from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Client, AuditLog, DashboardConfig
from .serializers import UserSerializer, ClientSerializer, AuditLogSerializer, DashboardConfigSerializer
from .views_api import ClientPageNumberPagination

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ClientPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut_general', 'region', 'langue', 'a_demande_aide', 'app_installee']
    search_fields = ['nom_client', 'sap_id', 'telephone']
    ordering_fields = [
        'date_creation', 'nom_client', 'sap_id', 'telephone', 'langue', 'statut_general',
        'canal_contact', 'notification_client', 'date_notification', 'app_installee', 'maj_app',
        'a_demande_aide', 'nature_aide', 'commentaire_agent', 'ville', 'region', 'segment_client',
        'relance_planifiee'
    ]

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]

class DashboardConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """Retourne la configuration paramétrable du dashboard"""
    queryset = DashboardConfig.objects.all()
    serializer_class = DashboardConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Désactiver la pagination pour renvoyer la liste complète
    pagination_class = None
