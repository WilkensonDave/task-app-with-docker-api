from django.contrib import admin
from core import models
# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Comment)
admin.site.register(models.Task)
admin.site.register(models.Project)