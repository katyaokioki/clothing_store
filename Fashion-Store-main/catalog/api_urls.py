from rest_framework.routers import DefaultRouter
from .api_views import CategoryViewSet, ProductViewSet, ProductVariantViewSet, ReviewViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)
router.register('variants', ProductVariantViewSet)
router.register('reviews', ReviewViewSet)

urlpatterns = router.urls
