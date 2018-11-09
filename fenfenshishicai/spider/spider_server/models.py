# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
#用户表
class TaskUser(models.Model):
    user_id =  models.IntegerField()
    user_name = models.CharField(max_length=30)    #主键
    user_password =  models.CharField(max_length=30)
    user_status = models.BooleanField()