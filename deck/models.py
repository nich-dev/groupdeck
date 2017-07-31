# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin, BaseUserManager) 
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.dispatch import receiver
from datetime import timedelta, datetime
import random, itertools
from django.db.models.signals import pre_delete, post_save
from django.db.models import signals
from django.conf import settings

colors = (
    ('blue', 'Blue (Default)'), ('red', 'Red'), ('pink', 'Pink'),
    ('purple', 'Purple'), ('deep-purple', 'Deep Purple'),
    ('indigo', 'Indigo'), ('light-blue', 'Light Blue'),
    ('cyan', 'Cyan'), ('teal', 'Teal'), ('green', 'Green'),
    ('light-green', 'Light Green'), ('lime', 'Lime'),
    ('orange', 'Orange'), ('deep-orange', 'Deep Orange'),
    ('brown', 'Brown'), ('blue-grey', 'Blue-Grey'),
)

DEF_MAX_ALLOWED_CARDS = 500
DEF_MAX_ALLOWED_DECKS = 5
DEF_MAX_ALLOWED_ROOMS = 2
def get_max_count():
    try:
        if settings.MAX_ALLOWED_CARDS:
            return settings.MAX_ALLOWED_CARDS
        else: return DEF_MAX_ALLOWED_CARDS
    except:
        return DEF_MAX_ALLOWED_CARDS
def get_max_decks():
    try:
        if settings.MAX_ALLOWED_DECKS:
            return settings.MAX_ALLOWED_DECKS
        else: return DEF_MAX_ALLOWED_DECKS
    except:
        return DEF_MAX_ALLOWED_DECKS
def get_max_rooms():
    try:
        if settings.MAX_ALLOWED_ROOMS:
            return settings.MAX_ALLOWED_ROOMS
        else: return DEF_MAX_ALLOWED_ROOMS
    except:
        return DEF_MAX_ALLOWED_ROOMS
# Create your models here.
class Card(models.Model):
    text = models.CharField(max_length=255)# action text
    flavor_text = models.CharField(max_length=255, blank=True, null=True)#extra text not for an action
    in_deck = models.BooleanField(default=False) # mark as true to not see these in general uses
    
    date_edited = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user_created = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    
    slug = models.SlugField(unique=True,max_length=50,blank=True,null=True)
    
    def __unicode__(self):
        return '%s' % (self.text[:50])
    
    def save( self, *args, **kw ):
        if not self.pk and not self.in_deck:
            self.slug = slugify(self.text)[:50]
            for x in itertools.count(1):
                if not Card.objects.filter(slug=self.slug).exists():
                    break
    
                # Truncate the original slug dynamically. Minus 1 for the hyphen.
                self.slug = "%s-%d" % (slugify(self.text)[:50 - len(str(x)) - 1], x)
        super( Card, self ).save( *args, **kw )

class CardInDeck(models.Model):
    card = models.ForeignKey(Card, blank=True, null=True)
    count = models.IntegerField(default=1)

    def save( self, *args, **kw ):
        if self.count > 100:
            self.count = 100
        super( CardInDeck, self ).save( *args, **kw )

    def __unicode__(self):
        return '%s (%s)' % (self.card.text[:50], str(self.count))
    

