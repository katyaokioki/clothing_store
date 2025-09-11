from django.urls import path
from .web_views import list_orders, order_detail, checkout

urlpatterns = [
    path('', list_orders, name='orders'),
    path('<int:pk>/', order_detail, name='order_detail'),
    path('checkout/', checkout, name='checkout'),
]
