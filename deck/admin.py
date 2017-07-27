# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
import models

@admin.register(models.Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('text', 'date_created', 'in_deck')
    search_fields = ('text',)
    list_filter = ('in_deck', 'user_created')

@admin.register(models.CardInDeck)
class CardInDeckAdmin(admin.ModelAdmin):
    list_display = ('card', 'count')
    search_fields = ('card',)

@admin.register(models.Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_created')
    search_fields = ('name',)

@admin.register(models.GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_created')
    search_fields = ('name',)