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
    path('operator-home/package-details/<int:tour_id>/', views.package_single_view, name='package_single_view'),
    path('operator-home/delete-tour-image/<int:image_id>/', views.delete_tour_image, name='delete_tour_image'),
    path('operator-home/bookings/', views.booking_view, name='booking_view'),
    path('operator-home/update-booking-status/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
    path('operator-home/process-refund/<int:booking_id>/', views.process_refund, name='process_refund'),
    path('operator-home/profile/', views.profile_view, name='operator_profile'),
    path('operator-home/reports/', views.datewise_report, name='datewise_report'),
    path('operator-home/reports/export/', views.bookings_export, name='bookings_export'),
]