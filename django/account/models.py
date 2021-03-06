import re
from enum import Enum, auto, unique

import requests
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        UserManager)
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class UserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_('email address'), unique=True)
    webhook_url = models.URLField(
        _('Webhook URL'), max_length=500, blank=True, null=True, help_text=_(
            'If you would like to be notified by the chat tool, '
            'please obtain and enter your Webhook URL. '
            'Supported for Incoming Webhook URL of Slack and IFTTT.'
        ),
    )

    language_code = models.CharField(
        _('Language'),
        max_length=3,
        default='en',
        help_text=_('Language used to display.')
        )

    is_notify_to_email = models.BooleanField(
        _('is notity to E-mail'), default=True,
        help_text=_(
            'If enabled, it will notify your email address of'
            ' updates to the Docker repository.'
        ),
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        ),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    timezone = models.CharField(
        _('timezone'),
        max_length=50,
        default=timezone.get_default_timezone_name()
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        return send_mail(
            subject, message, from_email, [self.email], **kwargs) > 0

    def post_webhook(self, message: dict):
        """Post Webhook to user defined URL."""
        result = requests.post(url=str(self.webhook_url), data=message)
        result.raise_for_status()
        return result.status_code == requests.codes.ok

    def get_webhook_type(self):
        if self.webhook_url is None:
            return WebhookType.NONE
        elif _SLACK_URL_PATTERN.match(self.webhook_url):
            return WebhookType.SLACK
        elif _IFTTT_URL_PATTERN.match(self.webhook_url):
            return WebhookType.IFTTT
        else:
            return WebhookType.OTHER


@unique
class WebhookType(Enum):
    """User's Webhook site type. """
    SLACK = auto()
    IFTTT = auto()
    UNKNOWN = auto()
    NONE = auto()


_SLACK_URL_PATTERN = re.compile(
    r'^https://hooks.slack.com/services/[A-Za-z0-9]+/[A-Za-z0-9]+/[A-Za-z0-9]+'
)
_IFTTT_URL_PATTERN = re.compile(
    r'https://maker.ifttt.com/[\w/:%#$&\?\(\)~\.=\+\-]+'
)
