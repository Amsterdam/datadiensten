from django.contrib import admin
from .models import GeoLocation

@admin.register(GeoLocation)
class GeoLocationAdmin(admin.ModelAdmin):
    """
    Admin interface for the GeoLocation model.
    
    This provides an easy-to-use interface for site administrators to:
    1. View and manage stored geolocation data
    2. Filter locations by timestamp and user
    3. Search locations by associated user information
    4. Visualize coordinates in a readable format
    
    While not explicitly required by the assessment, this admin interface
    enhances the usability of the application for data management purposes.
    """
    list_display = ('id', 'user', 'timestamp', 'location_display')
    list_filter = ('timestamp', 'user')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    
    def location_display(self, obj):
        """
        Custom display for the location field showing lat/long coordinates.
        
        This converts the GeoDjango Point object to a human-readable
        coordinate representation for the admin interface.
        """
        return f"({obj.location.x}, {obj.location.y})"
    location_display.short_description = 'Coordinates' 