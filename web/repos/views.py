from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView

from .forms import WatchingForm
from .models import Repository, Watching


@login_required
def index(request):
    repos = Repository.objects.select_related() \
            .filter(watching__user=request.user).all()
    return render(request, "repos/index.html", {'repositories': repos})


@login_required
class WatchingCreateView(CreateView):
    model = Watching
    form_class = WatchingForm
    template_name = "create_form.html"
    success_url = "/"


@login_required
class WatchingUpdateView(UpdateView):
    model = Watching
    form_class = WatchingForm
    template_name = "form.html"
    success_url = "/"

