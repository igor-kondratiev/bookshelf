# coding=utf-8
import os

from django.conf import settings


STOPWORDS_FILE = os.path.join(settings.BASE_DIR, 'books', 'tools', 'stopwords.list')

# Сохраняем их в мапу чтоб быстрее искать
STOPWORDS_LIST = {}
with open(STOPWORDS_FILE, 'r') as f:
    words = map(lambda x: x.strip('\n'), f.readlines())
    for word in words:
        STOPWORDS_LIST[word] = 0
