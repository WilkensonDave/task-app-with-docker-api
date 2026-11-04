from django.shortcuts import render
from task_management import serializers
from rest_framework import (viewsets, mixins, status)
from core.models import (Project, Task, Comment)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from drf_spectacular.utils import(
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma Separated list  of tags IDS to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separted list of Ingredients IDS to filter.',
            )
        ]
    )
)

class ProjectView(viewsets.ModelViewSet):
    """View for managing project"""
    serializer_class = serializers.ProjectDetailSerializer
    authentication_classes =[TokenAuthentication]
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(
            project_owner=self.request.user
        ).order_by("-id").distinct()

    def perform_create(self, serializer):
        """"Create a new project"""
        serializer.save()

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.ProjectSerializer
        elif self.action == 'upload_image':
            return serializers.ProjectImageSerializer
        return self.serializer_class

    @action(
        methods=['POST'],
        detail=True, url_path='upload-image',
        parser_classes=[MultiPartParser, FormParser]
        )
    def upload_image(self, request, pk=None):
        """Upload an image to a project"""
        project = self.get_object()
        serializer = self.get_serializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description="Filter by items assigned to recipes.",
            )
        ]
    )
)


class BaseProjectAttrViewSet(
            mixins.DestroyModelMixin,
            mixins.UpdateModelMixin,
            mixins.ListModelMixin,
            mixins.CreateModelMixin,
            mixins.RetrieveModelMixin,
            viewsets.GenericViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class TaskView(BaseProjectAttrViewSet):
    serializer_class = serializers.TaskSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        """Retrieve task for task owner"""
        # s
        return self.queryset.filter(
            created_by=self.request.user).order_by("-id").distinct()

    def perform_create(self, serializer):
        """"Create a new project"""
        serializer.save(created_by=self.request.user)


class CommentView(BaseProjectAttrViewSet):
    serializer_class = serializers.CommentSerializer
    queryset = Comment.objects.all()

    def get_queryset(self):
        """Retrieve comment for authenticated users"""
        return self.queryset.filter(
            user=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        """create comment"""
        serializer.save(user=self.request.user)

