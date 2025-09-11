from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api_views import SignupAPIView

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='api-signup'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
