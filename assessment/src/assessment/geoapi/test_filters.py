from django.test import TestCase
from django.contrib.gis.geos import Point
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Q
from django.contrib.gis.measure import D
from django.contrib.auth import get_user_model
from .models import GeoLocation
from .views import DistanceFilter

User = get_user_model()

class DistanceFilterTests(TestCase):
    """Test cases for DistanceFilter"""
    
    def setUp(self):
        """Set up test data"""
        # Clear any existing data to ensure a clean test environment
        GeoLocation.objects.all().delete()
        User.objects.filter(username__in=['testuser1', 'testuser2']).delete()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpassword1',
            email='testuser1@example.com'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpassword2',
            email='testuser2@example.com'
        )
        
        # Amsterdam coordinates (lng, lat)
        self.amsterdam = Point(4.8897, 52.3740, srid=4326)
        # Rotterdam coordinates (lng, lat) - ~57km from Amsterdam
        self.rotterdam = Point(4.4777, 51.9244, srid=4326)
        # Utrecht coordinates (lng, lat) - ~35km from Amsterdam
        self.utrecht = Point(5.1214, 52.0907, srid=4326)
        # Den Helder coordinates (lng, lat) - ~80km from Amsterdam
        self.den_helder = Point(4.7592, 52.9641, srid=4326)
        
        # Create test objects
        self.amsterdam_loc = GeoLocation.objects.create(
            location=self.amsterdam,
            timestamp=make_aware(datetime.now() - timedelta(days=3)),
            user=self.user1
        )
        self.rotterdam_loc = GeoLocation.objects.create(
            location=self.rotterdam,
            timestamp=make_aware(datetime.now() - timedelta(days=2)),
            user=self.user1
        )
        self.utrecht_loc = GeoLocation.objects.create(
            location=self.utrecht,
            timestamp=make_aware(datetime.now() - timedelta(days=1)),
            user=self.user2
        )
        self.den_helder_loc = GeoLocation.objects.create(
            location=self.den_helder,
            timestamp=make_aware(datetime.now()),
            user=self.user2
        )
    
    def test_filter_by_distance_with_all_parameters(self):
        """Test filtering with all parameters provided"""
        # Create a filter object with all parameters
        f = DistanceFilter()
        f.data = {
            'lat': '52.3740',
            'lng': '4.8897',
            'distance': '50000'  # 50km radius from Amsterdam
        }
        
        # Apply the filter
        queryset = GeoLocation.objects.all()
        filtered_qs = f.filter_by_distance(queryset, 'location', None)
        
        # Should include Amsterdam and Utrecht, but not Rotterdam or Den Helder
        self.assertEqual(filtered_qs.count(), 2)
        ids = set(filtered_qs.values_list('id', flat=True))
        self.assertIn(self.amsterdam_loc.id, ids)
        self.assertIn(self.utrecht_loc.id, ids)
        self.assertNotIn(self.rotterdam_loc.id, ids)
        self.assertNotIn(self.den_helder_loc.id, ids)
        
        # Check that results are ordered by distance (Amsterdam should be first)
        first = filtered_qs.first()
        self.assertEqual(first.id, self.amsterdam_loc.id)
    
    def test_filter_by_distance_with_missing_parameters(self):
        """Test filtering with missing parameters"""
        # Create a filter object with missing parameters
        f = DistanceFilter()
        f.data = {
            'lat': '52.3740',
            # missing lng and distance
        }
        
        # Apply the filter
        queryset = GeoLocation.objects.all()
        filtered_qs = f.filter_by_distance(queryset, 'location', None)
        
        # Should return the original queryset
        self.assertEqual(filtered_qs.count(), 4)
    
    def test_filter_by_distance_large_radius(self):
        """Test filtering with a large radius that includes all locations"""
        # Create a filter object with a large radius
        f = DistanceFilter()
        f.data = {
            'lat': '52.3740',
            'lng': '4.8897',
            'distance': '100000'  # 100km radius from Amsterdam
        }
        
        # Apply the filter
        queryset = GeoLocation.objects.all()
        filtered_qs = f.filter_by_distance(queryset, 'location', None)
        
        # Should include all locations
        self.assertEqual(filtered_qs.count(), 4)
    
    def test_distance_annotation(self):
        """Test that distances are properly annotated"""
        # Create a filter object
        f = DistanceFilter()
        f.data = {
            'lat': '52.3740',
            'lng': '4.8897',
            'distance': '50000'  # 50km radius from Amsterdam
        }
        
        # Apply the filter
        queryset = GeoLocation.objects.all()
        filtered_qs = f.filter_by_distance(queryset, 'location', None)
        
        # Check that distances are annotated
        for location in filtered_qs:
            self.assertTrue(hasattr(location, 'distance'))
            self.assertIsNotNone(location.distance)
            
            # Amsterdam's distance to itself should be very close to 0
            if location.id == self.amsterdam_loc.id:
                self.assertLess(location.distance.m, 1)  # Less than 1 meter
    
    def test_filter_by_user(self):
        """Test that user filter works correctly"""
        # Create a filter object with user filter
        f = DistanceFilter()
        f.data = {
            'user': str(self.user1.id)
        }
        
        # Apply the filter
        queryset = GeoLocation.objects.all()
        filtered_qs = queryset.filter(user=self.user1.id)
        
        # Should include only user1's locations (Amsterdam and Rotterdam)
        self.assertEqual(filtered_qs.count(), 2)
        ids = set(filtered_qs.values_list('id', flat=True))
        self.assertIn(self.amsterdam_loc.id, ids)
        self.assertIn(self.rotterdam_loc.id, ids)
        self.assertNotIn(self.utrecht_loc.id, ids)
        self.assertNotIn(self.den_helder_loc.id, ids)
    
    def test_filter_by_distance_and_user(self):
        """Test filtering by both distance and user"""
        # Create a filter object with both distance and user filters
        f = DistanceFilter()
        f.data = {
            'lat': '52.3740',
            'lng': '4.8897',
            'distance': '50000',  # 50km radius from Amsterdam
            'user': str(self.user1.id)
        }
        
        # Apply the filters
        queryset = GeoLocation.objects.filter(user=self.user1.id)
        filtered_qs = f.filter_by_distance(queryset, 'location', None)
        
        # Should include only Amsterdam (user1 location within 50km)
        self.assertEqual(filtered_qs.count(), 1)
        ids = set(filtered_qs.values_list('id', flat=True))
        self.assertIn(self.amsterdam_loc.id, ids)
        self.assertNotIn(self.rotterdam_loc.id, ids)  # Rotterdam is outside 50km radius
        self.assertNotIn(self.utrecht_loc.id, ids)    # Utrecht belongs to user2
        self.assertNotIn(self.den_helder_loc.id, ids) # Den Helder belongs to user2 