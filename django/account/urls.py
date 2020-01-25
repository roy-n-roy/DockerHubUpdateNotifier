from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('delete_complete', views.DeleteView.as_view(),
         name='delete-complete'),
]
