from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('operator-home/', views.operator_home, name='operator_home'),
    path('operator-home/tour-regn-view/', views.tour_regn_view, name='tour_regn_view'),
    path('operator-home/tour-regn-insert/', views.tour_regn_insert, name='tour_regn_insert'),
    path('filllocations/', views.filllocations, name='filllocations'),
    path('operator-home/tour-view/', views.tour_view, name='tour_view'),
    path('operator-home/edit-package/<int:tour_id>/', views.edit_package, name='edit_package'),
    path('operator-home/delete-package/<int:tour_id>/', views.delete_package, name='delete_package'),
    path('operator-home/delete-tour-image/<int:image_id>/', views.delete_tour_image, name='delete_tour_image'),
]