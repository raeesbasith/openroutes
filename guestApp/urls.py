from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('guest/',views.guestHome, name='guest'),
    path('register-select/',views.regn_select, name='regn_select'),
    path('traveller-register/',views.traveller_regn, name='traveller_regn'),
    path('login/',views.login_view, name='login'),
]