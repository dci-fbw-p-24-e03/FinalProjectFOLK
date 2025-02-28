from django.contrib import admin
from .models import CustomUser

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'stars', 'nation', 'average_stars_per_game')  
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff', 'nation')  
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'stars', 'image', 'coins', 'nation', 'average_stars_per_game')  
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password1', 'password2', 'nation', 'average_stars_per_game')  
        }),    
    )

admin.site.register(CustomUser, CustomUserAdmin)