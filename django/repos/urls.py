from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'repos'

urlpatterns = [
    path('', views.IndexListView.as_view(), name="index"),
    path('add', views.edit, name="add"),
    path('update/<int:watching_id>', views.edit, name="update"),
    path('delete/<int:watching_id>', views.delete, name="delete"),
    path('last_updated/<str:owner>/<str:name>/<str:tag>',
         views.check, name="check"),
    path('tags/<str:owner>/<str:name>/<int:page>', views.tags, name="tags"),
    path('js/bookmarklet.js', TemplateView.as_view(
        template_name="repos_js/bookmarklet.js"), name='bookmarklet'),
    path('open_in/<str:owner>/<str:name>', login_required(TemplateView.as_view(
        template_name="repos/openin.html")), name='openin'),
    path('usage', TemplateView.as_view(
        template_name="repos/usage.html"), name='usage'),
    path('history/<int:watching_id>', views.HistoryView.as_view(),
         name='history'),
]
