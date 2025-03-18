from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import GeoLocation

class GeoLocationSerializer(GeoFeatureModelSerializer):
    """
    Serializer for GeoLocation model that converts to/from GeoJSON format.
    """
    class Meta:
        model = GeoLocation
        geo_field = 'location'  # Specify the geometry field
        fields = ('id', 'location', 'timestamp')  # Fields to include in the serialization 