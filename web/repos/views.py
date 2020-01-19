from django.shortcuts import render
from django.views.generic import CreateView, UpdateView

from .forms import WatchingForm
from .models import Repository, Watching


def index(request):
    repos = Repository.objects.select_related() \
            .filter(watching__user=request.user).all()
    return render(request, "apps/index.html", {'repositories': repos})


class WatchingCreateView(CreateView):
    model = Watching
    form_class = WatchingForm
    template_name = "create_form.html"
    success_url = "/"


class WatchingUpdateView(UpdateView):
    model = Watching
    form_class = WatchingForm
    template_name = "form.html"
    success_url = "/"

