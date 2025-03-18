from django.contrib import admin
from .models import GeoLocation

@admin.register(GeoLocation)
class GeoLocationAdmin(admin.ModelAdmin):
    """Admin interface for the GeoLocation model."""
    list_display = ('id', 'user', 'timestamp', 'location_display')
    list_filter = ('timestamp', 'user')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    
    def location_display(self, obj):
        """Custom display for the location field showing lat/long coordinates."""
        return f"({obj.location.x}, {obj.location.y})"
    location_display.short_description = 'Coordinates' 