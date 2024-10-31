from django.shortcuts import render
from rest_framework.views import APIView

class HomeView(APIView):
    """View for the main calculator page"""
    def get(self, request):
        return render(request, 'index.html')