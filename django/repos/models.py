from django.contrib.auth import get_user_model
from django.db import models


class Repository(models.Model):
    """
    Docker Hubのリポジトリ
    """
    owner = models.CharField(max_length=1024)
    name = models.CharField(max_length=1024)
    tag = models.CharField(max_length=1024)
    last_updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("owner", "name", "tag")

    def __str__(self):
        u = '' if self.owner == 'library' \
            else self.owner + '/'
        return u + self.name + ':' + self.tag

    def get_url(self):
        if self.owner == 'library':
            return (
                f'https://hub.docker.com/_/{self.name}'
                f'?tab=tags&name={self.tag}'
            )
        else:
            return (
                f'https://hub.docker.com/r/{self.owner}/{self.name}/tags'
                f'?name={self.tag}'
            )


class Watching(models.Model):
    """
    通知設定
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("user", "repository")
