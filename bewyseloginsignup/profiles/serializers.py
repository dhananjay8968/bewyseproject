from rest_framework import serializers
from profiles.models import UserProfile

class UserProfileSerializer(serializers.Serializer):
    full_name = serializers.SerializerMethodField()
    def get_full_name(self,obj):
        return f"{obj.first_name}-{obj.last_name}"