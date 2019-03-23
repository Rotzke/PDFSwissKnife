#!/usr/bin/env python3
"""Archive.org PDF books downloader."""
import logging
import os
import re
import requests
from time import sleep
from multiprocessing.pool import ThreadPool

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                    level=logging.INFO, datefmt='%Y/%m/%dT%H:%M:%S')


def slugify(value):
    """
   Normalizes string, converts to lowercase, removes non-alpha characters,
   and converts spaces to hyphens.
   """
    value = value.encode('ascii', 'ignore')
    value = re.sub('[^\w\s-]', '', value.decode()).strip().lower()
    value = re.sub('[-\s]+', '-', value)

    return value


def get_links():
    """Helper to generate links to PDF files."""
    links = []
    cursor = ''
    url = 'https://archive.org/services/search/v1/scrape?' +\
        'fields=title&q=genealogy&count=10000'

    while True:
        body = requests.get(url + cursor)
        logging.info(f"{body.json().get('total')} URLs left to parse")
        [links.append(i) for i in body.json()['items'] if i not in links]
        cursor_raw = body.json().get('cursor')
        if cursor_raw:
            cursor = f'&cursor={cursor_raw}'
        else:
            return links
        return links


def fetch_url(item):
    if 'census' in item['title'].lower():
        return
    path = os.path.join(directory, slugify(item['title'])[:50] + '.pdf')
    filelink = 'http://archive.org/download/{0}/{0}.pdf'.format(
        item['identifier'])
    if not os.path.exists(path):
        for i in range(10):
            try:
                r = requests.get(filelink, stream=True)
                break
            except Exception as e:
                logging.warning('\tConnection problem, retrying!')
                sleep(5)
        else:
            return
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
            logging.info(f"\t[{item['title']}]...OK")
    return path


if __name__ == "__main__":
    while True:
        items = get_links()
        directory = '/books'
        os.makedirs(directory, exist_ok=True)
        while True:
            try:
                ThreadPool(10).map(fetch_url, items)
                break
            except Exception as e:
                continue
