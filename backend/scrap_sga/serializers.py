from rest_framework import serializers
from .models import ScrapDimagazBC, ScrapDimagazBCLine, ScrapProduct, ScrapFournisseur, ScrapFournisseurCentre, ScrapUser

class ScrapDimagazBCLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapDimagazBCLine
        fields = '__all__'

class ScrapDimagazBCSerializer(serializers.ModelSerializer):
    lines = ScrapDimagazBCLineSerializer(many=True, read_only=True)
    class Meta:
        model = ScrapDimagazBC
        fields = '__all__'

class ScrapProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapProduct
        fields = '__all__'

class ScrapFournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapFournisseur
        fields = '__all__'

class ScrapFournisseurCentreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapFournisseurCentre
        fields = '__all__'

class ScrapUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapUser
        fields = '__all__'
