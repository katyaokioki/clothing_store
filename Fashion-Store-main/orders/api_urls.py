from rest_framework.routers import DefaultRouter
from .api_views import OrderViewSet, CouponViewSet

router = DefaultRouter()
router.register('coupons', CouponViewSet)
router.register('', OrderViewSet, basename='orders')

urlpatterns = router.urls
