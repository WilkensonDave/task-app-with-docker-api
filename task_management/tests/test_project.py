from core.models import (Project, Task, Comment)
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import TestCase
import tempfile
from PIL import Image
import os

from task_management.serializers import ProjectSerializer, ProjectDetailSerializer

PROJECT_URL = reverse("project:project-list")

def create_user(email="user@example.com", username="user", password="user@#12345"):
    """this function will create and return a new user"""
    return get_user_model().objects.create_user(email=email, username=username, password=password)

def project_details(project_id):
    """this function will return the details for a project"""
    return reverse("project:project-detail", args=[project_id])

def image_upload_url(project_id):
    """create and return and image"""
    return reverse('project:project-upload-image', args=[project_id])

def create_project(user, **params):
    """Create and return a project"""
    defaults = {
        "title":"project",
        "description":"we are creating a project",
    }

    defaults.update(params)

    project = Project.objects.create(project_owner=user, **defaults)
    return project


class PublicProjectAPITests(TestCase):
    """Test unauthenticated API request"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test to make sure authentication is required to access any project."""
        res = self.client.get(PROJECT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateProjectAPITests(APITestCase):
    """Test for authenticated request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="dave@example.com", password="dave!@12345", username="Dave")
        self.user1 = create_user(email="bob@example.com", password="bob!@12345", username="bob")
        self.client.force_authenticate(self.user)

    def test_retrieve_list_project(self):
        """Retrieve project lists."""

        create_project(user=self.user)
        create_project(user=self.user)

        res = self.client.get(PROJECT_URL)
        projects = Project.objects.all().order_by("-id")
        serializer = ProjectSerializer(projects, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_project(self):
        """Create project"""
        payload ={
            "title":"create app",
            "description":"we need to create this project",
            "project_owner":self.user.id
        }
        self.client.force_authenticate(user=self.user)
        res = self.client.post(PROJECT_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_only_authenticated_user_can_retrieve_list_of_projects(self):
        """Test to check only authenticated user can retrieve a list of projects"""
        self.client.force_authenticate(user=None)
        res = self.client.get(PROJECT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_return_success_message_for_authenticated_user(self):
        """Test to return a successful message if the user is authenticated."""
        res = self.client.get(PROJECT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_limit_project_list_only_to_authenticated_project_onwer(self):
        """Test to return projects for only project_onwer"""

        other_user = create_user(
            username="Son",
            password="sondave@12345",
            email="son@example.com"
        )

        create_project(user=self.user)
        create_project(user=other_user)
        res = self.client.get(PROJECT_URL)
        project = Project.objects.filter(project_owner=self.user)
        serializer = ProjectSerializer(project, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_single_project_details(self):
        """Test to retrieve a single project details"""
        project = create_project(user=self.user)
        url = project_details(project.id)
        res = self.client.get(url)
        serializer = ProjectDetailSerializer(project)
        self.assertEqual(res.data, serializer.data)

    def test_create_new_project(self):
        """Test to create a new project"""

        payload = {
            "description":"you need to fix all the bugs on the home page.",
            "title":"Fix react bugs"
        }

        res = self.client.post(PROJECT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(id=res.data["id"])

        for k, v in payload.items():
            self.assertEqual(getattr(project, k), v)

    def test_update_existing_project(self):
        """Test to update existing project"""
        self.client.force_authenticate(user=self.user1)
        project = create_project(title="Fix backend bugs", user=self.user1, description="Improve the  backend logic")
        payload = {
            "title":"Fix all the backend bugs for time complexity",
            "description":"We need to fix all the bugs and push the code to github"
        }

        url = project_details(project.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        project.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(project, k), v)

        self.assertEqual(project.project_owner, self.user1)

    def test_partial_update_existing_project(self):
        """Test for partial update an existing project"""
        self.client.force_authenticate(user=self.user1)
        project = create_project(title="Udate purchase button", user=self.user1, description="change the color of the purchase button")

        payload ={
            "title":"Update the purchase button"
        }

        url = project_details(project.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        self.assertEqual(project.title, payload["title"])
        self.assertEqual(project.project_owner, self.user1)

    def test_change_project_owner(self):
        """Test to change the project owner"""
        self.client.force_authenticate(user=self.user1)
        new_user = create_user(email="wil@example.com", username="Wil", password="wil#1234")
        project = create_project(user=self.user1)
        payload = {
            "user":new_user.id
        }

        url = project_details(project.id)
        self.client.patch(url, payload)
        project.refresh_from_db()
        self.assertEqual(project.project_owner, self.user1)

    def test_delete_project(self):
        """Test to delete a project"""
        project = create_project(user=self.user)
        url = project_details(project.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=project.id).exists())


    def test_user_cannot_delete_others_project(self):
        """Test to return an error if a user tries to delete others recipe"""
        new_user = create_user(email="wil@example.com", username="Wil", password="wil#1234")
        project = create_project(user=new_user)
        url = project_details(project.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Project.objects.filter(id=project.id).exists())


    def test_filter_by_tasks(self):
        """Test to filter projects by task"""
        p1 = create_project(user=self.user, title="Design the home page")
        p2 = create_project(user=self.user, title="design the backend")

        task1 = Task.objects.create(project=p1, name="create the API key")
        task2 = Task.objects.create(project=p2, name="create the react ap")


        params = {"tasks":f'{task1.id}, {task2.id}'}
        res = self.client.get(PROJECT_URL, params)
        self.client.force_authenticate(user=self.user1)
        p3 = create_project(user=self.user1, title="Create docker image")
        s1 = ProjectSerializer(p1)
        s2 = ProjectSerializer(p2)
        s3 = ProjectSerializer(p3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

class ImageUploadTests(TestCase):
    """Test to upload image for each project"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='dave@example.com', username='Dave', password="dave###!!!123")
        self.client.force_authenticate(self.user)
        self.project = create_project(user=self.user)

    def tearDown(self):
        self.project.image.delete()

    def test_upload_image(self):
        url = image_upload_url(self.project.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {'image':image_file}
            res = self.client.post(url, payload, format='multipart')

        self.project.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.project.image.path))

    def test_upload_image_bad_request(self):
        """Test to return error for invalid image"""
        url = image_upload_url(self.project.id)
        payload = {"image":"notaniamge"}
        res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)









































