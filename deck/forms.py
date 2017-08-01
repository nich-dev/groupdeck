from django import forms
from models import (Card, Deck, GameRoom, colors, CardInDeck)
from searchableselect.widgets import SearchableSelect

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

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['text', 'flavor_text']

class CardDetailForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['text', 'flavor_text', 'id']
        widgets = {'id': forms.HiddenInput()}

class CardsInDeckForm(forms.Form):
    card = forms.ModelChoiceField(
            queryset=Card.objects.filter(in_deck=False),
            required=False
        )
    count = forms.IntegerField()

class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['name', 'cards']

class GameRoomForm(forms.ModelForm):
    class Meta:
        model = GameRoom
        fields = ['name', 'deck', 'secret', 'open_draw', 'allow_guests']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(GameRoomForm, self).__init__(*args, **kwargs)

class CardInDeckAdminForm(forms.ModelForm):
    class Meta:
        model = CardInDeck
        exclude = ()
        widgets = {
            'card': SearchableSelect(model='deck.Card', search_field='text', many=False),
        }