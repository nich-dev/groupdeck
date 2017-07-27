from django import forms
from models import (Card, Deck, GameRoom, colors)

class JoinRoomForm(forms.Form):
    name = forms.CharField(required=False, 
            widget=forms.TextInput(attrs={'placeholder': 'ex: Game Room Alpha'})
        )
    password = forms.CharField(required=False, 
            widget=forms.TextInput(attrs={'placeholder': 'ex: secretpassword'})
        )
    choose_previous = forms.ModelChoiceField(
            queryset=GameRoom.objects.all(),
            required=False
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(JoinRoomForm, self).__init__(*args, **kwargs)
        if not self.request.user.is_anonymous():
            self.fields['choose_previous'] = forms.ModelChoiceField(
                queryset=GameRoom.objects.filter(players=self.request.user),
                widget=forms.Select,
                label='Or choose a previously entered room',
                required=False
            )
        else:
            self.fields['choose_previous'] = forms.ModelChoiceField(
                queryset=GameRoom.objects.filter(pk=1),
                widget=forms.Select,
                label='Or choose a previously entered room',
                required=False
            )