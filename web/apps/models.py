from django.db import models
from django.contrib.auth import get_user_model


class Repository(models.Model):
    """
    Docker Hubのリポジトリ
    """
    dockerhub_user = models.CharField(max_length=1024)
    name = models.CharField(max_length=1024)
    tag = models.CharField(max_length=1024)
    last_updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("dockerhub_user", "name", "tag")

    def __str__(self):
        u = '' if self.dockerhub_user == 'library' \
            else self.dockerhub_user + '/'
        return u + self.name + ':' + self.tag


class Watching(models.Model):
    """
    通知設定
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("user", "repository")
