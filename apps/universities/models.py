# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Universities(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'universities'


class Departments(models.Model):
    university = models.ForeignKey(Universities, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'departments'
