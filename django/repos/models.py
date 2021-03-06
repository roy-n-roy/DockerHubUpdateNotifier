from django.contrib.auth import get_user_model
from django.db import models


class Repository(models.Model):
    """
    Docker Hubのリポジトリ
    """
    owner = models.CharField(max_length=1024)
    name = models.CharField(max_length=1024)

    class Meta:
        unique_together = ("owner", "name")

    def __str__(self):
        u = '' if self.owner == 'library' \
            else self.owner + '/'
        return u + self.name


class RepositoryTag(models.Model):
    """リポジトリ+タグ"""
    repository = models.ForeignKey(Repository, models.PROTECT)
    name = models.CharField(max_length=1024)
    last_updated = models.DateTimeField(null=False, blank=False)

    class Meta:
        unique_together = ("repository", "name")

    def __str__(self):
        return f'{self.repository}:{self.name}'

    def get_url(self):
        if self.repository.owner == 'library':
            return (
                f'https://hub.docker.com/_/{self.repository.name}'
                f'?tab=tags&name={self.name}'
            )
        else:
            return (
                f'https://hub.docker.com/r/{self.repository.owner}/'
                f'{self.repository.name}/tags?name={self.name}'
            )

    def history_count(self):
        hists = RepositoryTagHistory.objects.filter(repository_tag=self)
        return 0 if hists is None else hists.count()


class RepositoryTagHistory(models.Model):
    """
    リポジトリ+タグ 更新履歴
    """
    repository_tag = models.ForeignKey(RepositoryTag, on_delete=models.CASCADE)
    updated = models.DateTimeField(null=False, blank=False)

    class Meta:
        unique_together = ("repository_tag", "updated")

    def __str__(self):
        return f'{self.repository_tag}  {self.updated}'


class Watching(models.Model):
    """
    通知設定
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    repository_tag = models.ForeignKey(RepositoryTag, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("user", "repository_tag")

    def __str__(self):
        return f'{self.user} / {self.repository_tag}'

    def history_count(self):
        hists = WatchingHistory.objects.filter(watching=self)
        return 0 if hists is None else hists.count()


class WatchingHistory(models.Model):
    """
    通知履歴
    """
    watching = models.ForeignKey(Watching, on_delete=models.CASCADE)
    tag_history = \
        models.ForeignKey(RepositoryTagHistory, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.watching.user} / {self.tag_history}'
