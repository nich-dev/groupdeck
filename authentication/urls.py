from django.conf.urls import url
import views

urlpatterns = [
   url(r'^login/$', views.LoginView.as_view()),
   url(r'^logout/$', views.LogoutView.as_view()),
   url(r'^edit/password/$', views.change_password, name='accounts-password'),
   url(r'^edit/$', views.UserUpdate.as_view(), name="accounts-edit")
]
