from django.urls import path
from app.views import HomeView, UtilityRateView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('api/utility-rates/', UtilityRateView.as_view(), name='utility-rates'),
]