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
    path('booking-success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('process-payment/<int:booking_id>/', views.process_payment, name='process_payment'),
    path('submit-review/<int:booking_id>/', views.submit_review, name='submit_review'),
    path('profile/', views.profile_view, name='traveller_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('chatbot-api/', views.chatbot_api, name='chatbot_api'),
]