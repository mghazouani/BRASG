from rest_framework import routers
from .api_views import (
    ScrapDimagazBCViewSet, ScrapDimagazBCLineViewSet,
    ScrapProductViewSet, ScrapFournisseurViewSet, ScrapFournisseurCentreViewSet, ScrapUserViewSet
)

router = routers.DefaultRouter()
router.register(r'bc', ScrapDimagazBCViewSet)
router.register(r'bc-line', ScrapDimagazBCLineViewSet)
router.register(r'product', ScrapProductViewSet)
router.register(r'fournisseur', ScrapFournisseurViewSet)
router.register(r'fournisseur-centre', ScrapFournisseurCentreViewSet)
router.register(r'user', ScrapUserViewSet)

urlpatterns = router.urls
