from django.urls import path, include
from rest_framework import routers
from .views_api import ClientViewSet, AuditLogViewSet, MeView, MeUpdateView, ChangePasswordView, CustomTokenObtainPairView, DeleteAvatarView, VilleViewSet, adoption_kpis, engagement_kpis

router = routers.DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'villes', VilleViewSet)
router.register(r'auditlogs', AuditLogViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/me/', MeView.as_view(), name='me'),
    path('api/me/update/', MeUpdateView.as_view(), name='me-update'),
    path('api/me/avatar/', DeleteAvatarView.as_view(), name='delete-avatar'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('api/kpi/adoption/', adoption_kpis, name='kpi-adoption'),
    path('api/kpi/engagement/', engagement_kpis, name='kpi-engagement'),
]
