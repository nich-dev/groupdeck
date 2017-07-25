# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from forms import (CustomUserChangeForm, CustomUserCreationForm)
from django.utils.translation import ugettext_lazy as _
import models

# Register your models here.
class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field
    fieldsets = (
        (None, {'fields': ('email', 'username','password')}),
        (_('App Settings'), {'fields': ('theme',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'first_name', 'email', 'is_staff')
    search_fields = ('username', 'first_name', 'email')
    ordering = ('username',)

admin.site.register(models.CustomUser, CustomUserAdmin)