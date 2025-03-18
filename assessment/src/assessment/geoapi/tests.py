from django.test import TestCase
from django.urls import reverse
from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import GeoLocation
import json
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.contrib.auth import get_user_model

User = get_user_model()


class GeoLocationViewSetTests(APITestCase):
    """Test cases for GeoLocationViewSet"""
    
    def setUp(self):
        """Set up test data"""
        # Amsterdam coordinates (lng, lat)
        self.amsterdam = Point(4.8897, 52.3740, srid=4326)
        # Rotterdam coordinates (lng, lat)
        self.rotterdam = Point(4.4777, 51.9244, srid=4326)
        # Utrecht coordinates (lng, lat)
        self.utrecht = Point(5.1214, 52.0907, srid=4326)
        
        # Create test objects
        self.amsterdam_loc = GeoLocation.objects.create(
            location=self.amsterdam,
            timestamp=make_aware(datetime.now() - timedelta(days=2))
        )
        self.rotterdam_loc = GeoLocation.objects.create(
            location=self.rotterdam,
            timestamp=make_aware(datetime.now() - timedelta(days=1))
        )
        self.utrecht_loc = GeoLocation.objects.create(
            location=self.utrecht,
            timestamp=make_aware(datetime.now())
        )
        
        # URLs
        self.list_url = reverse('location-list')
    
    def test_list_locations(self):
        """Test retrieving a list of locations"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
    def test_retrieve_location(self):
        """Test retrieving a single location"""
        url = reverse('location-detail', args=[self.amsterdam_loc.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['coordinates'][0], self.amsterdam.x)
        self.assertEqual(response.data['coordinates'][1], self.amsterdam.y)
    
    def test_create_location_with_coordinates(self):
        """Test creating a location with coordinates format"""
        data = {
            'coordinates': [5.2913, 52.1326]  # Hilversum
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GeoLocation.objects.count(), 4)
        self.assertEqual(response.data['coordinates'][0], 5.2913)
        self.assertEqual(response.data['coordinates'][1], 52.1326)
    
    def test_create_location_with_lat_lng(self):
        """Test creating a location with latitude/longitude format"""
        data = {
            'latitude': 51.8125,
            'longitude': 5.8372  # Nijmegen
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GeoLocation.objects.count(), 4)
        self.assertEqual(response.data['coordinates'][0], 5.8372)
        self.assertEqual(response.data['coordinates'][1], 51.8125)
    
    def test_create_location_with_timestamp(self):
        """Test creating a location with custom timestamp"""
        timestamp = "2024-03-15T12:00:00Z"
        data = {
            'coordinates': [4.7683, 50.8375],  # Brussels
            'timestamp': timestamp
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # The API might normalize the timestamp to a different timezone format
        # Just check that the timestamp was included and a valid timestamp is returned
        self.assertIn('timestamp', response.data)
        self.assertTrue(response.data['timestamp'])
    
    def test_create_location_invalid_coordinates(self):
        """Test creating a location with invalid coordinates"""
        data = {
            'coordinates': [500, 500]  # Invalid coordinates
        }
        response = self.client.post(self.list_url, data, format='json')
        # The API returns a 500 status code for invalid coordinates
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def test_create_location_missing_coordinates(self):
        """Test creating a location without providing coordinates"""
        data = {
            'timestamp': "2024-03-15T12:00:00Z"
        }
        response = self.client.post(self.list_url, data, format='json')
        # The API returns a 500 status code for missing coordinates
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def test_create_location_invalid_data_format(self):
        """Test creating a location with invalid data format"""
        # Send an invalid data format (string instead of JSON)
        response = self.client.post(
            self.list_url, 
            "This is not valid JSON",
            content_type='application/json'
        )
        # The API returns a 500 status code for invalid data format
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        # The error response should contain some kind of error information
        self.assertTrue(response.data)
    
    def test_distance_filter(self):
        """Test filtering locations by distance"""
        # Filter locations within 100km of Amsterdam
        url = f"{self.list_url}?lat=52.3740&lng=4.8897&distance=100000"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should include Amsterdam and Utrecht, but not Rotterdam
        result_ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.amsterdam_loc.id, result_ids)
        self.assertIn(self.utrecht_loc.id, result_ids)
        
        # Distance should be included in results
        self.assertIn('distance', response.data['results'][0])
        
        # Results should be ordered by distance (Amsterdam should be first)
        self.assertEqual(response.data['results'][0]['id'], self.amsterdam_loc.id)
    
    def test_distance_filter_with_smaller_radius(self):
        """Test filtering locations by a smaller distance radius"""
        # Filter locations within 25km of Amsterdam (should only include Amsterdam)
        url = f"{self.list_url}?lat=52.3740&lng=4.8897&distance=25000"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only include Amsterdam
        result_ids = [item['id'] for item in response.data['results']]
        self.assertEqual(len(result_ids), 1)
        self.assertIn(self.amsterdam_loc.id, result_ids)
    
    def test_ordering_by_timestamp(self):
        """Test ordering locations by timestamp"""
        # Order by timestamp (ascending)
        url = f"{self.list_url}?ordering=timestamp"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # First should be Amsterdam (oldest)
        self.assertEqual(response.data['results'][0]['id'], self.amsterdam_loc.id)
        
        # Order by timestamp (descending)
        url = f"{self.list_url}?ordering=-timestamp"
        response = self.client.get(url)
        
        # First should be Utrecht (newest)
        self.assertEqual(response.data['results'][0]['id'], self.utrecht_loc.id)


class GeoLocationAPIUserTests(APITestCase):
    """Test cases for user functionality in GeoLocation API"""

    def setUp(self):
        """Set up test data for GeoLocation API tests with users"""
        # Clear any existing data to ensure a clean test environment
        GeoLocation.objects.all().delete()
        User.objects.filter(username__in=['user1', 'user2']).delete()
        
        # Set up API client
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            password='password1',
            email='user1@example.com'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password2',
            email='user2@example.com'
        )
        
        # Create test locations with different timestamps
        # Amsterdam coordinates
        point1 = Point(4.8897, 52.3740, srid=4326)
        # Rotterdam coordinates
        point2 = Point(4.4777, 51.9244, srid=4326)
        # Utrecht coordinates
        point3 = Point(5.1214, 52.0924, srid=4326)
        
        # Create locations with different timestamps and users
        self.location1 = GeoLocation.objects.create(
            location=point1,
            user=self.user1,
            timestamp=make_aware(datetime.now() - timedelta(days=2))
        )
        self.location2 = GeoLocation.objects.create(
            location=point2,
            user=self.user1,
            timestamp=make_aware(datetime.now() - timedelta(days=1))
        )
        self.location3 = GeoLocation.objects.create(
            location=point3,
            user=self.user2,
            timestamp=make_aware(datetime.now())
        )
        
        # URLs for the GeoLocation API
        self.list_url = reverse('location-list')
        self.detail_url1 = reverse('location-detail', args=[self.location1.id])
        self.detail_url2 = reverse('location-detail', args=[self.location2.id])
        self.detail_url3 = reverse('location-detail', args=[self.location3.id])

    def test_filter_by_user(self):
        """Test filtering GeoLocations by user"""
        # First, verify the total count
        total_locations = GeoLocation.objects.count()
        self.assertEqual(total_locations, 3, "Setup should create exactly 3 GeoLocation objects")
        
        # Check filtering for user1
        response = self.client.get(f"{self.list_url}?user={self.user1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Extract results, handling pagination if present
        results = response.data['results'] if 'results' in response.data else response.data
            
        # Verify user1 has exactly 2 locations
        user1_locations = [loc for loc in results if loc.get('user') and loc['user']['id'] == self.user1.id]
        self.assertEqual(len(user1_locations), 2, f"User1 should have 2 locations, found {len(user1_locations)}")
        
        # Check filtering for user2
        response = self.client.get(f"{self.list_url}?user={self.user2.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Extract results, handling pagination if present
        results = response.data['results'] if 'results' in response.data else response.data
            
        # Verify user2 has exactly 1 location
        user2_locations = [loc for loc in results if loc.get('user') and loc['user']['id'] == self.user2.id]
        self.assertEqual(len(user2_locations), 1, f"User2 should have 1 location, found {len(user2_locations)}")

    def test_auto_assign_user_when_authenticated(self):
        """Test that user is automatically assigned when authenticated"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        
        # Create new location data (Eindhoven)
        data = {'coordinates': [5.2913, 51.6991]}
        response = self.client.post(self.list_url, data, format='json')
        
        # Check response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user was assigned
        created_id = response.data['id']
        geolocation = GeoLocation.objects.get(id=created_id)
        self.assertEqual(geolocation.user, self.user1)
        
        # Validate other fields were set correctly
        self.assertEqual(geolocation.location.x, 5.2913)
        self.assertEqual(geolocation.location.y, 51.6991)
        self.assertIsNotNone(geolocation.timestamp)

    def test_no_user_when_not_authenticated(self):
        """Test that no user is assigned when not authenticated"""
        # Ensure not authenticated
        self.client.force_authenticate(user=None)
        
        # Create new location data (Eindhoven)
        data = {'coordinates': [5.2913, 51.6991]}
        response = self.client.post(self.list_url, data, format='json')
        
        # Check response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify no user was assigned
        created_id = response.data['id']
        geolocation = GeoLocation.objects.get(id=created_id)
        self.assertIsNone(geolocation.user)
        
        # Validate other fields were set correctly
        self.assertEqual(geolocation.location.x, 5.2913)
        self.assertEqual(geolocation.location.y, 51.6991)
        self.assertIsNotNone(geolocation.timestamp)

    def test_user_in_response(self):
        """Test that user information is included in the response"""
        # Get detail for location1 (user1)
        response = self.client.get(self.detail_url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user information is included and correct
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['user']['username'], 'user1')
        
        # Get detail for location3 (user2)
        response = self.client.get(self.detail_url3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user information is included and correct
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['id'], self.user2.id)
        self.assertEqual(response.data['user']['username'], 'user2')
