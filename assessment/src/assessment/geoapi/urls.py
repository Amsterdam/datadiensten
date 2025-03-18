from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewset
router = DefaultRouter()
router.register(r'locations', views.GeoLocationViewSet, basename='location')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
] 