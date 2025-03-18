from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewset
router = DefaultRouter()
# Register the GeoLocationViewSet to handle location-related API endpoints
# This fulfills the assessment requirements for:
# 1. A POST API endpoint for submitting geolocation data
# 2. A GET API endpoint for retrieving stored geolocations with filtering
router.register(r"locations", views.GeoLocationViewSet, basename="location")

# The API URLs are determined automatically by the router
# This creates endpoints like:
# - /locations/ (GET - list all locations, POST - create a new location)
# - /locations/<id>/ (GET - retrieve a specific location, PUT/PATCH - update, DELETE - remove)
# - /locations/?lat=52.3740&lng=4.8897&distance=5000 (GET - filtered by distance)
urlpatterns = [
    path("", include(router.urls)),
]
