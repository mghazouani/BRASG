from rest_framework import viewsets
from .models import ScrapDimagazBC, ScrapDimagazBCLine, ScrapProduct, ScrapFournisseur, ScrapFournisseurCentre, ScrapUser
from .serializers import ScrapDimagazBCSerializer, ScrapDimagazBCLineSerializer, ScrapProductSerializer, ScrapFournisseurSerializer, ScrapFournisseurCentreSerializer, ScrapUserSerializer

class ScrapDimagazBCViewSet(viewsets.ModelViewSet):
    queryset = ScrapDimagazBC.objects.all().order_by('-id')
    serializer_class = ScrapDimagazBCSerializer

class ScrapDimagazBCLineViewSet(viewsets.ModelViewSet):
    queryset = ScrapDimagazBCLine.objects.all().order_by('-id')
    serializer_class = ScrapDimagazBCLineSerializer

class ScrapProductViewSet(viewsets.ModelViewSet):
    queryset = ScrapProduct.objects.all().order_by('-id')
    serializer_class = ScrapProductSerializer

class ScrapFournisseurViewSet(viewsets.ModelViewSet):
    queryset = ScrapFournisseur.objects.all().order_by('-id')
    serializer_class = ScrapFournisseurSerializer

class ScrapFournisseurCentreViewSet(viewsets.ModelViewSet):
    queryset = ScrapFournisseurCentre.objects.all().order_by('-id')
    serializer_class = ScrapFournisseurCentreSerializer

class ScrapUserViewSet(viewsets.ModelViewSet):
    queryset = ScrapUser.objects.all().order_by('-id')
    serializer_class = ScrapUserSerializer
