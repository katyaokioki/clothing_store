from django.urls import path
from .web_views import home, product_detail,product_list, create_review
from .web_views import catalog_list, delete_review

urlpatterns = [
    path('', home, name='home'),
    path('product_list/', product_list, name='home'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('product/<int:pk>/review/', create_review, name='create_review'),
    path('product/<int:review_id>/delete_review/', delete_review, name='delete_review'),
    path("api/catalog/", catalog_list, name="catalog_list"),
]
