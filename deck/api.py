from rest_framework import viewsets, permissions, status
from rest_framework.decorators import detail_route, list_route, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import models, serializers 
from datetime import datetime
from braces.views import CsrfExemptMixin
from django.db.models import Q
from json import loads
import permissions as deckpermissions

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")

class CardViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CardSerializer
    queryset = models.Card.objects.filter(in_deck=False)
    lookup_field = ('pk')
    permission_classes = (permissions.IsAuthenticated,
        deckpermissions.IsOwnerOrReadOnly)
    
    def get_queryset(self):
        since = self.request.query_params.get('since', None)
        search = self.request.query_params.get('search', None)
        own = self.request.query_params.get('own', None)
        queryset = models.Card.objects.filter(in_deck=False)

        if own is not None:
            own = str2bool(own)
            queryset = models.Card.objects.filter(in_deck=False, user_created = self.request.user)
        if since is not None:
            last_time = datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
            queryset = queryset.filter(date_edited__gte=last_time)
        if search is not None:
            #queryset = queryset.filter(text__icontains = search).order_by('text').distinct('text')
            queryset = queryset.filter(text__icontains = search).order_by('text').distinct()
            
        return queryset

    # copies a card, sets the user as the requesting user. Allows for a collection of 'saved' cards
    @detail_route()
    def copy(self, request, pk=None):
        try:
            obj = self.get_object()
            self.check_object_permissions(request, obj)
            c = models.Card(text = obj.text, flavor_text = obj.flavor_text, 
                user_created = request.user)
            c.save()
            serializer = serializers.CardSerializer(c, many=False)
            return Response(serializer.data,
                status=status.HTTP_200_OK)
        except Exception, e:
            print e
            return Response({'status': 'Error copying card'},
                status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        serializer = serializers.CardCreateSerializer(data=request.data)
        if serializer.is_valid():
            card = serializer.save()
            card.user_created = request.user
            card.save()
            return Response(serializers.CardSerializer(card, many=False).data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        obj = self.get_object()
        serializer = serializers.CardCreateSerializer(data=request.data)
        if serializer.is_valid():
            obj.text = serializer.data['text']
            obj.flavor_text = serializer.data['flavor_text']
            obj.save()
            return Response(serializers.CardSerializer(obj, many=False).data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

class DeckViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.DeckSimpleSerializer
    queryset = models.Deck.objects.filter(in_play=False)
    lookup_field = ('slug')
    permission_classes = (permissions.IsAuthenticated,
        deckpermissions.IsOwnerOrReadOnly)
    
    def get_queryset(self):
        since = self.request.query_params.get('since', None)
        search = self.request.query_params.get('search', None)
        in_play = self.request.query_params.get('in_play', None)
        own = str2bool(self.request.query_params.get('own', True))
        queryset = models.Deck.objects.all()
        
        if in_play is not None and self.request.user.is_staff:
            queryset = models.Deck.objects.filter(in_play=in_play)
        if own:
            queryset = queryset.filter(user_created = self.request.user)
        if since is not None:
            last_time = datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
            queryset = queryset.filter(date_edited__gte=last_time)
        if search is not None:
            queryset = queryset.filter(name__icontains = search)
            
        return queryset

    @detail_route()
    def get_random_card(self, request, slug=None):
        try:
            obj = self.get_object()
            self.check_object_permissions(request, obj)
            serializer = serializers.CardSimpleSerializer(obj.choose_random_card, many=False)
            return Response(serializer.data,
                status=status.HTTP_200_OK)
        except Exception, e:
            print e
            return Response({'status': 'Error grabbing card'},
                status=status.HTTP_400_BAD_REQUEST)

    @detail_route()
    def play_view(self, request, slug=None):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        serializer = serializers.DeckInPlaySerializer(obj, many=False)
        return Response(serializer.data,
            status=status.HTTP_200_OK)

    #accepts a POST with a list cards and count fields
    #ex [{"card": {"text":"", "flavor_text":"", "pk":0}, "count": 2} ...]
    #if pk is invalid (-1,0), will preform a create. If you know pk, do not need to transmit text/flavor_text
    @detail_route(methods=['POST'])
    def add_cards(self, request, slug=None):
        obj = self.get_object()
        serializer = serializers.AddCardToDeckSerializer(data=request.data, many=True)
        if serializer.is_valid():
            for d in serializer.data:
                print d
                try: #try to find card and add
                    c = models.Card.objects.get(pk=d['card']['pk'])
                    if c.user_created is not request.user:
                        c = models.Card(text = c.text, flavor_text = c.flavor_text, user_created = request.user)
                        c.save()
                    obj.add_card(c, d['count'])
                except: 
                    c = models.Card(text=d['card']['text'], flavor_text=d['card']['flavor_text'], user_created=request.user)
                    c.save()
                    obj.add_card(c, d['count'], True)
            return Response(serializers.DeckSimpleSerializer(obj, many=False).data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    #accepts a POST with a list cardpks and count fields to update the counts
    #ex [{"card": 1, "count": 2} ...]. If count < 1, card will be deleted
    @detail_route(methods=['POST'])
    def change_count(self, request, slug=None):
        obj = self.get_object()
        serializer = serializers.ChangeCardCountSerializer(data=request.data, many=True)
        if serializer.is_valid():
            for d in serializer.data:
                try: #try to find card and change count
                    c = models.Card.objects.get(pk=d['card'])
                    obj.change_count(c, d['count'])
                except: pass
            return Response(serializers.DeckSimpleSerializer(obj, many=False).data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    #accepts a POST with a list of text/pk to delete, this will delete all cards with this text/pk
    #ex {"texts": ["Example text 1", "Example text 2"], "cards": [1,2,4]}
    @detail_route(methods=['POST'])
    def remove_cards(self, request, slug=None):
        obj = self.get_object()
        serializer = serializers.DeleteCardsInDeckSerializer(data=request.data, many=False)
        if serializer.is_valid():
            try: #try to remove all cards with text
                obj.remove_cards_by_text(serializer.data['texts'])
            except: pass
            try: #try to remove all cards with text
                obj.remove_cards_by_pk(serializer.data['cards'])
            except: pass
            return Response(serializers.DeckSimpleSerializer(obj, many=False).data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        serializer = serializers.DeckCreateSerializer(data=request.data)
        if serializer.is_valid():
            deck = serializer.save()
            deck.user_created = request.user
            deck.save()
            return Response(serializers.DeckSimpleSerializer(deck, many=False).data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, slug=None):
        queryset = self.get_queryset()
        deck = get_object_or_404(queryset, slug=slug)
        serializer = serializers.DeckSerializer(deck)
        return Response(serializer.data)    

class GameRoomViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.GameRoomSimpleSerializer
    queryset = models.GameRoom.objects.all()
    lookup_field = ('slug')
    permission_classes = (deckpermissions.IsPlayer,
        deckpermissions.IsOwnerOrReadOnly)

    def get_queryset(self):
        since = self.request.query_params.get('since', None)
        own = self.request.query_params.get('own', None)
        queryset = models.GameRoom.objects.all()

        if own and not self.request.user.is_anonymous():
            if str2bool(own):
                queryset = queryset.filter(user_created = self.request.user)        
        if since is not None:
            last_time = datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
            queryset = queryset.filter(date_edited__gte=last_time)
            
        return queryset

    #returns the current drawn card
    @detail_route()
    def get_current_card(self, request, slug=None):
        try:
            obj = self.get_object()
            self.check_object_permissions(request, obj)
            serializer = serializers.CardSimpleSerializer(obj.deck.card_displayed, many=False)
            return Response(serializer.data,
                status=status.HTTP_200_OK)
        except Exception, e:
            print e
            return Response({'status': 'Error grabbing card'},
                status=status.HTTP_400_BAD_REQUEST)

    #draws a card if able and returns that card
    @detail_route(permission_classes=[deckpermissions.CanDraw, deckpermissions.IsPlayer])
    def draw_card(self, request, slug=None):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        drawn_card = obj.deck.draw_card()
        if drawn_card:
            serializer = serializers.CardSimpleSerializer(drawn_card, many=False)
            return Response(serializer.data,
                status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Deck is empty'},
                status=status.HTTP_200_OK)

    @detail_route(permission_classes=[deckpermissions.IsPlayer])
    def get_deck(self, request, slug=None):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        serializer = serializers.DeckInPlaySerializer(obj.deck, many=False)
        return Response(serializer.data,
            status=status.HTTP_200_OK)

    @detail_route(permission_classes=[deckpermissions.IsOwner])
    def start_game(self, request, slug=None):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        serializer = serializers.DeckInPlaySerializer(obj.play_deck(), many=False)
        return Response(serializer.data,
            status=status.HTTP_200_OK)

    @detail_route(permission_classes=[deckpermissions.IsOwner])
    def stop_game(self, request, slug=None):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        serializer = serializers.GameRoomSerializer(obj.stop_play(), many=False)
        return Response(serializer.data,
            status=status.HTTP_200_OK)

    @detail_route(permission_classes=[deckpermissions.IsOwner])
    def close_room(self, request, slug=None):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        obj.close_room()
        return Response({'status': 'Room closed'},
            status=status.HTTP_200_OK)

    @detail_route(permission_classes=[deckpermissions.IsOwner])
    def reset_deck(self, request, slug=None):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        serializer = serializers.DeckInPlaySerializer(obj.reset_deck(), many=False)
        return Response(serializer.data,
            status=status.HTTP_200_OK)

    @detail_route(permission_classes=[deckpermissions.IsPlayer])
    def play_view(self, request, slug=None):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        serializer = serializers.DeckInPlaySerializer(obj.deck, many=False)
        return Response(serializer.data,
            status=status.HTTP_200_OK)

    def retrieve(self, request, slug=None):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, slug=slug)
        self.check_object_permissions(request, obj)
        serializer = serializers.GameRoomSerializer(obj)
        return Response(serializer.data)