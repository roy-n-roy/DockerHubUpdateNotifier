from django.contrib import admin

from .models import (Repository, RepositoryTag, RepositoryTagHistory, Watching,
                     WatichingHistory)

# Register your models here.


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    fields = ['owner', 'name']


@admin.register(RepositoryTag)
class RepositoryTagAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'last_updated')
    fields = ['repository', 'name', 'last_updated']


@admin.register(Watching)
class WatchingAdmin(admin.ModelAdmin):
    list_display = ('user', 'repository_tag')
    list_display_links = ('repository_tag',)


@admin.register(RepositoryTagHistory)
class RepositoryTagHistoryAdmin(admin.ModelAdmin):
    list_display = ('repository_tag', 'updated')
    list_display_links = ('repository_tag',)


@admin.register(WatichingHistory)
class WatchingHistoryAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    list_display_links = ('__str__',)
