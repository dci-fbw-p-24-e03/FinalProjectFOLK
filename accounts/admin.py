from django.contrib import admin
from .models import CustomUser

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'stars')  
    search_fields = ('username', 'email')  
    list_filter = ('is_active', 'is_staff')  
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'stars', 'image')  
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)