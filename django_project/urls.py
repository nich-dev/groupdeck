"""citi_ics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from calibration import views, views_api
from django.views.generic import RedirectView
from calibration import urls as calibration_urls


router = routers.DefaultRouter()
router.register(r'users', views_api.UserViewSet)
router.register(r'plants', views_api.PlantViewSet)
router.register(r'locations', views_api.LocationViewSet)
router.register(r'manufacturers', views_api.ManufacturerViewSet)
router.register(r'calibfreqs', views_api.CalibrationFrequencyViewSet)
router.register(r'calibs', views_api.CalibrationViewSet)
router.register(r'types', views_api.InstrumentTypeViewSet)
router.register(r'models', views_api.InstrumentModelViewSet)
router.register(r'models2', views_api.InstrumentModelViewSet2, base_name="models_2")
router.register(r'modelsjs', views_api.InstrumentModelViewSetForJS, base_name="models_js")
router.register(r'instruments', views_api.InstrumentViewSet)
router.register(r'calibpoints', views_api.CalibrationPointViewSet)
router.register(r'upcalib', views_api.CalibrationUploadViewSet, base_name="upload_calibration")
router.register(r'tasks', views_api.TaskViewSet)
router.register(r'taskcategories', views_api.TaskCatViewSet)
router.register(r'instrumentedit', views_api.InstrumentEditViewSet, base_name="instrument_edit")
router.register(r'instrumentprint', views_api.InstrumentNiceViewSet, base_name="instrument_print")
#router.register(r'columbiaupload', views_api.ColumbiaUploadViewSet, base_name="columbia")

urlpatterns = [
   url(r'^admin/manager/customuser/(?P<pk>\d+)/change/password/$', RedirectView.as_view(url='/admin/manager/customuser/(?P<pk>\d+)/', permanent=False), name='index'),
   url(r'^admin/', include(admin.site.urls)),
   url(r'^v2/auth/', include('rest_framework.urls', namespace='rest_framework')),
   url(r'^v2/', include(router.urls)),   
   url(r'^rest-auth/', include('rest_auth.urls')),
   url('^searchableselect/', include('searchableselect.urls')),
   url(r'^', include(calibration_urls)),
]
