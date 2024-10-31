from django.urls import path
from .views import UtilityRateView, HomeView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('api/utility-rates/', UtilityRateView.as_view(), name='utility-rates'),
]