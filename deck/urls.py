from django.conf.urls import include, url
import views, api
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'cards', api.CardViewSet)
router.register(r'decks', api.DeckViewSet)
router.register(r'rooms', api.GameRoomViewSet)

urlpatterns = [
   url(r'^$', views.Landing.as_view(), name="deck-home"),
   url(r'^v2/auth/', include('rest_framework.urls', namespace='rest_framework')),
   url(r'^v2/', include(router.urls)),  
   url(r'^room/(?P<slug>.+)/(?P<key>.+)/', views.Room.as_view(), name="game-room-key"), 
   url(r'^room/(?P<slug>.+)/', views.Room.as_view(), name="game-room-slug"), 
   url(r'^room/', views.Room.as_view(), name="game-room"),  
]