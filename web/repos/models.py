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

    def url(self):
        if self.owner == 'library':
            return ("https://hub.docker.com/_/{0}?tab=tags&name={1}"
                    .format(self.name, self.tag)
                    )
        else:
            return ("https://hub.docker.com/r/{0}/{1}/tags?name={2}"
                    .format(self.owner, self.name, self.tag)
                    )


class Watching(models.Model):
    """
    通知設定
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("user", "repository")
