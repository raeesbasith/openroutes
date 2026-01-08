from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('home/', views.adminHome, name='adminHome'),
    path('distRegn/', views.distRegn, name='distRegn'),
    path('distRegnInsert/', views.distRegnInsert, name='distRegnInsert'),
    path('distView/', views.distView, name='distView'),
    path('distDelete/<int:id>/', views.distDelete, name='distDelete'),
]