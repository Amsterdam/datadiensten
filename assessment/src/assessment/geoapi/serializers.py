from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import Point, GEOSGeometry, GEOSException
from .models import GeoLocation
from django.utils import timezone

class GeoLocationSerializer(serializers.ModelSerializer):
    """
    Serializer for GeoLocation model that accepts coordinates in multiple formats:
    
    JSON format:
    {
      "coordinates": [longitude, latitude],
      "timestamp": "2024-03-18T12:00:00Z"  # Optional
    }
    
    OR individual coordinate fields (for HTML forms):
    {
      "longitude": 4.8897,
      "latitude": 52.3740,
      "timestamp": "2024-03-18T12:00:00Z"  # Optional
    }
    """
    coordinates = serializers.ListField(
        child=serializers.FloatField(),
        required=False,
        min_length=2,
        max_length=2,
        write_only=True,
    )
    
    # Add individual coordinate fields for HTML forms
    longitude = serializers.FloatField(required=False, write_only=True)
    latitude = serializers.FloatField(required=False, write_only=True)
    
    distance = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = GeoLocation
        fields = ('id', 'coordinates', 'longitude', 'latitude', 'timestamp', 'distance')
        read_only_fields = ('id', 'distance')
    
    def get_distance(self, obj):
        """Return distance in meters if available"""
        if hasattr(obj, 'distance') and obj.distance is not None:
            return obj.distance.m
        return None
    
    def validate(self, data):
        """Validate that either coordinates or longitude/latitude are provided"""
        coordinates = data.get('coordinates')
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        
        # Check if either coordinates OR both longitude and latitude are provided
        if coordinates is None and (longitude is None or latitude is None):
            raise serializers.ValidationError(
                "Either 'coordinates' array or both 'longitude' and 'latitude' fields must be provided"
            )
        
        # If both formats are provided, prefer coordinates
        if coordinates is not None:
            # Remove longitude/latitude if coordinates is provided
            if 'longitude' in data:
                data.pop('longitude')
            if 'latitude' in data:
                data.pop('latitude')
        else:
            # Create coordinates from longitude/latitude
            data['coordinates'] = [longitude, latitude]
            # Remove the individual fields
            data.pop('longitude')
            data.pop('latitude')
        
        return data
    
    def validate_coordinates(self, value):
        """Validate coordinates are within valid ranges"""
        if not value or len(value) != 2:
            raise serializers.ValidationError("Coordinates must be [longitude, latitude]")
        
        longitude, latitude = value
        
        if not (-90 <= latitude <= 90):
            raise serializers.ValidationError(f"Latitude must be between -90 and 90, got {latitude}")
        
        if not (-180 <= longitude <= 180):
            raise serializers.ValidationError(f"Longitude must be between -180 and 180, got {longitude}")
            
        return value
    
    def create(self, validated_data):
        """Create a GeoLocation object from simplified data"""
        coordinates = validated_data.pop('coordinates')
        longitude, latitude = coordinates
        
        # Create the Point object
        point = Point(longitude, latitude, srid=4326)
        
        # Set the timestamp if provided, otherwise it will use the default
        timestamp = validated_data.get('timestamp', timezone.now())
        
        # Create and return the GeoLocation instance
        return GeoLocation.objects.create(
            location=point,
            timestamp=timestamp
        )
    
    def to_representation(self, instance):
        """Convert GeoLocation to simplified representation"""
        data = super().to_representation(instance)
        # Add coordinates to the output
        data['coordinates'] = [instance.location.x, instance.location.y]
        return data