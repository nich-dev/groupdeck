# Serializers define the API representation.
import models
from rest_framework import serializers
from datetime import datetime
        
#CARD SERIALIZERS------------------
class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Card
        fields = ('text', 'flavor_text', 'slug', 'pk',
            'user_created', 'date_edited', 'date_created')

class CardSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Card
        fields = ('text', 'flavor_text', 'pk')

class CardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Card
        fields = ('text', 'flavor_text')

#CARDINDECK SERIALIZERS------------
class CardInDeckSerializer(serializers.ModelSerializer):
    card = CardSimpleSerializer(many=False, read_only=True)

    class Meta:
        model = models.CardInDeck
        fields = ('card', 'count')

class CardInDeckSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CardInDeck
        fields = ('card', 'count')

#DECK SERIALIZERS------------------
class DeckSerializer(serializers.ModelSerializer):
    card_count = serializers.SerializerMethodField()
    cards = CardInDeckSerializer(many=True, read_only=True)
    cards_in_deck = CardSimpleSerializer(many=True, read_only=True)
    cards_in_discard = CardSimpleSerializer(many=True, read_only=True)
    card_displayed = CardSimpleSerializer(many=False, read_only=True)

    class Meta:
        model = models.Deck
        fields = ('name', 'slug', 'pk', 'cards_in_deck', 'card_count',
                'cards', 'cards_in_discard', 'card_displayed',
                'in_play', 'date_edited', 'date_created', 'user_created')

    def get_card_count(self, obj):
        return obj.get_count()

class DeckSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Deck
        fields = ('name', 'slug', 'cards', 'cards_in_deck', 
                'cards_in_discard', 'card_displayed',
                'in_play', 'user_created')

class DeckInPlaySerializer(serializers.ModelSerializer):
    cards_in_deck = CardSimpleSerializer(many=True, read_only=True)
    cards_in_discard = CardSimpleSerializer(many=True, read_only=True)
    card_displayed = CardSimpleSerializer(many=False, read_only=True)

    class Meta:
        model = models.Deck
        fields = ('name', 'slug', 'cards_in_deck', 
                'cards_in_discard', 'card_displayed',
                'in_play', 'user_created')

class AddCardToDeckSerializer(serializers.Serializer):
    card = CardSimpleSerializer(many=False, read_only=False)
    count = serializers.IntegerField()

class ChangeCardCountSerializer(serializers.Serializer):
    card = serializers.IntegerField()
    count = serializers.IntegerField()

class CreateCardForDeckSerializer(serializers.Serializer):
    card = CardSimpleSerializer(many=False, read_only=False)
    count = serializers.IntegerField()

class DeleteCardsInDeckSerializer(serializers.Serializer):
    texts = serializers.ListField(
        child=serializers.CharField()
    )
    cards = serializers.ListField(
        child=serializers.IntegerField()
    )

#GAME ROOM SERIALIZERS-------------
class GameRoomSerializer(serializers.ModelSerializer):
    deck = DeckSerializer(many=False, read_only=True)

    class Meta:
        model = models.GameRoom
        fields = ('name', 'slug', 'pk',
                'user_created', 'players', 'deck',
                'open_draw', 'date_edited', 'date_created')

class GameRoomSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GameRoom
        fields = ('name', 'slug',
                'user_created', 'players', 'deck',
                'open_draw')