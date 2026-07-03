from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('orders/list/',views.orders_list,name='orders_list'),
    path('orders/<int:good_id>/',views.orders,name='orders'),
    path('my/',views.my_orders,name='my_orders'),
]