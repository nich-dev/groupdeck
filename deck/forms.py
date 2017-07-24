from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from models import (CustomUser, Card, Deck, GameRoom)

class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    class Meta:
        model = CustomUser
        fields = ("username","first_name", "last_name", "email")
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    id = 0

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        
    password=ReadOnlyPasswordHashField(label= ("Password"),
      help_text= ("Raw passwords are not stored, so there is no way to see "
                  "this user's password, but you can <a style='font-weight:900;font-size:1.5em;' href=\"../password/\">change the password "
                  "using this form</a>."))
    
    class Meta:
        model = CustomUser
        fields = ("username","first_name", "last_name", "email", "phone", "password")       
        help_texts = {
            'phone': 'XXX-XXX-XXXX',
        }