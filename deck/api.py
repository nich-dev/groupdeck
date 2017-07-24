from rest_framework import viewsets, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import models, serializers 
from datetime import datetime
from braces.views import CsrfExemptMixin
from django.db.models import Q
from json import loads

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSimpleSerializer
    queryset = models.CustomUser.objects.all()
    lookup_field = ('username')
    permissions = (permissions.IsAuthenticated)

class CardViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CardSerializer
    queryset = models.Card.objects.all()
    lookup_field = ('pk')
    permissions = (permissions.IsAuthenticated)
    
    def get_queryset(self):
        since = self.request.query_params.get('since', None)
        queryset = models.Card.objects.all()
        
        if since is not None:
            last_time = datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
            queryset = queryset.filter(date_edited__gte=last_time)
            
        return queryset

class DeckViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.DeckSerializer
    queryset = models.Deck.objects.all()
    lookup_field = ('slug')
    permissions = (permissions.IsAuthenticated)
    
    def get_queryset(self):
        since = self.request.query_params.get('since', None)
        queryset = models.Deck.objects.all()
        
        if since is not None:
            last_time = datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
            queryset = queryset.filter(date_edited__gte=last_time)
            
        return queryset

class GameRoomViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.GameRoomSerializer
    queryset = models.GameRoom.objects.all()
    lookup_field = ('slug')
    permissions = (permissions.IsAuthenticated)
    
    def get_queryset(self):
        since = self.request.query_params.get('since', None)
        queryset = models.GameRoom.objects.all()
        
        if since is not None:
            last_time = datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
            queryset = queryset.filter(date_edited__gte=last_time)
            
        return queryset