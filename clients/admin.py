from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'phone', 'email', 'status', 'registration_date')
    list_filter = ('status', 'registration_date')
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at', 'registration_date')
    fieldsets = (
        ('Основная информация', {
            'fields': ('first_name', 'last_name', 'middle_name', 'birth_date')
        }),
        ('Контактная информация', {
            'fields': ('phone', 'email')
        }),
        ('Дополнительно', {
            'fields': ('photo', 'medical_notes', 'notes', 'status')
        }),
        ('Системная информация', {
            'fields': ('registration_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'ФИО'