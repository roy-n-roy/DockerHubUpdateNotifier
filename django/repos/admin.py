from django.contrib import admin

from .models import Repository, RepositoryTag, Watching

# Register your models here.


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'last_updated')
    fields = ['owner', 'name', 'last_updated']


@admin.register(RepositoryTag)
class RepositoryTagAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'last_updated')
    fields = ['repository', 'name', 'last_updated']


@admin.register(Watching)
class WatchingAdmin(admin.ModelAdmin):
    list_display = ('user', 'repository_tag')
    list_display_links = ('repository_tag',)
