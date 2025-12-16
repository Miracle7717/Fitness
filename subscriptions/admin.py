from django.contrib import admin
from .models import MembershipPlan, Membership

@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'get_period_display_text', 'visit_limit', 'is_active')
    list_filter = ('is_active', 'access_time')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'price')
        }),
        ('Период действия', {
            'fields': ('period_value', 'period_type')
        }),
        ('Ограничения', {
            'fields': ('visit_limit', 'access_time')
        }),
        ('Дополнительные возможности', {
            'fields': ('can_freeze', 'max_freeze_days')
        }),
        ('Отображение', {
            'fields': ('is_active', 'display_order')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('client', 'plan', 'start_date', 'end_date', 'status', 'remaining_visits')
    list_filter = ('status', 'plan', 'start_date')
    search_fields = ('client__first_name', 'client__last_name', 'client__phone')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('client', 'plan')
        }),
        ('Даты', {
            'fields': ('start_date', 'end_date')
        }),
        ('Статус и посещения', {
            'fields': ('status', 'remaining_visits', 'auto_renewal')
        }),
        ('Заморозка', {
            'fields': ('frozen_until',),
            'classes': ('collapse',)
        }),
        ('Примечания', {
            'fields': ('notes',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )