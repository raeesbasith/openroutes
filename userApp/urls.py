from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('traveller-home/', views.traveller_home, name='traveller_home'),
]