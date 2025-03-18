from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import Point
from .models import GeoLocation
from .serializers import GeoLocationSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

# Create your views here.

class GeoLocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows GeoLocations to be viewed or created.
    
    POST data format:
    {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [longitude, latitude]
        },
        "properties": {
            "timestamp": "2024-03-18T12:00:00Z"  # Optional, will default to current time
        }
    }
    """
    queryset = GeoLocation.objects.all().order_by('-timestamp')
    serializer_class = GeoLocationSerializer

    # Allow any user to create a GeoLocation
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except (ValueError, TypeError) as e:
            return Response(
                {'error': 'Invalid location data. Please provide valid longitude and latitude.'},
                status=status.HTTP_400_BAD_REQUEST
            )
