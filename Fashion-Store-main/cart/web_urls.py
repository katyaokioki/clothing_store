from django.urls import path
from .web_views import view_cart, add_to_cart, update_item, remove_item, apply_coupon

urlpatterns = [
    path('', view_cart, name='view_cart'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('update/<int:item_id>/', update_item, name='update_item'),
    path('remove/<int:item_id>/', remove_item, name='remove_item'),
    path('apply-coupon/', apply_coupon, name='apply_coupon'),
]
