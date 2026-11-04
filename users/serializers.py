
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _

from rest_framework import serializers

class CreateUserSerializer(serializers.ModelSerializer):
    "Serializer for creating user"
    class Meta:
        model = get_user_model()
        fields = ['email', "password", "username"]
        extra_kwargs = {"password":{"write_only":True, "min_length":8}}

    def create(self, validated_data):
        """create and return a new user"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update user profile and return user"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type":"password"},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """validate date and authenticate the user."""
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )

        if not user:
            message = _("Unable to authenticate with the provided credentials.")
            raise serializers.ValidationError(message, code="authorization")

        attrs["user"] = user
        return attrs