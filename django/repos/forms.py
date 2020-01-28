from django.forms import ModelForm

from .models import Watching


class WatchingForm(ModelForm):
    class Meta:
        model = Watching
        fields = ("repository_tag", )
