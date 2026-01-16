from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('operator-home/', views.operator_home, name='operator_home'),
]