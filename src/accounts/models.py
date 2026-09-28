from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Estudante'
        TEACHER = 'teacher', 'Professor'

    REQUIRED_FIELDS = ['email', 'role']

    role = models.CharField(max_length=10, choices=Role.choices)
    college = models.CharField(max_length=150, default='No college')
