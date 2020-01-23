import requests
from urllib.parse import urlparse, parse_qs
from django.apps import AppConfig
from django.conf import settings
from django.utils.dateparse import parse_datetime


class ReposConfig(AppConfig):
    name = 'repos'

    @staticmethod
    def check_repository(owner, name, tag):
        html = requests.get(
            settings.DOCKER_HUB_API.format(owner, name, tag, 1)
        )
        if html.status_code == requests.codes.ok:
            json = html.json()
            if 'last_updated' in json:
                last_updated = None
                try:
                    last_updated = parse_datetime(json['last_updated'])
                except ValueError:
                    pass
                return last_updated

        return None

    @staticmethod
    def get_tags(owner, name, page):
        html = requests.get(
            settings.DOCKER_HUB_API.format(owner, name, '', page)
        )
        if html.status_code != requests.codes.ok:
            return None

        json = html.json()
        tags = []
        if 'results' not in json or 'count' not in json or json['count'] <= 0:
            return None

        json['results']
        for tag in json['results']:
            if 'name' in tag:
                tags.append(tag['name'])

        next = None
        if 'next' in json and json['next'] is not None:
            url = urlparse(json['next'])
            if url.query is not None:
                query = parse_qs(url.query)
                if 'page' in query:
                    next = query['page']

        return {"tags": tags, "next": next}
