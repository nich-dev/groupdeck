# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import (TemplateView, FormView, RedirectView,
                                  UpdateView, CreateView, DeleteView)
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseServerError
from django.core.exceptions import PermissionDenied
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
        if not self.request.user.is_anonymous():
            context['pagetitle'] = self.request.user.username.title() + "'s Dashboard"
            context['cardform'] = forms.CardForm()
            context['cards'] = models.Card.objects.filter(user_created = self.request.user, in_deck = False).order_by('-date_edited')[:15]
            context['cardsmax'] = models.Card.objects.filter(user_created=self.request.user, in_deck = False).count() > models.get_max_cards()
            context['decks'] = models.Deck.objects.filter(user_created = self.request.user).order_by('-date_edited')
            context['decksmax'] = models.Deck.objects.filter(user_created=self.request.user).count() > models.get_max_decks()
            context['rooms'] = models.GameRoom.objects.filter(user_created = self.request.user).order_by('-date_edited')
            context['roomsmax'] = models.GameRoom.objects.filter(user_created=self.request.user).count() > models.get_max_rooms()
        return context

#--Playing
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
        context['deckrange'] = range(1,13,3)
        context['deckrange2'] = reversed(range(1,13,3))
        context['title'] = 'Deck'
        return context

#--OBJECT MANIPULATION
#----Room Objects
class RoomCreate(CreateView):
    model = models.GameRoom
    form_class = forms.GameRoomForm
    success_url = '/deck/'
    
    def get_template_names(self):
        if self.request.is_ajax():
            return ['forms/room.html']
        else:
            return ['container/form.room.html']
        
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if models.GameRoom.objects.filter(user_created=self.request.user).count() > models.get_max_rooms():
            raise PermissionDenied()
        return super(RoomCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        clean = form.cleaned_data      
        obj = form.save(commit=False)
        obj.user_created = self.request.user
        obj.save()
        return super(RoomCreate, self).form_valid(form)  
        
    def get_context_data(self, **kwargs):
        context = super(RoomCreate, self).get_context_data(**kwargs)
        context['form'].fields['deck'].queryset = models.Deck.objects.filter(user_created=self.request.user, in_play=False)
        context['title'] = 'Deck'
        context['theme'] = get_theme(self.request)
        context['pagetitle'] = 'Create a Game Room'
        return context

class RoomUpdate(UpdateView):
    model = models.GameRoom
    form_class = forms.GameRoomForm
    success_url = '/deck/'
    
    def get_template_names(self):
        if self.request.is_ajax():
            return ['forms/room.html']
        else:
            return ['container/form.room.html']
        
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RoomUpdate, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super(RoomUpdate, self).get_object(*args, **kwargs)
        if obj.user_created != self.request.user:
            raise PermissionDenied() #or Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(RoomUpdate, self).get_context_data(**kwargs)
        context['form'].fields['deck'].queryset = models.Deck.objects.filter(user_created=self.request.user, in_play=False)
        context['title'] = 'Deck'
        context['theme'] = get_theme(self.request)
        context['pagetitle'] = 'Edit '+self.get_object().name
        return context

class RoomDelete(DeleteView):
    model = models.GameRoom
    success_url = '/deck/'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if self.request.user != obj.user_created:
            raise PermissionDenied()
        obj.delete()
        return redirect(self.success_url)

#--OBJECT MANIPULATION
#----Deck Objects
class DeckManage(TemplateView):
    model = models.Deck
    success_url = '/deck/'
    
    def get_template_names(self):
        if self.request.is_ajax():
            return ['deck.html']
        else:
            return ['container/deck.html']
        
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeckManage, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
        except Exception, e:
            return None
        else:
            obj = models.Deck.objects.get(slug = slug)
            if obj.user_created != self.request.user:
                raise PermissionDenied() #or Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(DeckManage, self).get_context_data(**kwargs)
        obj = self.get_object()
        context['obj'] = obj
        context['title'] = 'Deck'
        context['theme'] = get_theme(self.request)
        context['pagetitle'] = 'Manage Deck'
        context['cardform'] = forms.CardDeckForm()
        if obj: context['pagetitle'] = context['pagetitle'] + ": " +str(obj.name)
        return context

class DeckDelete(DeleteView):
    model = models.Deck
    success_url = '/deck/'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if self.request.user != obj.user_created:
            raise PermissionDenied()
        obj.delete()
        return redirect(self.success_url)

#--OBJECT MANIPULATION
#----Card Objects
class CardCreate(CreateView):
    model = models.Card
    form_class = forms.CardForm
    success_url = '/deck/'
    
    def get_template_names(self):
        if self.request.is_ajax():
            return ['forms/card.html']
        else:
            return ['container/form.card.html']
        
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if models.Card.objects.filter(user_created=self.request.user, in_deck=False).count() > models.get_max_cards():
            raise PermissionDenied()
        return super(CardCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        clean = form.cleaned_data      
        obj = form.save(commit=False)
        obj.user_created = self.request.user
        obj.save()
        return super(CardCreate, self).form_valid(form)  
        
    def get_context_data(self, **kwargs):
        context = super(CardCreate, self).get_context_data(**kwargs)
        context['title'] = 'Deck'
        context['theme'] = get_theme(self.request)
        context['pagetitle'] = 'Create a Card'

class CardUpdate(UpdateView):
    model = models.Card
    form_class = forms.CardDetailForm
    success_url = '/deck/'
    
    def get_template_names(self):
        if self.request.is_ajax():
            return ['forms/card.html']
        else:
            return ['container/form.card.html']
        
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CardUpdate, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super(CardUpdate, self).get_object(*args, **kwargs)
        if obj.user_created != self.request.user:
            raise PermissionDenied() #or Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(CardUpdate, self).get_context_data(**kwargs)
        context['title'] = 'Deck'
        context['theme'] = get_theme(self.request)
        context['pagetitle'] = 'Edit Card '+ str(self.get_object().pk)
        return context

class CardDelete(DeleteView):
    model = models.Card
    success_url = '/deck/'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if self.request.user != obj.user_created:
            raise PermissionDenied()
        obj.delete()
        return redirect(self.success_url)
