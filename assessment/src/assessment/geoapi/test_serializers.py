from django.test import TestCase
from django.contrib.gis.geos import Point
from django.utils import timezone
from django.contrib.auth import get_user_model
from .serializers import GeoLocationSerializer, UserSerializer
from .models import GeoLocation

User = get_user_model()


class UserSerializerTests(TestCase):
    """Test cases for UserSerializer"""

    def setUp(self):
        """Set up test data for UserSerializer tests"""
        # Clear any existing user test data to ensure a clean environment
        User.objects.filter(username="testuser").delete()

        self.user_attributes = {
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com",
        }
        self.user = User.objects.create_user(**self.user_attributes)

    def test_user_serializer(self):
        """Test that UserSerializer correctly serializes a user"""
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data["id"], self.user.id)
        self.assertEqual(serializer.data["username"], "testuser")
        # Validate security - sensitive fields should not be included
        self.assertNotIn("password", serializer.data)
        self.assertNotIn("email", serializer.data)


class GeoLocationUserSerializerTests(TestCase):
    """Test cases for user functionality in GeoLocation serializer"""

    def setUp(self):
        """Set up test data for GeoLocation serializer tests with user"""
        # Clear any existing test data to ensure a clean environment
        GeoLocation.objects.all().delete()
        User.objects.filter(username="testuser").delete()

        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="test@example.com"
        )
        # Amsterdam coordinates
        self.point = Point(4.8897, 52.3740, srid=4326)
        self.geolocation = GeoLocation.objects.create(
            location=self.point, timestamp=timezone.now(), user=self.user
        )

    def test_user_in_serializer_output(self):
        """Test that user information is included in the serializer output"""
        serializer = GeoLocationSerializer(self.geolocation)
        self.assertIn("user", serializer.data)
        self.assertEqual(serializer.data["user"]["id"], self.user.id)
        self.assertEqual(serializer.data["user"]["username"], "testuser")

    def test_create_with_user(self):
        """Test creating a GeoLocation with a user"""
        serializer = GeoLocationSerializer()
        timestamp = timezone.now()
        validated_data = {
            "coordinates": [4.8897, 52.3740],
            "timestamp": timestamp,
            "user": self.user,
        }
        instance = serializer.create(validated_data)
        # Validate all fields are correctly set
        self.assertEqual(instance.user, self.user)
        self.assertEqual(instance.location.x, 4.8897)
        self.assertEqual(instance.location.y, 52.3740)
        self.assertEqual(instance.timestamp, timestamp)

    def test_create_without_user(self):
        """Test creating a GeoLocation without a user"""
        serializer = GeoLocationSerializer()
        timestamp = timezone.now()
        validated_data = {"coordinates": [4.8897, 52.3740], "timestamp": timestamp}
        instance = serializer.create(validated_data)
        # Validate all fields are correctly set and user is None
        self.assertIsNone(instance.user)
        self.assertEqual(instance.location.x, 4.8897)
        self.assertEqual(instance.location.y, 52.3740)
        self.assertEqual(instance.timestamp, timestamp)


class GeoLocationSerializerTests(TestCase):
    """Test cases for GeoLocationSerializer"""

    def setUp(self):
        """Set up test data for GeoLocationSerializer tests"""
        # Clear any existing GeoLocation objects to ensure a clean test environment
        GeoLocation.objects.all().delete()

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
        data = {"coordinates": [4.8897, 52.3740]}
        result = serializer.validate(data)
        self.assertEqual(result["coordinates"], [4.8897, 52.3740])

    def test_validate_data_with_lat_lng(self):
        """Test validating data with lat/lng format"""
        serializer = GeoLocationSerializer()
        data = {"latitude": 52.3740, "longitude": 4.8897}
        result = serializer.validate(data)
        self.assertEqual(result["coordinates"], [4.8897, 52.3740])

    def test_validate_data_with_both_formats(self):
        """Test validating data with both formats (should prefer coordinates)"""
        serializer = GeoLocationSerializer()
        data = {
            "coordinates": [4.8897, 52.3740],
            "latitude": 51.9244,
            "longitude": 4.4777,
        }
        result = serializer.validate(data)
        self.assertEqual(result["coordinates"], [4.8897, 52.3740])
        self.assertNotIn("latitude", result)
        self.assertNotIn("longitude", result)

    def test_validate_data_missing_both_formats(self):
        """Test validating data without coordinates or lat/lng"""
        serializer = GeoLocationSerializer()
        data = {"timestamp": timezone.now()}
        with self.assertRaises(Exception) as context:
            serializer.validate(data)
        self.assertIn(
            "Either 'coordinates' array or both 'longitude' and 'latitude' fields must be provided",
            str(context.exception),
        )

    def test_create_with_coordinates(self):
        """Test creating a GeoLocation with coordinates"""
        serializer = GeoLocationSerializer()
        timestamp = timezone.now()
        validated_data = {"coordinates": [4.8897, 52.3740], "timestamp": timestamp}
        instance = serializer.create(validated_data)
        # Validate all fields are correctly set
        self.assertEqual(instance.location.x, 4.8897)
        self.assertEqual(instance.location.y, 52.3740)
        self.assertEqual(instance.timestamp, timestamp)
        self.assertIsNone(instance.user)

    def test_to_representation(self):
        """Test serializing a GeoLocation to representation"""
        # Create test data
        point = Point(4.8897, 52.3740, srid=4326)  # Amsterdam
        timestamp = timezone.now()
        instance = GeoLocation.objects.create(location=point, timestamp=timestamp)

        # Test serialization
        serializer = GeoLocationSerializer(instance)
        data = serializer.data

        # Validate representation
        self.assertEqual(data["coordinates"], [4.8897, 52.3740])
        self.assertIn("timestamp", data)
        self.assertIn("id", data)

        # Test that distance is null when not annotated
        self.assertIsNone(data["distance"])
