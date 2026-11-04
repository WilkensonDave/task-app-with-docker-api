from django.shortcuts import render
from rest_framework import generics, authentication, permissions
from users.serializers import CreateUserSerializer,AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

# Create your views here.

class UserRegisterView(generics.CreateAPIView):
    """View for registering a new user."""
    serializer_class = CreateUserSerializer

class CreateTokenView(ObtainAuthToken):
    """View to create a token for users with validated data"""
    serializer_class = AuthTokenSerializer
    render_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Class to manage authenticated user."""
    serializer_class = CreateUserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """retrieve and return the authenticated user."""
        return self.request.user