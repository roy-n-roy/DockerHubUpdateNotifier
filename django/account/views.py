from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic

from .forms import UserCreateForm

User = get_user_model()


class SignUpView(generic.CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class ProfileView(LoginRequiredMixin, generic.View):

    def get(self, *args, **kwargs):
        return render(self.request, 'registration/profile.html')


class UpdateView(LoginRequiredMixin, generic.View):

    def post(self, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        post = self.request.POST
        if 'email' in post and 'webhook_url' in post:
            user.email = post['email']
            user.webhook_url = post['webhook_url']
            try:
                user.save()
            except IntegrityError as e:
                if e.args[0].startswith('UNIQUE'):
                    messages.error('指定されたE-Mailアドレスは別のユーザーに登録されています。')
                else:
                    messages.error('更新に失敗しました。')
            else:
                messages.info(self.request, "更新しました。")
        else:
            messages.error('更新に失敗しました。')

        return redirect('accounts:profile')


class DeleteView(LoginRequiredMixin, generic.View):

    def get(self, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        user.is_active = False
        user.save()
        auth_logout(self.request)
        return render(self.request, 'registration/delete_complete.html')
