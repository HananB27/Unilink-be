# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from pgvector.django import VectorField

from apps.posts.models import Tags

ROLES=[
        ('student', 'Student'),
        ('professor', 'Professor'),
        ('university', 'University'),
        ('department', 'Department'),
        ('company', 'Company'),
        ('admin', 'Admin'),
    ]

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # hashes password correctly
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(unique=True, max_length=64)
    email = models.CharField(unique=True, max_length=100)
    password = models.TextField()
    university = models.ForeignKey('universities.Universities', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    department = models.ForeignKey('universities.Departments', models.DO_NOTHING, blank=True, null=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    role = models.CharField(max_length=64, choices=ROLES, default='student')

    embedding = VectorField(dimensions=768, blank=True, null=True)

    profile_picture = models.ImageField(
        upload_to='user-profile-picture',
        db_column='profile_picture',
        blank=True,
        null=True
    )

    groups = None
    user_permissions = None

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def delete(self, *args, **kwargs):
        self.profile_picture.delete()
        super(Users, self).delete(*args, **kwargs)

    class Meta:
        db_table = 'users'


class UserSkills(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING)
    skill = models.ForeignKey('Skills', models.DO_NOTHING)

    class Meta:
        # managed = False
        db_table = 'user_skills'


class UserInterests(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING, primary_key=True, db_column='user_id')
    tag = models.ForeignKey(Tags, models.DO_NOTHING, db_column='tag_id')

    class Meta:
        # managed = False
        db_table = 'user_interests'
        unique_together = (('user', 'tag'),)

    def __str__(self):
        return f"{self.user.email} - {self.tag.name}"
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Skills(models.Model):
    name = models.CharField(unique=True, max_length=50)

    class Meta:
        # managed = False
        db_table = 'skills'