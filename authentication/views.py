# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import (FormView, RedirectView, UpdateView)
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.decorators import login_required
from models import CustomUser
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
# Create your views here.

def get_theme(request):
    if not request.user.is_anonymous():
        return request.user.theme
    else:
        return "blue"

#-----User object manipulation--------
class LoginView(FormView):
    """
    Provides the ability to login as a user with a username and password
    """
    success_url = '/deck/'
    form_class = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = "container/login.html"
    context_object_name="form_login"

    def get_template_names(self):
        if self.request.is_ajax(): return ['login.ajax.html']
        else: return ['container/login.html']

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        auth_login(self.request, form.get_user())

        # If the test cookie worked, go ahead and
        # delete it since its no longer needed
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(LoginView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['theme'] = get_theme(self.request)
        context['title'] = 'Accounts'
        return context

    def get_success_url(self):
    	next = self.request.POST.get('next')
    	if next:
    		return next
        return self.success_url

class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """
    url = '/authentication/login/'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)
    
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts-edit')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    if request.is_ajax():
        return render(request, 'forms/change_password.html', {
            'form': form,
            'theme': get_theme(request),
            'title': 'Accounts'
        })
    else:
        return render(request, 'container/change_password.html', {
            'form': form,
             'theme': get_theme(request),
             'title': 'Accounts'
        })

class UserUpdate(UpdateView):
    model = CustomUser
    fields = ['email', 'first_name', 
            'last_name', 'phone',
            'theme']
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserUpdate, self).dispatch(*args, **kwargs)
    
    def get_template_names(self):
        if self.request.is_ajax():
            return ['forms/user.edit.html']
        else:
            return ['container/user.edit.html']
        
    def get_context_data(self, **kwargs):
        context = super(UserUpdate, self).get_context_data(**kwargs)
        context['theme'] = get_theme(self.request)
        context['title'] = 'Accounts'
        return context
        
    def get_object(self, queryset=None):
        return self.request.user