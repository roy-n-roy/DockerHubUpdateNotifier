import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import (Http404, HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden)
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import ListView

from .apps import ReposConfig as App
from .forms import WatchingForm
from .models import Repository, Watching
from django.utils.translation import gettext_lazy as _


class IndexListView(LoginRequiredMixin, ListView):
    http_method_names = ['get']
    model = Watching
    context_object_name = 'items'
    template_name = "repos/index.html"
    paginate_by = 10

    def get_queryset(self):
        quieryset = Watching.objects.filter(user=self.request.user)
        req = self.request.GET
        if 'sortby' == req and req['sortby']:
            quieryset = quieryset.order_by(req[''])
        return quieryset


@require_POST
@login_required
def delete(request, watching_id):
    watching = get_object_or_404(Watching, pk=watching_id, user=request.user)
    watching.delete()
    messages.success(
        request, _('Deletion completed.') + str(watching.repository))
    return redirect('repos:index')


@require_POST
@login_required
def edit(request, watching_id=None):
    action = _('Registration') if watching_id is None else _('Update')
    if watching_id is None:
        watching = Watching(user=request.user)
    else:
        watching = get_object_or_404(
            Watching, pk=watching_id, user=request.user)

    if watching.user.id != request.user.id:
        return HttpResponseForbidden()

    data = request.POST
    if 'owner' not in data or 'name' not in data or 'tag' not in data:
        return HttpResponseBadRequest()

    keys = {
        "owner": data['owner'],
        "name": data['name'],
        "tag": data['tag']
    }
    repo = Repository.objects.filter(**keys).first()
    if repo is None:
        repo = Repository(**keys)
        last_updated = App.check_repository(**keys)
        if last_updated is not None:
            repo.last_updated = last_updated
            repo.save()
        else:
            raise Http404()

    form = WatchingForm(data={"repository": repo}, instance=watching)
    if form.is_valid():
        try:
            watching.save()
        except IntegrityError as e:
            if e.args[0].startswith('UNIQUE'):
                messages.info(request, _(str(repo) + ' is a duplicate.'))
            else:
                messages.error(request, _(action + ' failed.'))
        else:
            messages.success(request, _(action + ' completed.') + str(repo))
    else:
        messages.error(request, _(action + ' failed.'))

    return redirect('repos:index')


@require_GET
@login_required
def check(request, owner, name, tag):
    last_update = App.check_repository(owner, name, tag)
    if last_update:
        return HttpResponse(json.dumps({"lastupdated": str(last_update)}))
    else:
        raise Http404


@require_GET
@login_required
def tags(request, owner, name, page):
    tags = App.get_tags(owner, name, page)
    if tags:
        tags['owner'] = owner
        tags['name'] = name
        return HttpResponse(json.dumps(tags))
    else:
        raise Http404
