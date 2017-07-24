from django.conf.urls import include, url
import views, api
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'cards', api.CardViewSet)
router.register(r'decks', api.DeckViewSet)
router.register(r'rooms', api.GameRoomViewSet)
router.register(r'users', api.UserViewSet)

urlpatterns = [
   url(r'^$', views.Landing.as_view()),
   url(r'^v2/auth/', include('rest_framework.urls', namespace='rest_framework')),
   url(r'^v2/', include(router.urls)),  
]