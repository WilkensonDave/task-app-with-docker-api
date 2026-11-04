from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import (Task, Comment, Project)
from task_management import serializers

COMMENT_URL = reverse("project:comment-list")

def create_user(email="user@example.com", username="user", password="user@#12345"):
    """this function will create and return a new user"""
    return get_user_model().objects.create_user(
        email=email, username=username, password=password)

def comment_details(comment_id):
    """return a comment"""
    return reverse("project:comment-detail", args=[comment_id])

def create_project(user, **params):
    """Create and return a project"""
    defaults = {
        "title":"project",
        "description":"we are creating a project",
    }

    defaults.update(params)

    project = Project.objects.create(project_owner=user, **defaults)
    return project

def create_task(user, **params):
    """function to create a task"""
    defaults = {
        "name":"React router"
    }
    defaults.update(params)

    task = Task.objects.create(created_by=user, **defaults)
    return task

def create_comment(user, **params):
    """function to create a comment"""

    defauls = {
        "description":"task is done"
    }

    defauls.update(params)
    comment = Comment.objects.create(user=user, **defauls)
    return comment

class PublicCommentAPITests(TestCase):
    """Private test cases"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test to make sure only auth users can access comments"""
        res = self.client.get(COMMENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCommentAPITests(APITestCase):
    """private class for the comment api"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_to_retrieve_list_comments(self):
        """test to retrieve a list of comment"""
        project= create_project(user=self.user)
        user2 = create_user(email="user3@example.com", username="user3", password="user3@12345")
        task = create_task(user=user2, project=project, name="push code to github")
        create_comment(user=user2, task=task, description="task completed")
        create_comment(user=user2, task=task, description="task needs to review")
        self.client.force_authenticate(user=user2)
        res = self.client.get(COMMENT_URL)
        comments = Comment.objects.all().order_by("-id")
        serializer = serializers.CommentSerializer(comments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_return_comment_for_created_user(self):
        """Test to return a comment for the commented user."""

        user1 = create_user(email="chau@example.com", username="chau", password="chau!12334")
        project1= create_project(user=self.user)
        task = create_task(user=user1, name="create the api", project=project1)
        comment = create_comment(user=user1, task=task)
        self.client.force_authenticate(user=user1)
        res = self.client.get(COMMENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['description'], comment.description)
        self.assertEqual(res.data[0]['id'], comment.id)

    def test_delete_comment(self):
        """Test to delelete a comment"""
        project= create_project(user=self.user)
        user2 = create_user(email="user3@example.com", username="user3", password="user3@12345")
        task = create_task(user=user2, project=project, name="push code to github")
        comment = create_comment(user=user2, task=task, description="task completed")
        self.client.force_authenticate(user=user2)
        url = comment_details(comment.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        comments = Comment.objects.filter(user=user2)
        self.assertFalse(comments.exists())

    def test_update_comment(self):
        """test to update a comment"""
        project= create_project(user=self.user)
        user2 = create_user(email="user3@example.com", username="user3", password="user3@12345")
        task = create_task(user=user2, project=project, name="push code to github")
        comment = create_comment(user=user2, task=task, description="task completed")
        payload = {
            "description":"there's a new update to work on."
        }
        self.client.force_authenticate(user=user2)
        url = comment_details(comment.id)
        res = self.client.put(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)








