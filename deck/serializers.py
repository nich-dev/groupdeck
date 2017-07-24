# Serializers define the API representation.
import models
from rest_framework import serializers
from datetime import datetime

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'decks', 'theme')
        
class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Card
        fields = ('text', 'slug', 'pk',
                 'date_edited', 'date_created')

class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GameRoom
        fields = ('name', 'slug', 'pk', 
        		'cards', 'cards_in_discard', 'card_displayed',
        		'in_play', 'parent'
                'date_edited', 'date_created')

class GameRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Deck
        fields = ('name', 'slug', 'pk',
        		'owner', 'players', 'deck',
        		'deck_parent', 'open_draw',
                'date_edited', 'date_created')