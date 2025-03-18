from django.contrib.gis.db import models
from django.utils import timezone
from django.conf import settings

class GeoLocation(models.Model):
    """
    Model to store geolocation data with timestamp.
    The location field uses GeoDjango's PointField to store latitude and longitude coordinates.
    """
    location = models.PointField(
        help_text="Geographic location (latitude and longitude)",
        spatial_index=True,  # Creates a spatial index for better query performance
        geography=True,  # Use geography type for more accurate distance calculations
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When this location was recorded"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who reported this location"
    )

    # class Meta:
    #     ordering = ['-timestamp']  # Order by most recent first
    #     indexes = [
    #         models.Index(fields=['timestamp']),  # Add index on timestamp for better query performance
    #     ]

    def __str__(self):
        return f"Location ({self.location.x}, {self.location.y}) at {self.timestamp}"
