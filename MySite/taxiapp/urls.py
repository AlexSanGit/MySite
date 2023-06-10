from django.urls import path
from taxiapp import views

urlpatterns = [
    path('taxiapp/', views.home, name='taxihome'),
    path('taxiapp/select_city', views.select_city, name='select_city'),
    path('taxiapp/driver/', views.driver, name='driver'),
    path('taxiapp/passenger/', views.passenger, name='passenger'),
    path('taxiapp/select_taxi/', views.select_taxi, name='select_taxi'),
    path('taxiapp/booking_success/', views.booking_success, name='booking_success'),
    path('choose_taxi/', views.choose_taxi, name='choose_taxi'),
    path('order/<int:taxi_id>/', views.order, name='order'),
    path('order_confirmation/', views.order_confirmation, name='order_confirmation'),
]
