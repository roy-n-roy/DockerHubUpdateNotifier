from django import forms
from .models import Watching


class WatchingForm(forms.ModelForm):
    class Meta:
        model = Watching
        fields = ("repository", )
    pass
