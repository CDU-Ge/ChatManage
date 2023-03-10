# -*- coding: utf-8 -*-
# Copyright (c) CDU

"""Model Docstrings

"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from __future__ import annotations

import typing as t
import importlib
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
    print(f'question key: {api_key}')
    openai.proxy = 'http://127.0.0.1:10809'
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=generate_messages(qs), stream=True)
        for token in completion:
            resp = token.choices[0].delta
            if char := resp.get("content"):
                yield char
    except Exception as e:
        with transaction.atomic():
            key = ApiKey.objects.filter(value=api_key).first()
            key.is_valid = False
            key.save()
        yield "服务异常！"


if __name__ == '__main__':
    with open(r"H:\Projects\ChatManage\r.txt", 'r', encoding='utf8') as f:
        content = f.readlines()
    record = {'qs': []}
    buff = []
    for i in content:
        if i.startswith(('# ', 'assistant')):
            if buff:
                record['qs'].append(''.join(buff))
                buff.clear()
            i = i.replace('# ', '').replace('assistant', '').strip()
        buff.append(i)
    print(len(''.join(record['qs'])))
    # with open('record.json', 'w', encoding='utf8') as f:
    #     import json
    #
    #     json.dump(record, f)
    _qs = []
    # while 1:
    #     prompt = input('# ')
    #     if prompt == 'reset':
    #         _qs.clear()
    #     if prompt == 'quit':
    #         break
    #     _qs.append(prompt)
    #     question(_qs, "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")
