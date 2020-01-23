from django.core.management.base import BaseCommand, CommandError

from account.models import User
from ...models import Repository, Watching
from ...apps import ReposConfig as App


import re
import traceback

SLACK_URL_PATTERN = re.compile(
    r'^https://hooks.slack.com/services/[A-Za-z0-9]+/[A-Za-z0-9]+/[A-Za-z0-9]+'
)
SLACK_MESSAGE = '{{"text": "<{url}|{repo}> was updated on {date}."}}'
IFTTT_URL_PATTERN = re.compile(
    r'https://maker.ifttt.com/[\w/:%#$&\?\(\)~\.=\+\-]+'
)
IFTTT_MESSAGE = (
    '{{"value1": "{repo} was updated on {date}.",' +
    ' "value2": "{url}", "value3", "{date}"}}'
)
EMAIL_MESSAGE = (
    'The Docker Hub repository {repo} was updated at {date}.\n' +
    'To view the repository on Docker Hub, go to the following URL:\n\n{url}'
)

RESULT_LOG = '{type} notification was {result}. "{repo}", last_updated: {date}'


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    output_transaction = True

    def handle(self, *args, **options):
        for repo in Repository.objects.all():
            try:
                last_updated = App.check_repository(
                    repo.owner, repo.name, repo.tag
                )

                if last_updated is None:
                    raise CommandError('Repository "%s" does not exist' % repo)
                elif repo.last_updated != last_updated:
                    repo.last_updated = last_updated
                    for wch in Watching.objects.filter(repository=repo).all():
                        send_notify(self, wch.user, repo)
                    repo.save()
                else:
                    self.stdout.write(
                        self.style.NOTICE('No update on "%s".' % repo)
                    )
            except Exception:
                self.stdout.write(self.style.ERROR(traceback.format_exc()))


def send_notify(command: Command, user: User, repo: Repository):
    if not user.is_active:
        return

    webhook_url = user.webhook_url
    if webhook_url is not None:
        if SLACK_URL_PATTERN.match(webhook_url):
            message = SLACK_MESSAGE.format(
                url=get_repo_url(repo), repo=str(repo), date=repo.last_updated)
        elif IFTTT_URL_PATTERN.match(webhook_url):
            message = IFTTT_MESSAGE.format(
                url=get_repo_url(repo), repo=str(repo), date=repo.last_updated)

        result = user.post_webhook(message)
        if result:
            command.stdout.write(command.style.SUCCESS(
                RESULT_LOG.format(
                    type='Webhook', result='successfully',
                    repo=repo, date=repo.last_updated
                )
            ))
        else:
            command.stdout.write(command.style.ERROR(
                RESULT_LOG.format(
                    type='Webhook', result='failed',
                    repo=repo, date=repo.last_updated
                )
            ))

    if user.is_notify_to_email:
        result = user.email_user(
            subject='Docker repository {repo} was Updated.'.format(repo=repo),
            message=EMAIL_MESSAGE.format(
                url=get_repo_url(repo), repo=str(repo), date=repo.last_updated)
        )
        if result:
            command.stdout.write(command.style.SUCCESS(
                RESULT_LOG.format(
                    type='E-mail', result='successfully',
                    repo=repo, date=repo.last_updated
                )
            ))
        else:
            command.stdout.write(command.style.ERROR(
                RESULT_LOG.format(
                    type='E-mail', result='failed',
                    repo=repo, date=repo.last_updated
                )
            ))


def get_repo_url(repo: Repository):
    if str(repo.owner) == 'library':
        return (
            'https://hub.docker.com/_/{name}?tab=tags&name={tag}'
            .format(name=repo.name, tag=repo.tag)
        )
    else:
        return (
            'https://hub.docker.com/r/{owner}/{name}/tags?name={tag}'
            .format(owner=repo.owner, name=repo.name, tag=repo.tag)
        )
