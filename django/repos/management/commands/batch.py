import traceback

import pytz
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.timezone import activate as tz_activate
from django.utils.timezone import deactivate as tz_deactivate
from django.utils.translation import activate as lang_activate
from django.utils.translation import get_language

from account.models import User, WebhookType

from ...apps import ReposConfig as App
from ...models import (RepositoryTag, RepositoryTagHistory, Watching,
                       WatchingHistory)

RESULT_LOG = '{type} notification was {result}. "{repo}", last_updated: {date}'

SYS_LANGUAGE_CODE = get_language()


class Command(BaseCommand):
    help = 'Update repositories from Docker Hub and notify users.'
    output_transaction = True

    def handle(self, *args, **options):
        self.stdout.write('Start Bach Application.')
        for tag in RepositoryTag.objects.all():
            try:
                last_updated = App.check_repository(
                    tag.repository.owner, tag.repository.name, tag.name
                )
                if last_updated is None:
                    self.stdout.write(self.style.WARNING(
                        f'Cannot get update for tag "{tag}".'
                    ))
                elif tag.last_updated == last_updated:
                    self.stdout.write(f'No update on "{tag}".')
                else:
                    tag.last_updated = last_updated
                    tag.save()

                    hist, _ = RepositoryTagHistory.objects.get_or_create(
                        repository_tag=tag, updated=last_updated)

                    for wch in Watching.objects.filter(
                            repository_tag=tag).all():
                        WatchingHistory(watching=wch, tag_history=hist).save()
                        send_notify(self, wch.user, tag)
            except Exception:
                self.stdout.write(self.style.ERROR(traceback.format_exc()))

        self.stdout.write('Finished Bach Application.')


def send_notify(command: Command, user: User, repo_tag: RepositoryTag):
    """
    ユーザーに通知を送信する
    """
    if not user.is_active:
        return

    context = {
        "repo": str(repo_tag),
        "last_updated": repo_tag.last_updated,
        "url": repo_tag.get_url(),
    }
    webhook_type = user.get_webhook_type()
    message = None
    if webhook_type == WebhookType.SLACK:
        try:
            lang_activate(str(user.language_code))
            tz_activate(pytz.timezone(user.timezone))
            message = render_to_string(
                'messages/update_notify_slack.txt', context).encode('UTF-8')
        finally:
            lang_activate(SYS_LANGUAGE_CODE)
            tz_deactivate()
    elif webhook_type == WebhookType.IFTTT:
        try:
            lang_activate(str(user.language_code))
            tz_activate(pytz.timezone(user.timezone))
            message = render_to_string(
                'messages/update_notify_slack.txt', context).encode('UTF-8')
        finally:
            lang_activate(SYS_LANGUAGE_CODE)
            tz_deactivate()
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
                    f' "{repo_tag}", last_updated: {repo_tag.last_updated}'
                ))
            else:
                command.stdout.write(command.style.ERROR(
                    f'Webhook notification was failed.'
                    f' "{repo_tag}", last_updated: {repo_tag.last_updated}\n'
                    f'message: {message}'
                ))

    if user.is_notify_to_email:
        result = False
        try:
            lang_activate(str(user.language_code))
            tz_activate(pytz.timezone(user.timezone))
            result = user.email_user(
                subject=render_to_string(
                    'messages/update_notify_subject.txt', context),
                message=render_to_string(
                    'messages/update_notify_email.html', context)
            )
        except Exception:
            command.stdout.write(command.style.ERROR(traceback.format_exc()))
        finally:
            lang_activate(SYS_LANGUAGE_CODE)
            tz_deactivate()
            if result:
                command.stdout.write(command.style.SUCCESS(
                    f'E-mail notification was successfully.'
                    f' "{repo_tag}", last_updated: {repo_tag.last_updated}'
                ))
            else:
                command.stdout.write(command.style.ERROR(
                    f'E-mail notification was failed.'
                    f' "{repo_tag}", last_updated: {repo_tag.last_updated}\n'
                    f'message: {message}'
                ))
