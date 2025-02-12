from django.contrib import admin
from .models import CustomUser
from shop.models import Product,Order

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'stars')  
    search_fields = ('username', 'email')  
    list_filter = ('is_active', 'is_staff')  
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'stars', 'image','coins')  
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Product)
admin.site.register(Order)