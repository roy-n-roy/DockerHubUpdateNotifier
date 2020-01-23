from django.contrib.auth import get_user_model
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from .forms import UserCreateForm, UserUpdateFrom

User = get_user_model()


class SignUpView(generic.CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class ProfileView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateFrom
    template_name = 'registration/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user


class DeleteView(LoginRequiredMixin, generic.View):

    def get(self, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        user.is_active = False
        user.save()
        auth_logout(self.request)
        return render(self.request, 'registration/delete_complete.html')
