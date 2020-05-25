from django.contrib import admin

from .models import User


@admin.register(User)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('is_active', '__str__', 'last_login')
    list_display_links = ('__str__',)
