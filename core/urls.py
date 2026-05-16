from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    DashboardView,
    LogoutView,
    SearchView,
    MedicineManagementView,
    DiseasePredictionView,
    ToggleShopStatusView,
)

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('search/', SearchView.as_view(), name='search'),
    path('medicine-management/', MedicineManagementView.as_view(), name='medicine_management'),
    path('disease-prediction/', DiseasePredictionView.as_view(), name='disease_prediction'),
    path('toggle-shop-status/', ToggleShopStatusView.as_view(), name='toggle_shop_status'),
    # Add other core app URLs here
]
