# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin, BaseUserManager) 
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.utils import timezone

# Create your models here.
colors = (
    ('blue', 'Blue (Default)'), ('red', 'Red'), ('pink', 'Pink'),
    ('purple', 'Purple'), ('deep-purple', 'Deep Purple'),
    ('indigo', 'Indigo'), ('light-blue', 'Light Blue'),
    ('cyan', 'Cyan'), ('teal', 'Teal'), ('green', 'Green'),
    ('light-green', 'Light Green'), ('lime', 'Lime'),
    ('orange', 'Orange'), ('deep-orange', 'Deep Orange'),
    ('brown', 'Brown'), ('blue-grey', 'Blue-Grey'),
)

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
        super( CustomUser, self ).save( *args, **kw )