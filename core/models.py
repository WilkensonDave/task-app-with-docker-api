from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import os
from django.conf import settings
# Create your models here.

def project_image_file_path(instance, filename):
    """Function to generate a file path for a new project image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join("uploads", 'project', filename)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    profile_image =models.ImageField(upload_to="user-images", null=True, blank=True)
    USERNAME_FIELD="email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class Project(models.Model):
    """project object"""
    project_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="project_owners")
    members = models.ManyToManyField(settings.AUTH_USER_MODEL,  related_name="members", blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(null=True, upload_to=project_image_file_path)

    def __str__(self):
        return self.title

class Task(models.Model):
    """Task object"""
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="tasks")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_tasks")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="assigned_tasks")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Comment(models.Model):
    """comment object"""
    task = models.ForeignKey("Task", on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.CharField(max_length=300, blank=False)

    def __str__(self):
        return f"Comment for - {self.task.name}"




