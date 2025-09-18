from django.urls import path
from .web_views import signup_view, login_view, logout_view, ResetPasswordView, ResetPasswordConfirmView,add_address,profile,address_list,edit_address
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path("profile/", profile, name="profile"),
    path('logout/', logout_view, name='logout'),
    path('add-address/', add_address, name='add_address'),
    path("addresses/", address_list, name="address_list"),
    path("addresses/edit/<int:id>/", edit_address, name="edit_address"),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
]
