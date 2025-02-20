from django.contrib import admin
from game.models import Questions

class QuestionsAdmin(admin.ModelAdmin):
    list_display = ('question', 'player')  
    search_fields = ('question', 'player')    
    fieldsets = (
        (None, {
            'fields': ('question', 'player')  
        }),
    )

admin.site.register(Questions)