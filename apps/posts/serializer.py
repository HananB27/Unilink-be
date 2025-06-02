from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Posts
from .models import Tags

User = get_user_model()

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email')

class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Posts
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 'image']
        read_only_fields = ['author','created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['created_at']