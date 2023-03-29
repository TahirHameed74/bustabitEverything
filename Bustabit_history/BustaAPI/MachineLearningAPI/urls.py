from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('MachineLearningAPI', views.AnomalyView)
urlpatterns = [
    #path('api/', include(router.urls)),
    path('anomalies/', views.timeseriesmodel),
 
] 