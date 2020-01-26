from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import DateTimeField, ChoiceField

User = get_user_model()

language_code_choice = ChoiceField(
    choices=(('en', 'English'), ('ja', '日本語')),
    label=User._meta.get_field('language_code').verbose_name,
)


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        if User.USERNAME_FIELD == 'email':
            fields = ('email', 'language_code')
        else:
            fields = ('username', 'email', 'language_code')

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    language_code = language_code_choice


class UserUpdateFrom(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        if User.USERNAME_FIELD == 'email':
            fields = (
                'language_code',
                'is_notify_to_email',
                'email',
                'webhook_url',
                'date_joined',
            )
        else:
            fields = (
                'language_code',
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
    language_code = language_code_choice
