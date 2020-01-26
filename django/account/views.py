from django.contrib.auth import get_user_model
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (csrf_protect, login_required,
                                       method_decorator,
                                       sensitive_post_parameters,
                                       update_session_auth_hash)
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from .forms import UserCreateForm, UserUpdateFrom

User = get_user_model()


class SignUpView(generic.CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'initial': {'language_code': self.request.LANGUAGE_CODE}
        })
        return kwargs


class ProfileView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateFrom
    template_name = 'registration/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        if isinstance(form, PasswordChangeForm):
            form.save()
            # Updating the password logs out all other sessions for the user
            # except the current one.
            update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["password_change_form"] = PasswordChangeForm(self.request.user)
        return context


class DeleteView(LoginRequiredMixin, generic.View):

    def get(self, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        user.is_active = False
        user.save()
        auth_logout(self.request)
        return render(self.request, 'registration/delete_complete.html')
