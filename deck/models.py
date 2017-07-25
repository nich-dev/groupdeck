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

colors = (
    ('blue', 'Blue (Default)'), ('red', 'Red'), ('pink', 'Pink'),
    ('purple', 'Purple'), ('deep-purple', 'Deep Purple'),
    ('indigo', 'Indigo'), ('light-blue', 'Light Blue'),
    ('cyan', 'Cyan'), ('teal', 'Teal'), ('green', 'Green'),
    ('light-green', 'Light Green'), ('lime', 'Lime'),
    ('orange', 'Orange'), ('deep-orange', 'Deep Orange'),
    ('brown', 'Brown'), ('blue-grey', 'Blue-Grey'),
)
MAX_ALLOWED_CARDS = 500
MAX_ALLOWED_DECKS = 5
MAX_ALLOWED_ROOMS = 1

# Create your models here.
class Card(models.Model):
    text = models.CharField(max_length=255)
    in_deck = models.BooleanField(default=False) # mark as true to not see these in general uses
    
    date_edited = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    slug = models.SlugField(unique=True,max_length=50,blank=True,null=True)
    
    def __unicode__(self):
        return '%s' % (self.text[:50])
    
    def save( self, *args, **kw ):
        if not self.pk:
            self.slug = slugify(self.text)[:50]
            for x in itertools.count(1):
                if not Card.objects.filter(slug=self.slug).exists():
                    break
    
                # Truncate the original slug dynamically. Minus 1 for the hyphen.
                self.slug = "%s-%d" % (slugify(self.text)[:50 - len(str(x)) - 1], x)
        super( Card, self ).save( *args, **kw )

class Deck(models.Model):
    name = models.CharField(max_length=255)
    cards = models.ManyToManyField(Card, #make sure to copy these from the card obj in case of further editing
                                    help_text=_('Cards in the deck'), 
                                    related_name="card_set",blank=True)
    cards_in_discard = models.ManyToManyField(Card, 
                                    help_text=_('Cards in the discard pile'), 
                                    related_name="discard_set",blank=True)
    card_displayed = models.ForeignKey(Card, blank=True, null=True)
    in_play = models.BooleanField(default=False)
    
    date_edited = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user_created = models.ForeignKey('CustomUser', blank=True, null=True)
    
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
        if self.pk and self.cards.count() > MAX_ALLOWED_CARDS:
            for c in self.cards.all()[MAX_ALLOWED_CARDS:]:
                self.cards.remove(c)
        super( Deck, self ).save( *args, **kw )

    def add_card(self, text, count=1):
        if self.cards.count()+count > MAX_ALLOWED_CARDS:
            count = self.cards.count() - MAX_ALLOWED_CARDS
        if count > 0:
            for x in range(count):
                new_card = Card(text = text, in_deck = True)
                new_card.save()
                self.cards.add(new_card)
        return self.cards

    def remove_card(self, card):
        self.cards.remove(card)
        return self.cards

    def remove_card_by_pk(self, pk):
        self.cards.remove(Card.objects.get(pk=pk))
        return self.cards

    def remove_cards(self, text):
        for c in self.cards.filter(text=text):
            self.cards.remove(c)
        return self.cards

    def get_card_count(self, text):
        return self.cards.filter(text=text).count()

    def draw_card(self):
        if self.card_displayed:
            self.cards_in_discard.add(self.card_displayed)
            self.card_displayed = None
        drawn_card = self.choose_random_card()
        if drawn_card:
            self.cards.remove(drawn_card)
            self.card_displayed = drawn_card
            self.save()
            return self.card_displayed
        else: return None

    def choose_random_card(self):
        if self.cards.count():
            return random.choice(self.cards.all())
        else: return None

    def reset_deck(self):
        if self.card_displayed:
            self.cards.add(self.card_displayed)
            self.card_displayed = None
        for c in self.cards_in_discard.all():
            self.cards.add(c)
        self.cards_in_discard.clear()
        self.save()
        return self

#TODO: move to external app
class CustomUserManager(BaseUserManager):

    def _create_user(self, username, password,
                     is_staff, is_superuser, **extra_fields):
        """s
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        return self._create_user(username, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, password, True, True,
                                 **extra_fields)
        
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    username = models.CharField(_('username'), max_length=100, unique=True)
    email = models.EmailField(_('email address'), max_length=254, blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    phone = models.CharField(_('Phone Number'), max_length=12, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    theme = models.CharField(max_length=50, 
                                    help_text=_('The color of the website for this user'),
                                    choices=colors, default="blue")
    decks = models.ManyToManyField(Deck, 
                                    help_text=_('Decks ths user has created'), 
                                    blank=True)
    
    objects = CustomUserManager()


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering= ['username']
    
    def get_absolute_url(self):
        return "/accounts/edit/"

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])
        
    def save( self, *args, **kw ):
        if self.pk and self.decks.count() > MAX_ALLOWED_DECKS:
            for d in self.decks.all()[MAX_ALLOWED_DECKS:]:
                self.cards.remove(d)
        super( CustomUser, self ).save( *args, **kw )

class GameRoom(models.Model):
    name = models.CharField(max_length=255)
    players = models.ManyToManyField(CustomUser,#users that are playing, passed the secret password
                                    help_text=_('Users allowed in game room'), #make sure to add owner
                                    related_name="player_set",blank=True)
    deck = models.ForeignKey(Deck, related_name="deck_played",blank=True,null=True)#temp deck being played
    deck_parent = models.ForeignKey(Deck, related_name="original_deck")#keep track of the deck
    open_draw = models.BooleanField(default=True,
                                    help_text=_('Allow anyone to draw a card'))
    secret = models.CharField(max_length=50,blank=True,null=True,
                                    help_text=_('Secret key to let someone in the room'))
    allow_guests = models.BooleanField(default=True,
                                    help_text=_('Allow anyone to play with the secret key without signing in'))
    finished = models.BooleanField(default=False,
                                    help_text=_('Mark for destruction'))

    date_edited = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user_created = models.ForeignKey(CustomUser)
    
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
        #create a deep copy so furhter changes wont affect the temp deck
        temp_deck = Deck(name = self.deck_parent.name, in_play=True,
            user_created = self.user_created)
        temp_deck.save()
        temp_deck.cards.clear()
        for c in self.deck_parent.cards.all():
            new_card = Card(text=c.text, in_deck=True)
            new_card.save()
            temp_deck.cards.add(new_card)
        self.stop_play()
        self.deck = temp_deck
        self.save()
        return self.deck

    def stop_play(self):#destroy the deck
        if self.deck:
            old_deck_id = self.deck.pk
            self.deck = None
            self.save()
            Deck.objects.get(pk = old_deck_id).delete()
        return self

    def reset_deck(self):
        self.deck.reset_deck()
        return self

    def close_room(self):
        self.stop_play()
        self.delete()
        return 0

#signals for object manipulation here
@receiver(post_save, sender = GameRoom)
def add_owner(instance, created, **kwargs):
    if created:
        instance.players.add(CustomUser.objects.get(pk = instance.user_created.pk))