class Deck(models.Model):
    name = models.CharField(max_length=255)
    cards = models.ManyToManyField(CardInDeck, #make sure to copy these from the card obj in case of further editing
                                    help_text=_('Cards in the deck (Master list)'), 
                                    blank=True)
    cards_in_deck = models.ManyToManyField(Card, 
                                    help_text=_('Cards in the deck'), 
                                    related_name="play_set",blank=True)
    cards_in_discard = models.ManyToManyField(Card, 
                                    help_text=_('Cards in the discard pile'), 
                                    related_name="discard_set",blank=True)
    card_displayed = models.ForeignKey(Card, blank=True, null=True)
    in_play = models.BooleanField(default=False)
    
    date_edited = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user_created = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    slug = models.SlugField(unique=True,max_length=50,blank=True,null=True)
    
    def __unicode__(self):
        return '%s' % (self.name)
    
    def save( self, *args, **kw ):
        if not self.pk:
            self.slug = slugify(self.name)[:50]
            for x in itertools.count(1):
                if not Deck.objects.filter(slug=self.slug).exists():
                    break
    
                # Truncate the original slug dynamically. Minus 1 for the hyphen.
                self.slug = "%s-%d" % (slugify(self.name)[:50 - len(str(x)) - 1], x)
        if self.pk and self.get_count() > get_max_count():
            return
        super( Deck, self ).save( *args, **kw )

    def get_count(self):
        return self.cards.all().aggregate(models.Sum('count'))['count__sum']

    def limit_count(self, count):
        total_count = self.get_count()
        if total_count+count > get_max_count():
            count = get_max_count() - total_count
        return count

    def add_card(self, card, count=1, with_create=False):
        count = self.limit_count(count)
        if count > 0:
            if with_create:
                card.save()
            c = CardInDeck(card=card, count=count)
            c.save()
            cards.add(c)
        return self.cards

    def remove_card(self, card):
        self.cards.filter(card=card).delete()
        return self.cards

    def remove_cards_by_pk(self, pk):
        self.cards.filter(card__pk__in=pk).delete()
        return self.cards

    def remove_cards_by_text(self, text):
        self.cards.filter(card__text__in=text).delete()
        return self.cards

    def get_card_count(self, text):
        return self.cards.filter(text=text).count()

    def change_count(self, card, count=1):
        count = self.limit_count(count)
        if count > 0:
            c = self.cards.filter(card=card)
            c.count = count
            c.save()
        else:
            self.remove_card(card)
        return self.cards

    def draw_card(self):
        if self.card_displayed:
            self.cards_in_discard.add(self.card_displayed)
            self.card_displayed = None
        drawn_card = self.choose_random_card()
        if drawn_card:
            self.card_displayed = drawn_card
            self.save()
            self.cards_in_deck.remove(drawn_card)
            return self.card_displayed
        else: return None

    def choose_random_card(self):
        if self.cards_in_deck.count():
            return random.choice(self.cards_in_deck.all())
        else: return None

    def reset(self):
        if self.card_displayed:
            self.cards_in_deck.add(self.card_displayed)
            self.card_displayed = None
        for c in self.cards_in_discard.all():
            self.cards_in_deck.add(c)
        self.cards_in_discard.clear()
        self.save()
        return self

    def play(self):
        self.cards_in_deck.clear()
        self.cards_in_discard.clear()
        self.card_displayed = None
        self.in_play = True
        self.save()
        for obj in self.cards.all():
            for i in range(obj.count):
                c = Card(text = obj.card.text, flavor_text = obj.card.flavor_text, in_deck = True)
                c.save()
                self.cards_in_deck.add(c)
        return self

    def stop(self):
        self.cards_in_deck.all().delete()
        self.cards_in_discard.all().delete()
        if self.card_displayed:
            self.card_displayed.delete()
        self.in_play = False
        self.save()
        return self

class GameRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    players = models.ManyToManyField(settings.AUTH_USER_MODEL,#users that are playing, passed the secret password
                                    help_text=_('Users allowed in game room'), #make sure to add owner
                                    related_name="player_set",blank=True)
    deck = models.ForeignKey(Deck, blank=True,null=True)#temp deck being played
    open_draw = models.BooleanField(default=True,
                                    help_text=_('Allow anyone to draw a card'))
    secret = models.CharField(max_length=50,blank=True,null=True,
                                    help_text=_('Secret password to let someone in the room'))
    allow_guests = models.BooleanField(default=False,
                                    help_text=_('Allow anyone to play with the secret key without being signed into the website'))
    finished = models.BooleanField(default=False,
                                    help_text=_('Mark for destruction'))

    date_edited = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user_created = models.ForeignKey(settings.AUTH_USER_MODEL)
    
    slug = models.SlugField(unique=True,max_length=50,blank=True,null=True)
    
    def __unicode__(self):
        return '%s' % (self.name[:50])
    
    def save( self, *args, **kw ):
        if not self.pk:
            self.slug = slugify(self.name)[:50]
            for x in itertools.count(1):
                if not GameRoom.objects.filter(slug=self.slug).exists():
                    break
    
                # Truncate the original slug dynamically. Minus 1 for the hyphen.
                self.slug = "%s-%d" % (slugify(self.name)[:50 - len(str(x)) - 1], x)
        elif self.finished:
            self.delete()
            return 0
        super( GameRoom, self ).save( *args, **kw )

    def play_deck(self):
        return self.deck.play()

    def stop_play(self):#destroy the deck
        self.deck.stop()
        return self

    def reset_deck(self):
        return self.deck.reset()

    def close_room(self):
        self.stop_play()
        self.deck = None
        self.save()
        self.delete()
        return 0

#signals for object manipulation here
@receiver(post_save, sender = GameRoom)
def add_owner(instance, created, **kwargs):
    if created:
        instance.players.add(instance.user_created)