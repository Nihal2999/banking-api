from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    BankAccountListCreateView,
    BankAccountDetailView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("bank-accounts/", BankAccountListCreateView.as_view(), name="bank-accounts"),
    path("bank-accounts/<uuid:pk>/", BankAccountDetailView.as_view(), name="bank-account-detail"),
]