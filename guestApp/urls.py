from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('guest/',views.guestHome, name='guest'),
    path('regn/',views.regn, name='regn'),
    path('login/',views.login_view, name='login'),
    path('regn_insert/',views.regn_insert, name='regn_insert')
]