# -*- coding: utf-8 -*-
# Copyright (c) CDU

"""Model Docstrings

"""

from __future__ import absolute_import
from __future__ import annotations
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import typing as t

from django.db import transaction

from .models import ApiKey


def generate_messages(qs: t.List[str]) -> t.List[dict]:
    messages = []
    for i, msg in enumerate(qs):
        message = {}
        if i % 2 == 0:
            message['role'] = 'assistant'
        else:
            message['role'] = 'user'
        message['content'] = msg
        messages.append(message)
    return messages


def question(qs: t.List[str], api_key: str) -> t.Generator[str]:
    # openai = importlib.import_module('openai')
    import openai
    openai.api_key = api_key
    openai.proxy = "http://127.0.0.1:10809"
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=generate_messages(qs), stream=True)
        for token in completion:
            resp = token.choices[0].delta
            if char := resp.get("content"):
                yield char
    except Exception as e:
        logging.warning(e)
        with transaction.atomic():
            key = ApiKey.objects.filter(value=api_key).first()
            key.is_valid = False
            key.save()
        yield "服务异常！"
    finally:
        with transaction.atomic():
            key = ApiKey.objects.filter(value=api_key).first()
            key.is_work = False
            key.save()
