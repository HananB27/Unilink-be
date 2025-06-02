# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone


class Posts(models.Model):
    user = models.ForeignKey('users.Users', on_delete=models.CASCADE, blank=True, null=True)
    university = models.ForeignKey('universities.Universities', on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=255)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'posts'


class PostTags(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, primary_key=True)
    tag = models.ForeignKey('Tags', on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'post_tags'
        unique_together = ('post', 'tag')



class Tags(models.Model):
    name = models.CharField(unique=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'tags'
