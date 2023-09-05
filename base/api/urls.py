from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('room/<str:pk>/', views.get_rooms),
]
