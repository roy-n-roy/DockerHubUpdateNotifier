import requests
from django.apps import AppConfig
from django.conf import settings
from django.utils.dateparse import parse_datetime


class ReposConfig(AppConfig):
    name = 'repos'

    @staticmethod
    def check_repository(owner, name, tag):
        html = requests.get(
            settings.DOCKER_HUB_API.format(owner, name, tag)
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
