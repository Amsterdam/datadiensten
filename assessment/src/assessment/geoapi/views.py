from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters
from .models import GeoLocation
from .serializers import GeoLocationSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

# Create your views here.

class DistanceFilter(FilterSet):
    """
    Filter for GeoLocation objects based on distance from a point.
    """
    lat = filters.NumberFilter(method='filter_by_distance', label='Latitude')
    lng = filters.NumberFilter(method='filter_by_distance', label='Longitude')
    distance = filters.NumberFilter(method='filter_by_distance', label='Distance in meters')
    
    class Meta:
        model = GeoLocation
        fields = ['lat', 'lng', 'distance']
    
    def filter_by_distance(self, queryset, name, value):
        """
        Filter queryset to only include locations within the specified distance.
        """
        if 'lat' in self.data and 'lng' in self.data and 'distance' in self.data:
            lat = float(self.data['lat'])
            lng = float(self.data['lng'])
            distance = float(self.data['distance'])
            
            # Create a point based on the provided latitude and longitude
            point = Point(lng, lat, srid=4326)
            
            # Filter queryset to only include points within the specified distance
            # Also annotate each point with its distance from the given point
            return queryset.annotate(
                distance=Distance('location', point)
            ).filter(
                location__distance_lte=(point, D(m=distance))
            ).order_by('distance')
        
        return queryset

class GeoLocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows GeoLocations to be viewed or created.
    
    POST data formats:
    
    JSON format:
    {
      "coordinates": [longitude, latitude],
      "timestamp": "2024-03-18T12:00:00Z"  # Optional, will default to current time
    }
    
    HTML form format:
    {
      "longitude": 4.8897,
      "latitude": 52.3740,
      "timestamp": "2024-03-18T12:00:00Z"  # Optional, will default to current time
    }
    
    GET parameters for distance filtering:
    - lat: Latitude of the center point
    - lng: Longitude of the center point
    - distance: Distance in meters
    
    Example: /api/locations/?lat=52.3740&lng=4.8897&distance=5000
    This will return all locations within 5km of Amsterdam center, ordered by proximity.
    """
    queryset = GeoLocation.objects.all().order_by('-timestamp')
    serializer_class = GeoLocationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = DistanceFilter
    ordering_fields = ['timestamp', 'distance']

    # Allow any user to create a GeoLocation
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Create a new GeoLocation instance with validation.
        
        Validates:
        - Coordinate ranges
        - Data types
        """
        try:
            # The serializer will handle validation of the location data
            return super().create(request, *args, **kwargs)
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Invalid data format: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Handle any unexpected errors
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
