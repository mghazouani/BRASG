from rest_framework import serializers
from .models import User, Client, AuditLog, DashboardConfig, Ville
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image
import io
from django.core.files.base import ContentFile

THUMB_SIZES = {
    'small': (64, 64),
    'medium': (192, 192),
    'large': (384, 384),
}

PLACEHOLDER_URL = '/static/img/avatar_placeholder.png'

class UserSerializer(serializers.ModelSerializer):
    image_profil = serializers.SerializerMethodField()
    image_profil_small = serializers.SerializerMethodField()
    image_profil_medium = serializers.SerializerMethodField()
    image_profil_large = serializers.SerializerMethodField()

    def _get_placeholder_url(self, request):
        if request is not None:
            return request.build_absolute_uri(PLACEHOLDER_URL)
        return PLACEHOLDER_URL

    def get_image_profil(self, obj):
        request = self.context.get('request')
        if obj.image_profil and hasattr(obj.image_profil, 'url'):
            url = obj.image_profil.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return self._get_placeholder_url(request)

    def get_image_profil_small(self, obj):
        return self._get_thumb_url(obj, 'small', placeholder=True)
    def get_image_profil_medium(self, obj):
        return self._get_thumb_url(obj, 'medium', placeholder=True)
    def get_image_profil_large(self, obj):
        return self._get_thumb_url(obj, 'large', placeholder=True)

    def _get_thumb_url(self, obj, size, placeholder=False):
        request = self.context.get('request')
        if obj.image_profil and hasattr(obj.image_profil, 'url'):
            base_url = obj.image_profil.url
            thumb_url = base_url.replace('/avatars/', f'/avatars/thumbnails/{size}/')
            if request is not None:
                return request.build_absolute_uri(thumb_url)
            return thumb_url
        if placeholder:
            return self._get_placeholder_url(request)
        return None

    def validate_image_profil(self, image):
        # Limiter la taille à 2 Mo
        max_size = 2 * 1024 * 1024
        if image and image.size > max_size:
            raise ValidationError('La taille de l\'image ne doit pas dépasser 2 Mo.')
        # Limiter le type
        valid_types = ['image/jpeg', 'image/png', 'image/gif']
        if image and hasattr(image, 'content_type') and image.content_type not in valid_types:
            raise ValidationError('Format d\'image non autorisé. JPEG, PNG ou GIF uniquement.')
        # Limiter la résolution
        max_width, max_height = 600, 600
        img = Image.open(image)
        if img.width > max_width or img.height > max_height:
            raise ValidationError(f"La résolution maximale autorisée est {max_width}x{max_height} pixels.")
        return image

    def create(self, validated_data):
        image = validated_data.get('image_profil', None)
        instance = super().create(validated_data)
        if image:
            self._create_thumbnails(instance)
        return instance

    def update(self, instance, validated_data):
        image = validated_data.get('image_profil', None)
        instance = super().update(instance, validated_data)
        if image:
            self._create_thumbnails(instance)
        return instance

    def _create_thumbnails(self, instance):
        if not instance.image_profil:
            return
        img = Image.open(instance.image_profil)
        img = img.convert('RGB')
        for size_name, size in THUMB_SIZES.items():
            thumb = img.copy()
            thumb.thumbnail(size)
            thumb_io = io.BytesIO()
            thumb.save(thumb_io, format='JPEG')
            thumb_name = instance.image_profil.name.replace('avatars/', f'avatars/thumbnails/{size_name}/').rsplit('.', 1)[0] + '.jpg'
            instance.image_profil.storage.save(thumb_name, ContentFile(thumb_io.getvalue()))

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_active', 'created_at', 'last_login',
            'image_profil', 'image_profil_small', 'image_profil_medium', 'image_profil_large'
        ]

class ClientSerializer(serializers.ModelSerializer):
    # Ville référencée, affichée par son nom au lieu de son ID
    ville = serializers.SlugRelatedField(slug_field='nom', queryset=Ville.objects.all())
    region = serializers.CharField(read_only=True)
    class Meta:
        model = Client
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

class DashboardConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardConfig
        fields = '__all__'
