from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path(r'^create', views.WatchingCreateView.as_view()),
    path(r'^update', views.WatchingUpdateView.as_view())
]
