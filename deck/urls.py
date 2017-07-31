from django.conf.urls import include, url
import views

urlpatterns = [
   url(r'^$', views.Landing.as_view(), name="deck-home"),
   url(r'^room/(?P<slug>.+)/(?P<key>.+)/', views.Room.as_view(), name="game-room-key"), 
   url(r'^room/(?P<slug>.+)/', views.Room.as_view(), name="game-room-slug"), 
   url(r'^room/', views.Room.as_view(), name="game-room"),
   url(r'^create/room/', views.RoomCreate.as_view(), name="create-room"),  
   url(r'^update/room/(?P<slug>.+)/', views.RoomUpdate.as_view(), name="update-room"),  
]