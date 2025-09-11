from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Fashion Store API",
        default_version='v1',
        description="API documentation for Fashion Store",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.web_urls')),
    path('accounts/', include('accounts.web_urls')),
    path('cart/', include('cart.web_urls')),
    path('orders/', include('orders.web_urls')),
    path('api/auth/', include('accounts.api_urls')),
    path('api/products/', include('catalog.api_urls')),
    path('api/cart/', include('cart.api_urls')),
    path('api/orders/', include('orders.api_urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
