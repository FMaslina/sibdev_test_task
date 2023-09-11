from django.urls import path
from users.views import CreateUserView, TokenAuthView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('user/register', CreateUserView.as_view(), name='register'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/login', TokenAuthView.as_view(), name='login_jwt'),
]
