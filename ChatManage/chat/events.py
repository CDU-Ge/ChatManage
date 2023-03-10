# -*- coding: utf-8 -*-
# Copyright (c) CDU

"""Model Docstrings

"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from __future__ import annotations

import logging
import typing as t

from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import transaction
from .models import ChatUser


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created,**kwargs):
    """"""
    if created:
        logging.info(f'Create User Profile. {instance}')
        ChatUser.objects.create(user=instance)