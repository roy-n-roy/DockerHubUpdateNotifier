from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import DateTimeField

User = get_user_model()


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        if User.USERNAME_FIELD == 'email':
            fields = ('email',)
        else:
            fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserUpdateFrom(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        if User.USERNAME_FIELD == 'email':
            fields = (
                'is_notify_to_email',
                'email',
                'webhook_url',
                'date_joined',
            )
        else:
            fields = (
                'username',
                'is_notify_to_email',
                'email',
                'webhook_url',
                'date_joined',
            )

    date_joined = DateTimeField(
        label=User._meta.get_field('date_joined').verbose_name,
        disabled=True,
    )
