from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, PredictView, HistoryView, HistoryDetailView, MyTokenObtainPairView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', MyTokenObtainPairView.as_view(), name='auth_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth_refresh'),
    path('predict/', PredictView.as_view(), name='predict'),
    path('history/', HistoryView.as_view(), name='history'),
    path('history/<int:pk>/', HistoryDetailView.as_view(), name='history_detail'),
]
