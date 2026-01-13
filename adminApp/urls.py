from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('home/', views.adminHome, name='adminHome'),
    path('distRegn/', views.distRegn, name='distRegn'),
    path('distRegnInsert/', views.distRegnInsert, name='distRegnInsert'),
    path('distView/', views.distView, name='distView'),
    path('distDelete/<int:id>/', views.distDelete, name='distDelete'),
    path('distEdit/<int:id>/', views.distEdit, name='distEdit'),
    path('locationRegn/', views.locationRegn, name='locationRegn'),
    path('locationInsert/', views.locationInsert, name='locationInsert'),
    path('locationView/', views.locationView, name='locationView'),
    path('locationDelete/<int:id>/', views.locationDelete, name='locationDelete'),
    path('locationEdit/<int:id>/', views.locationEdit, name='locationEdit'),
    path('disabilityRegn/', views.disabilityRegn, name='disabilityRegn'),
    path('disabilityInsert/', views.disabilityInsert, name='disabilityInsert'),
    path('disabilityView/', views.disabilityView, name='disabilityView'),
    path('disabilityDelete/<int:id>/', views.disabilityDelete, name='disabilityDelete'),
    path('disabilityEdit/<int:id>/', views.disabilityEdit, name='disabilityEdit'),
    path('accessibilityRegn/', views.accessibilityRegn, name='accessibilityRegn'),
    path('accessibilityInsert/', views.accessibilityInsert, name='accessibilityInsert'),
    path('accessibilityView/', views.accessibilityView, name='accessibilityView'),
    path('accessibilityDelete/<int:id>/', views.accessibilityDelete, name='accessibilityDelete'),
    path('accessibilityEdit/<int:id>/', views.accessibilityEdit, name='accessibilityEdit'),
]