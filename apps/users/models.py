# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Users(models.Model):
    username = models.CharField(unique=True, max_length=64)
    email = models.CharField(unique=True, max_length=100)
    password = models.TextField()
    university = models.ForeignKey('Universities', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    department = models.ForeignKey('Departments', models.DO_NOTHING, blank=True, null=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class UserSkills(models.Model):
    pk = models.CompositePrimaryKey('user_id', 'skill_id')
    user = models.ForeignKey(Users, models.DO_NOTHING)
    skill = models.ForeignKey('Skills', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_skills'


class UserInterests(models.Model):
    pk = models.CompositePrimaryKey('user_id', 'tag_id')
    user = models.ForeignKey(Users, models.DO_NOTHING)
    tag = models.ForeignKey('Tags', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_interests'
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
        managed = False
        db_table = 'skills'
