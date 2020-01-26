import traceback

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.translation import get_language, activate
from account.models import User, WebhookType

from ...apps import ReposConfig as App
from ...models import Repository, Watching

RESULT_LOG = '{type} notification was {result}. "{repo}", last_updated: {date}'

SYS_LANGUAGE_CODE = get_language()


class Command(BaseCommand):
    help = 'Update repositories from Docker Hub and notify users.'
    output_transaction = True

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Start Bach Application.'))
        for repo in Repository.objects.all():
            try:
                last_updated = App.check_repository(
                    repo.owner, repo.name, repo.tag
                )
                if last_updated is None or repo.last_updated != last_updated:
                    repo.last_updated = last_updated
                    for wch in Watching.objects.filter(repository=repo).all():
                        send_notify(self, wch.user, repo)
                    repo.save()
                else:
                    self.stdout.write(f'No update on "{repo}".')
            except Exception:
                self.stdout.write(self.style.ERROR(traceback.format_exc()))
        self.stdout.write(self.style.NOTICE('Finished Bach Application.'))


def send_notify(command: Command, user: User, repo: Repository):
    if not user.is_active:
        return

    context = {
        "repo": str(repo),
        "last_updated": repo.last_updated,
        "url": repo.get_url(),
    }
    webhook_type = user.get_webhook_type()
    message = None
    if webhook_type == WebhookType.SLACK:
        try:
            activate(str(user.language_code))
            message = render_to_string(
                'messages/update_notify_slack.txt', context).encode('UTF-8')
        finally:
            activate(SYS_LANGUAGE_CODE)
    elif webhook_type == WebhookType.IFTTT:
        try:
            activate(str(user.language_code))
            message = render_to_string(
                'messages/update_notify_slack.txt', context).encode('UTF-8')
        finally:
            activate(SYS_LANGUAGE_CODE)
    elif webhook_type == WebhookType.UNKNOWN:
        command.stdout.write(command.style.ERROR(
            f'User {user} has UNKNOWN URL.\n{user.webhook_url}'
        ))

    if webhook_type not in [WebhookType.UNKNOWN, WebhookType.NONE]:
        result = False
        try:
            if message:
                result = user.post_webhook(message)
        except Exception:
            command.stdout.write(command.style.ERROR(traceback.format_exc()))
        finally:
            if result:
                command.stdout.write(command.style.SUCCESS(
                    f'Webhook notification was successfully.'
                    f' "{repo}", last_updated: {repo.last_updated}'
                ))
            else:
                command.stdout.write(command.style.ERROR(
                    f'Webhook notification was failed.'
                    f' "{repo}", last_updated: {repo.last_updated}\n'
                    f'message: {message}'
                ))

    if user.is_notify_to_email:
        result = False
        try:
            activate(str(user.language_code))
            result = user.email_user(
                subject=render_to_string(
                    'messages/update_notify_subject.txt', context),
                message=render_to_string(
                    'messages/update_notify_email.html', context)
            )
        except Exception:
            command.stdout.write(command.style.ERROR(traceback.format_exc()))
        finally:
            activate(SYS_LANGUAGE_CODE)
            if result:
                command.stdout.write(command.style.SUCCESS(
                    f'E-mail notification was successfully.'
                    f' "{repo}", last_updated: {repo.last_updated}'
                ))
            else:
                command.stdout.write(command.style.ERROR(
                    f'E-mail notification was failed.'
                    f' "{repo}", last_updated: {repo.last_updated}\n'
                    f'message: {message}'
                ))
