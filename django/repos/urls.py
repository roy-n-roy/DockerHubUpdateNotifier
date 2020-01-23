from django.urls import path

from . import views

app_name = 'repos'

urlpatterns = [
    path('', views.IndexListView.as_view(), name="index"),
    path('add', views.edit, name="add"),
    path('update/<int:watching_id>', views.edit, name="update"),
    path('delete/<int:watching_id>', views.delete, name="delete"),
    path('last_updated/<str:owner>/<str:name>/<str:tag>',
         views.check, name="check"),
    path('tags/<str:owner>/<str:name>/<int:page>', views.tags, name="tags")
]
