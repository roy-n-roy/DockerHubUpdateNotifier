from django.contrib.auth.forms import (AuthenticationForm, UserChangeForm,
                                       UserCreationForm)
from .models import User


class UserAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


class UsreCreateForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2",)


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
