import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import (Http404, HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden)
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import ListView

from .apps import ReposConfig as App
from .forms import WatchingForm
from .models import Repository, RepositoryTag, Watching


class IndexListView(LoginRequiredMixin, ListView):
    http_method_names = ['get']
    model = Watching
    context_object_name = 'items'
    template_name = "repos/index.html"
    paginate_by = 0

    def get_queryset(self):
        quieryset = Watching.objects.filter(user=self.request.user)
        return quieryset


@require_POST
@login_required
def delete(request, watching_id):
    watching = get_object_or_404(Watching, pk=watching_id, user=request.user)
    watching.delete()
    messages.success(
        request, _('Deletion completed.') + ' ' + str(watching.repository_tag))
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

    repo_tag = RepositoryTag.objects.filter(
        repository__owner=data['owner'],
        repository__name=data['name'],
        name=data['tag']
    ).first()
    if repo_tag is None:
        repo, createed = Repository.objects.get_or_create(
            owner=data['owner'],
            name=data['name'],
        )
        if createed:
            repo.last_updated = App.check_repository(
                owner=data['owner'],
                name=data['name'],
                tag='')
            if repo.last_updated is not None:
                repo.save()
            else:
                raise Http404()

        repo_tag = RepositoryTag(repository=repo, name=data['tag'])
        repo_tag.last_updated = App.check_repository(
                owner=data['owner'],
                name=data['name'],
                tag=data['tag'])
        if repo_tag.last_updated is not None:
            repo_tag.save()
        else:
            raise Http404()

    form = WatchingForm(data={"repository_tag": repo_tag}, instance=watching)
    if form.is_valid():
        try:
            watching.save()
        except IntegrityError as e:
            if e.args[0].startswith('UNIQUE'):
                messages.info(request, _('%(repo_tag)s is a duplicate.') % {
                    'repo_tag': str(repo_tag)
                })
            else:
                messages.error(
                    request, _('%(action)s failed.') % {'action': action})
        else:
            messages.success(
                request, _('%(action)s completed. %(repo_tag)s') % {
                    'action': action, 'repo_tag': str(repo_tag)
                }
            )
    else:
        messages.error(request, _('%(action)s failed.') % {'action': action})

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
