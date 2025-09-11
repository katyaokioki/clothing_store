from django.urls import path
from .web_views import home, product_detail,product_list

urlpatterns = [
    path('', home, name='home'),
     path('product_list/', product_list, name='home'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
]
