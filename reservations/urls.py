from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from rest_framework import routers
from .views import FlightReservationViewSet, FlightScheduleViewSet

# Routers
router = routers.DefaultRouter()
router.register(r'flight-schedules', FlightScheduleViewSet)
router.register(r'reservations', FlightReservationViewSet)

urlpatterns = [
    # API
    path('api/', include(router.urls)),

    # Make the root URL redirect to /home/
    path('', RedirectView.as_view(pattern_name='home', permanent=False)),

    # Login, Logout, and Role Selection
    path('login/', views.login_user, name='login'),
    path('login-users/', views.login_users, name='login_users'),
    path('logout/', views.logout_view, name='logout'),  # Only one logout path now

    path('select-role/', views.select_role, name='select_role'),

    # Registration Users
    path('register/', views.register_user, name='register'),

    # User Dashboard and Booking
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('Booking/', views.booking_flight, name='booking_flight'),

    # Home and Admin Dashboard
    path('home/', views.home, name='home'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-flight-schedule/', views.add_flight_schedule, name='add_flight_schedule'),

    # Flight schedule views
    path('view_flight_schedule/', views.view_flight_schedule, name='view_flight_schedule'),
    path('view_flight_schedule1/', views.view_flight_schedule1, name='view_flight_schedule1'),

    # Booking a flight with flight_id
    path('book_a_flight/<int:flight_id>/', views.book_a_flight, name='book_a_flight'),

    # Reservations
    path('reservations/', views.list_reservations, name='list_reservations'),

    path('reservations/edit/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
    path('reservations/cancel/<int:id>/', views.cancel_reservation, name='cancel_reservation'),

    # Edit and Delete flight schedules
    path('edit-flight-schedule/<int:pk>/', views.edit_flight_schedule, name='edit_flight_schedule'),
    path('delete-flight-schedule/<int:id>/', views.delete_flight_schedule, name='delete_flight_schedule'),
    path('edit-schedule/<int:id>/', views.edit_schedule, name='edit_schedule'),
    # Payment
    path('payment/<int:flight_id>/', views.payment, name='payment'),

    path('contact/', views.contact_support, name='contact_support'),
]
