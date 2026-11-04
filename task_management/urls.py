from django.urls import path, include
from rest_framework.routers import DefaultRouter
from task_management import views


router = DefaultRouter()
router.register("projects", views.ProjectView)
router.register("tasks", views.TaskView)
router.register("comments", views.CommentView)
app_name = 'project'


urlpatterns = [
    path("", include(router.urls))
]
