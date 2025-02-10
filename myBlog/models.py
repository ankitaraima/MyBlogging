from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    type = models.CharField(max_length=100, choices=[('admin', 'admin'), ('user', 'user'), ('manager', 'manager')], default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.fname} {self.lname} {self.id}"

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=100, choices=[('tech', 'tech'), ('sports', 'sports'), ('entertainment', 'entertainment')], default='lifestyle')
    image_id = models.IntegerField()
    author = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title} - {self.author}"

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    post_id = models.IntegerField()
    user_id = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

class like_share(models.Model):
    id = models.AutoField(primary_key=True)
    post_id = models.IntegerField()
    user_id = models.IntegerField(default=None)
    like = models.IntegerField(default=0)
    share = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.post_id} - {self.user_id} - {self.like} - {self.share}"