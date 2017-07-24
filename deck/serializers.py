# Serializers define the API representation.
import models
from rest_framework import serializers
from datetime import datetime

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'decks', 'theme')

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ('username', 'first_name')
        
class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Card
        fields = ('text', 'slug', 'pk',
                 'date_edited', 'date_created')

class CardSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Card
        fields = ('text', 'pk')

class DeckSerializer(serializers.ModelSerializer):
    cards = CardSimpleSerializer(many=True, read_only=True)
    cards_in_discard = CardSimpleSerializer(many=True, read_only=True)
    card_displayed = CardSimpleSerializer(many=False, read_only=True)

    class Meta:
        model = models.Deck
        fields = ('name', 'slug', 'pk', 
                'cards', 'cards_in_discard', 'card_displayed',
                'in_play', 'date_edited', 'date_created', 'user_created')

class DeckSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Deck
        fields = ('name', 'slug', 
                'cards', 'cards_in_discard', 'card_displayed',
                'in_play', 'user_created')

class GameRoomSerializer(serializers.ModelSerializer):
    players = UserSimpleSerializer(many=True, read_only=True)
    deck = DeckSerializer(many=False, read_only=True)

    class Meta:
        model = models.GameRoom
        fields = ('name', 'slug', 'pk',
                'user_created', 'players', 'deck',
                'deck_parent', 'open_draw',
                'date_edited', 'date_created')

class GameRoomSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GameRoom
        fields = ('name', 'slug',
                'user_created', 'players', 'deck',
                'deck_parent', 'open_draw')