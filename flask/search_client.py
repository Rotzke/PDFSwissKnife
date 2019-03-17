#!/usr/bin/env python
import os
from time import sleep

import requests


def search_term(term, titlezation):
    search = requests.get(
        f'http://elastic:9200/_search?q=content:/{term}/&_source_include=meta&size=500')

    raw = search.json()

    filenames = []
    if raw['hits']['total'] > 0:
        for num, i in enumerate(raw['hits']['hits']):
            try:
                title = i['_source']['meta']['raw']['pdf:docinfo:title']
            except KeyError:
                title = i['_source']['meta']['raw']['resourceName']
            filenames.append(
                {'filenum': num + 1,
                 'title':
                 title[:100] + '...' if len(title) > 100 else title,
                 'raw_title':
                 title,
                 'filename':
                 '/'.join(['file://',
                           os.path.abspath(__file__).lstrip('/'),
                           'books',
                           i['_source']['meta']['raw']['resourceName']])
                 }
            )
        if titlezation:
            filenames = sorted(filenames, key=lambda k: titlezation.lower() in k['raw_title'].lower(), reverse=True)

    return filenames
