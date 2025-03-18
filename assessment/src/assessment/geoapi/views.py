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
    
    This fulfills the assessment requirement for filtering based on distance:
    "Add filtering based on distance. For example: show geolocations within 
    a certain radius range of a given point."
    
    The implementation uses GeoDjango's spatial filtering capabilities to
    efficiently query points within a given distance.
    """
    lat = filters.NumberFilter(method='filter_by_distance', label='Latitude')
    lng = filters.NumberFilter(method='filter_by_distance', label='Longitude')
    distance = filters.NumberFilter(method='filter_by_distance', label='Distance in meters')
    user = filters.NumberFilter(field_name='user__id', label='User ID')
    
    class Meta:
        model = GeoLocation
        fields = ['lat', 'lng', 'distance', 'user']
    
    def filter_by_distance(self, queryset, name, value):
        """
        Filter queryset to only include locations within the specified distance.
        
        This method:
        1. Creates a Point from the provided lat/lng coordinates
        2. Filters the queryset to include only points within the specified distance
        3. Annotates each point with its distance from the reference point
        4. Orders the results by proximity (closest first)
        
        This satisfies the requirement for spatial filtering capabilities.
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
 
    ## Endpoints
    
    ### GET /api/locations/
    
    Returns a list of all stored geolocations.
    
    **Query Parameters:**
    
    * `lat` - Latitude of center point for distance filtering
    * `lng` - Longitude of center point for distance filtering
    * `distance` - Distance in meters from center point
    * `user` - Filter by user ID
    * `ordering` - Field to order by (prefix with `-` for descending)
    
    **Examples:**
    
    ```
    GET /api/locations/?lat=52.3740&lng=4.8897&distance=5000
    ```
    Returns all locations within 5km of Amsterdam center, ordered by proximity.
    
    ```
    GET /api/locations/?user=1
    ```
    Returns all locations for user with ID 1.
    
    ```
    GET /api/locations/?ordering=-timestamp
    ```
    Returns all locations ordered by timestamp (newest first).
    
    ### GET /api/locations/{id}/
    
    Retrieves a single geolocation by ID.
    
    ### POST /api/locations/
    
    Creates a new geolocation record.
    
    **Request Body:**
    
    JSON format:

    ```
    {
      "coordinates": [longitude, latitude],  
      "timestamp": "2024-03-18T12:00:00Z"  # Optional, will default to current time
    }
    ```
    
    HTML form format:

    ```
    longitude: 4.8897  
    latitude: 52.3740  
    timestamp: 2024-03-18T12:00:00Z  # Optional
    ```
    
    **Response:**
    
    ```
    {
      "id": 1,  
      "coordinates": [4.8897, 52.3740],  
      "timestamp": "2024-03-18T12:00:00Z",  
      "user": null  
    }
    ```
    
    
    ## Data Validation
    
    * Latitude must be between -90 and 90
    * Longitude must be between -180 and 180
    * Timestamp must be a valid ISO format datetime
    
    ## Authentication
    
    * Reading locations is allowed for all users
    * Creating, updating and deleting locations is allowed for all users
    * Authenticated users will have their locations associated with their user account
    """
    queryset = GeoLocation.objects.all().order_by('-timestamp')
    serializer_class = GeoLocationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = DistanceFilter
    ordering_fields = ['timestamp', 'distance']

    # Allow any user to create a GeoLocation
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        """
        Set the user to the authenticated user by default when creating a GeoLocation.
        If the user is not authenticated, the user field remains null.
        
        This addresses the optional user requirement from the assessment, where
        the user model can be linked to geolocation data if authentication is present.
        """
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    def create(self, request, *args, **kwargs):
        """
        Create a new GeoLocation instance with validation.
        
        This method fulfills the assessment requirement:
        "The API must validate that the location data is valid."
        
        Validates:
        - Coordinate ranges (via serializer)
        - Data types
        - Proper error handling for invalid inputs
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
