from django.conf.urls import include, url
import api
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'cards', api.CardViewSet)
router.register(r'decks', api.DeckViewSet)
router.register(r'rooms', api.GameRoomViewSet)

urlpatterns = [
   url(r'^/', include(router.urls)),
]