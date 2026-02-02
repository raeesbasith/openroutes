from django.urls import path
from . import views
from .views import *

urlpatterns = [

    path('traveller-home/', views.traveller_home, name='traveller_home'),
    path('tour-packages/', views.tour_packages_view, name='tour_packages'),
    path('filllocation/', views.filllocation, name='filllocation'),
    path('tour-detail/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    path('booking/<int:tour_id>/', views.booking, name='booking'),
    path('booking-confirm/<int:tour_id>/', views.booking_confirm, name='booking_confirm'),
]