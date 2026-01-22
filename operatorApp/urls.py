from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('operator-home/', views.operator_home, name='operator_home'),
    path('operator-home/tour-regn-view/', views.tour_regn_view, name='tour_regn_view'),
    path('operator-home/tour-regn-insert/', views.tour_regn_insert, name='tour_regn_insert'),
    path('filllocations/', views.filllocations, name='filllocations'),
]