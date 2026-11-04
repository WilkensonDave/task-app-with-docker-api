from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from rest_framework import status
from core.models import (Project, Task)
from django.urls import reverse
from task_management import serializers
from django.contrib.auth import get_user_model

TASK_URL = reverse("project:task-list")

def create_user(email="user2@example.com", username="user2",password="user2@12345"):
    """function to create a user"""
    return get_user_model().objects.create_user(email=email, username=username, password=password)

def task_details(task_id):
    """Function to retrieve a recipe"""
    return reverse("project:task-detail", args=[task_id])

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

class PublicTaskAPITests(TestCase):
    """Private test cases"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test to make sure only authenticate users can access the task list"""
        res = self.client.get(TASK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTaskAPITests(APITestCase):
    """Class to test authenticated users."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)


    def test_create_task(self):
        """Create a task"""
        project = create_project(user=self.user)

        payload = {
            "name":"create api",
            "project":project.id,
            "created_by":self.user.id
        }

        res = self.client.post(TASK_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_retrieve_list_task(self):
        """test to retrieve task list"""
        project= create_project(user=self.user)
        user2 = create_user(email="son@example.com", username="son",  password="son@1234")
        create_task(user=self.user, name="fetch data", project=project, assigned_to=user2)
        create_task(user=self.user, name="dockerize the project", project=project, assigned_to=user2)
        res = self.client.get(TASK_URL)
        tasks = Task.objects.all().order_by("-id")
        serializer = serializers.TaskSerializer(tasks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_single_task(self):
        """test to retrieve a single task"""
        project = create_project(user=self.user)
        task = create_task(user=self.user, project=project)
        url = task_details(task.id)

        res = self.client.get(url)
        serializer = serializers.TaskSerializer(task)
        self.assertEqual(res.data, serializer.data)

    def test_to_return_task_for_task_owner(self):
        """Test to return task for correct user"""
        user2 = create_user(email="son@example.com", username="son",  password="son@1234")
        project1= create_project(user=self.user)
        project2= create_project(user=user2)
        task = create_task(user=user2, name="create the api", project=project2)
        create_task(user=self.user, name="create the database", project=project1)
        self.client.force_authenticate(user=user2)

        res = self.client.get(TASK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], task.name)
        self.assertEqual(res.data[0]['id'], task.id)

    def test_to_delete_task_for_auth_user(self):
        """delete task"""
        project= create_project(user=self.user)
        task = create_task(user=self.user, name="deploy app", project=project)
        url = task_details(task.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tasks = Task.objects.filter(created_by=self.user)
        self.assertFalse(tasks.exists())

    def test_update_task(self):
        """Test to update a task"""
        project= create_project(user=self.user)
        task = create_task(user=self.user, name="deploy react", project=project)

        payload = {
            "name":"fix bug before deploy",
            "project":project.id

        }
        url = task_details(task.id)
        res = self.client.put(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

