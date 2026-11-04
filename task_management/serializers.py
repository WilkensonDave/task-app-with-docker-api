from rest_framework import serializers
from core.models import (Project, Comment, Task)


class CommentSerializer(serializers.ModelSerializer):
    """comment serializers"""
    class Meta:
        model = Comment
        fields = ['id', 'description', 'task', 'user']
        read_only_fields=['id']

class TaskSerializer(serializers.ModelSerializer):
    """serialize tasks"""
    comments = CommentSerializer(many=True, required=False)
    class Meta:
        model = Task
        fields = ['id', 'name', 'project', 'comments', 'created_by', 'assigned_to']
        read_only_fields = ['id']

    def _get_or_create_comments(self, comments, task):
            """Private method to create a project with a comment"""
            auth_user = self.context['request'].user
            for comment in comments:
                Comment.objects.create(tasks=task, user=auth_user, **comment)

    def create(self, validated_data):
        """create task"""
        comments = validated_data.pop("comments", [])
        task = Task.objects.create(**validated_data)
        self._get_or_create_comments(comments, task)
        return task

class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for project"""
    tasks = TaskSerializer(many=True, required=False)
    class Meta:
        model = Project
        fields = [
            "title", 'id', 'description', 'project_owner',
            'members', 'tasks'
        ]
        read_only_fields = ['id']

    def _get_or_create_tasks(self, tasks, project):
        """Private method to create a project with a task"""
        auth_user = self.context['request'].user
        for task in tasks:
            Task.objects.create(project=project, created_by=auth_user, **task)

    def create(self, validated_data):
        """create project"""
        members = validated_data.pop("members", [])
        project = Project.objects.create(**validated_data)
        project.members.set(members)
        return project


class ProjectDetailSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['description', 'image']

class ProjectImageSerializer(serializers.ModelSerializer):
    """serializer for uploading images to the project"""
    class Meta:
        model = Project
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {"image":{'required':'True'}}





