from django.core.management.base import BaseCommand, CommandError

from ...models import Repository, Watching
from ...apps import ReposConfig as App


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    output_transaction = True

    def handle(self, *args, **options):
        for repo in Repository.objects.all():
            last_updated = App.check_repository(
                repo.owner, repo.name, repo.tag
            )

            if last_updated is None:
                raise CommandError('Repository "%s" does not exist' % repo)
            elif repo.last_updated != last_updated:
                repo.last_updated = last_updated
                for wch in Watching.objects.filter(repository=repo).all():
                    pass
                    # wch.user.notify()
                repo.save()
                self.stdout.write(
                    self.style.NOTICE(last_updated + ' : ' + repo.last_updated)
                )
                self.stdout.write(
                    self.style.SUCCESS('Successfully notify "%s"' % repo)
                )
            else:
                self.stdout.write(
                    self.style.NOTICE('No update on "%s".' % repo)
                )
