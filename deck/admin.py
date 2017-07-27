# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
import models
from forms import CardInDeckAdminForm

def add_to_new_deck(modeladmin, request, queryset):
    tempname = "generated deck for " + request.user.username
    d = models.Deck(name = tempname, user_created=request.user)
    d.save()
    for c in queryset:
        cid = models.CardInDeck(card=c, count=1)
        cid.save()
        d.cards.add(cid)
add_to_new_deck.short_description = "Make a new deck with these"

@admin.register(models.Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('text', 'date_created', 'in_deck')
    search_fields = ('text',)
    list_filter = ('in_deck', 'user_created')
    actions = [add_to_new_deck]

@admin.register(models.CardInDeck)
class CardInDeckAdmin(admin.ModelAdmin):
    list_display = ('card', 'count')
    search_fields = ('card',)
    list_filter = ('deck', 'deck__user_created')
    form = CardInDeckAdminForm

@admin.register(models.Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_created')
    search_fields = ('name',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(DeckAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['cards'].queryset = models.CardInDeck.objects.filter(deck__user_created=request.user)
        form.base_fields['cards_in_deck'].queryset = models.Card.objects.filter(deck=obj)
        form.base_fields['cards_in_discard'].queryset = models.Card.objects.filter(deck=obj)
        form.base_fields['card_displayed'].queryset = models.Card.objects.filter(deck=obj)
        return form

@admin.register(models.GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_created')
    search_fields = ('name',)