from django.test import TestCase
from django.contrib.gis.geos import Point
from django.utils import timezone
from .serializers import GeoLocationSerializer
from .models import GeoLocation


class GeoLocationSerializerTests(TestCase):
    """Test cases for GeoLocationSerializer"""
    
    def test_validate_coordinates_valid(self):
        """Test validating valid coordinates"""
        serializer = GeoLocationSerializer()
        valid_coordinates = [4.8897, 52.3740]  # Amsterdam
        result = serializer.validate_coordinates(valid_coordinates)
        self.assertEqual(result, valid_coordinates)
    
    def test_validate_coordinates_invalid_latitude(self):
        """Test validating coordinates with invalid latitude"""
        serializer = GeoLocationSerializer()
        invalid_coordinates = [4.8897, 95.0]  # Invalid latitude
        with self.assertRaises(Exception) as context:
            serializer.validate_coordinates(invalid_coordinates)
        self.assertIn("Latitude must be between -90 and 90", str(context.exception))
    
    def test_validate_coordinates_invalid_longitude(self):
        """Test validating coordinates with invalid longitude"""
        serializer = GeoLocationSerializer()
        invalid_coordinates = [185.0, 52.3740]  # Invalid longitude
        with self.assertRaises(Exception) as context:
            serializer.validate_coordinates(invalid_coordinates)
        self.assertIn("Longitude must be between -180 and 180", str(context.exception))
    
    def test_validate_data_with_coordinates(self):
        """Test validating data with coordinates format"""
        serializer = GeoLocationSerializer()
        data = {'coordinates': [4.8897, 52.3740]}
        result = serializer.validate(data)
        self.assertEqual(result['coordinates'], [4.8897, 52.3740])
    
    def test_validate_data_with_lat_lng(self):
        """Test validating data with lat/lng format"""
        serializer = GeoLocationSerializer()
        data = {'latitude': 52.3740, 'longitude': 4.8897}
        result = serializer.validate(data)
        self.assertEqual(result['coordinates'], [4.8897, 52.3740])
    
    def test_validate_data_with_both_formats(self):
        """Test validating data with both formats (should prefer coordinates)"""
        serializer = GeoLocationSerializer()
        data = {
            'coordinates': [4.8897, 52.3740],
            'latitude': 51.9244,
            'longitude': 4.4777
        }
        result = serializer.validate(data)
        self.assertEqual(result['coordinates'], [4.8897, 52.3740])
        self.assertNotIn('latitude', result)
        self.assertNotIn('longitude', result)
    
    def test_validate_data_missing_both_formats(self):
        """Test validating data without coordinates or lat/lng"""
        serializer = GeoLocationSerializer()
        data = {'timestamp': timezone.now()}
        with self.assertRaises(Exception) as context:
            serializer.validate(data)
        self.assertIn("Either 'coordinates' array or both 'longitude' and 'latitude' fields must be provided", 
                      str(context.exception))
    
    def test_create_with_coordinates(self):
        """Test creating a GeoLocation with coordinates"""
        serializer = GeoLocationSerializer()
        validated_data = {
            'coordinates': [4.8897, 52.3740],
            'timestamp': timezone.now()
        }
        instance = serializer.create(validated_data)
        self.assertEqual(instance.location.x, 4.8897)
        self.assertEqual(instance.location.y, 52.3740)
    
    def test_to_representation(self):
        """Test serializing a GeoLocation to representation"""
        point = Point(4.8897, 52.3740, srid=4326)
        instance = GeoLocation.objects.create(
            location=point,
            timestamp=timezone.now()
        )
        serializer = GeoLocationSerializer(instance)
        data = serializer.data
        self.assertEqual(data['coordinates'], [4.8897, 52.3740]) 