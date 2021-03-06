from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator, MinLengthValidator, FileExtensionValidator
import uuid, os

class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('users must have an username')

        if not password:
            raise ValueError('users must provide a password')

        user = self.model(
            username = username,
        )

        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, username, password):
        user = self.create_user(
            username,
            password=password
        )

        user.is_staff = True
        user.is_superuser = True
        
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    '''Custom User models extending AbstractBaseUser class, an auto incrementing uid is automatically attached to this model by Django'''

    username = models.CharField(max_length=256, unique=True ,validators=[RegexValidator(regex='^[aA][.^\S]*[01]$', 
                                message='username must start with a/A and ends with 0/1')])
    join_date = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta():
        verbose_name = "User"

def task_upload_location(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('tasks', filename)


class Task(models.Model):
    ''' Task model having a foreign key of user '''
    
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='tasks')
    task_title = models.CharField(max_length=200, validators=[MinLengthValidator(limit_value=10)])
    task_description = models.CharField(max_length=2000, blank=True)
    task_pic = models.FileField(null=True, blank=True, upload_to=task_upload_location)
    create_time_stamps = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} | {self.task_title}'

    class Meta:
        ordering = ('-create_time_stamps',)
