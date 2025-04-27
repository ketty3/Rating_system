
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    ROLES = [
        ('ST', 'Студент'),
        ('TE', 'Преподаватель'),
        ('AD', 'Администратор'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=50, verbose_name='Отчество', blank=True)
    role = models.CharField(max_length=2, choices=ROLES, verbose_name='Роль')
    group = models.CharField(max_length=20, verbose_name='Группа', blank=True, null=True)


    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name} {self.middle_name or ""}'

    def get_full_name(self):
        return f'{self.user.last_name} {self.user.first_name} {self.middle_name or ""}'

