from rest_framework.routers import DefaultRouter
from .api_views import CartViewSet, CartItemViewSet

router = DefaultRouter()
router.register('items', CartItemViewSet, basename='cart-items')
router.register('', CartViewSet, basename='cart')

urlpatterns = router.urls
