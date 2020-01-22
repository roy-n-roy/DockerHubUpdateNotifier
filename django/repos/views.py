import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import (Http404, HttpResponse, get_object_or_404,
                              redirect, render)
from django.views.decorators.http import require_GET, require_POST

from .apps import ReposConfig as App
from .forms import WatchingForm
from .models import Repository, Watching


@require_GET
@login_required
def index(request):
    subs = Watching.objects.filter(user=request.user) \
           .select_related('repository').all()
    return render(request, "repos/index.html", {'subs': subs})


@require_POST
@login_required
def delete(request, watching_id):
    watching = get_object_or_404(Watching, pk=watching_id)
    watching.delete()
    messages.success(request, '削除完了: ' + str(watching.repository))
    return redirect('repos:index')


@require_POST
@login_required
def edit(request, watching_id=None):
    action = '登録' if watching_id is None else '更新'
    if watching_id is None:
        watching = Watching(user=request.user)
    else:
        watching = get_object_or_404(Watching, pk=watching_id)

    if watching.user.id != request.user.id:
        return HttpResponseForbidden()

    data = request.POST
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
                messages.info(request, str(repo) + 'は登録済みです。')
            else:
                messages.error(request, action + 'に失敗しました。')
        else:
            messages.success(request, action + '完了: ' + str(repo))
    else:
        messages.error(request, action + 'に失敗しました。')

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
