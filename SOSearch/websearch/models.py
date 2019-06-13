# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Question(models.Model):
    # id = models.IntegerField(primary_key=True)
    title = models.TextField()
    link = models.TextField()
    asked = models.TextField()
    viewed = models.IntegerField()
    active = models.TextField(blank=True, null=True)
    vote = models.IntegerField()
    star = models.IntegerField(blank=True, null=True)
    content = models.TextField()
    status = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'question'


class Answer(models.Model):
    # id = models.IntegerField(primary_key=True)
    # question = models.ForeignKey(Question, on_delete=models.CASCADE)
    rid = models.IntegerField()
    vote = models.IntegerField()
    accepted = models.IntegerField()
    content = models.TextField()

    class Meta:
        managed = False
        db_table = 'answer'


class User(models.Model):
    # id = models.IntegerField(primary_key=True)
    rid = models.IntegerField()
    name = models.TextField(blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    time = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    is_owner = models.IntegerField()
    revision = models.TextField(blank=True, null=True)
    reputation = models.IntegerField(blank=True, null=True)
    gold = models.IntegerField(blank=True, null=True)
    silver = models.IntegerField(blank=True, null=True)
    bronze = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'


class Comment(models.Model):
    # id = models.IntegerField(primary_key=True)
    rid = models.IntegerField()
    score = models.IntegerField()
    content = models.TextField()
    user = models.TextField()
    user_href = models.TextField()
    time = models.TextField()

    class Meta:
        managed = False
        db_table = 'comment'


class LinkedQuestion(models.Model):
    # id = models.IntegerField(primary_key=True)
    rid = models.IntegerField()
    qid = models.IntegerField()
    title = models.TextField()
    link = models.TextField()
    vote = models.IntegerField()
    accepted = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'linked_question'


class RelatedQuestion(models.Model):
    # id = models.IntegerField(primary_key=True)
    rid = models.IntegerField()
    qid = models.IntegerField()
    title = models.TextField()
    link = models.TextField()
    vote = models.IntegerField()
    accepted = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'related_question'
