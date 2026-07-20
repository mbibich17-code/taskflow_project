from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'priority', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    ordering = ['-created_at']
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'description', 'author')
        }),
        ('État et priorité', {
            'fields': ('status', 'priority', 'is_completed')
        }),
        ('Dates', {
            'fields': ('due_date', 'created_at', 'updated_at')
        }),
    )
