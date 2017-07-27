# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import (TemplateView, FormView, RedirectView,
                                  UpdateView, CreateView)
from django.http import HttpResponseServerError
import models, forms

def get_theme(request):
    if not request.user.is_anonymous():
        return request.user.theme
    else:
        return "blue"

# Create your views here.
class Landing(TemplateView):
    def get_template_names(self):
        if self.request.is_ajax():
            return ['base.html']
        return ['container/base.html']

    def get_context_data(self, **kwargs):
        context = super(Landing, self).get_context_data(**kwargs)
        context['theme'] = get_theme(self.request)
        context['form'] = AuthenticationForm
        context['joinform'] = forms.JoinRoomForm(request=self.request)
        context['title'] = 'Deck'
        return context

class Room(TemplateView):
    def get_template_names(self):
        if self.request.is_ajax():
            return ['room.html']
        return ['container/room.html']

    def post(self, request, *args, **kwargs):
        print request.POST
        try:
            slug = self.kwargs['slug']
        except Exception, e:
            try:
                if request.POST['choose_previous']:
                    room = models.GameRoom.objects.get(pk = request.POST['choose_previous'])
                else:
                    room = models.GameRoom.objects.get(name = request.POST['name'])
                if request.POST['password'] and room.secret:
                    return redirect('/deck/room/'+room.slug+'/'+request.POST['password']+'/')
                return redirect('/deck/room/'+room.slug+'/')
            except Exception, e:
                return redirect('/deck/')
        return super(Room, self).post(*args, **kwargs)

    def get(self, *args, **kwargs):
        if not self.get_object():
            return redirect('/deck/')
        return super(Room, self).get(*args, **kwargs)

    def get_object(self):
        try:
            return models.GameRoom.objects.get(slug = self.kwargs['slug'])
        except Exception, e:
            return None

    def check_key(self):
        try:
            return self.get_object().secret and self.kwargs['key'] == self.get_object().secret
        except:
            return False

    def is_player(self):
        obj = self.get_object()
        if self.request.user.is_anonymous():
            return self.check_key() and obj.allow_guests
        if self.check_key():
            obj.players.add(self.request.user)
        return self.request.user == obj.user_created or self.request.user in self.get_object().players.all()

    def can_draw(self):
        obj = self.get_object()
        return obj.user_created == self.request.user or (obj.open_draw and self.is_player())

    def get_context_data(self, **kwargs):
        context = super(Room, self).get_context_data(**kwargs)
        context['theme'] = get_theme(self.request)
        if not self.is_player():
            return context
        context['obj'] = self.get_object()
        context['can_draw'] = self.can_draw()
        context['title'] = 'Deck'
        return context