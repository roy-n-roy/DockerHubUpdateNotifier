from django.contrib import admin

from .models import Repository, Watching

# Register your models here.


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'last_updated')
    fields = ['owner', 'name', 'tag', 'last_updated']


@admin.register(Watching)
class WatchingAdmin(admin.ModelAdmin):
    list_display = ('user', 'repository')
    list_display_links = ('repository',)
