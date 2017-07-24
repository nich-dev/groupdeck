# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import (TemplateView, FormView, RedirectView,
                                  UpdateView, CreateView)

# Create your views here.
def get_theme(request):
    if not request.user.is_anonymous():
        return request.user.theme
    else:
        return "blue"

class Landing(TemplateView):
    def get_template_names(self):
        if self.request.is_ajax():
            return ['base.html']
        else:
            return ['container/base.html']

    def get_context_data(self, **kwargs):
        context = super(Landing, self).get_context_data(**kwargs)
        context['form'] = AuthenticationForm
        context['theme'] = get_theme(self.request)
        return context