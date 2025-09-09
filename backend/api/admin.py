from django.contrib import admin
from .models import Category, Tag, Note, Attachment, LearningProgress


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at', 'notes_count']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def notes_count(self, obj):
        return obj.notes.count()
    notes_count.short_description = 'Notes Count'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at', 'notes_count']
    list_filter = ['created_at', 'user']
    search_fields = ['name']
    readonly_fields = ['created_at']
    
    def notes_count(self, obj):
        return obj.notes.count()
    notes_count.short_description = 'Notes Count'


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'user', 'difficulty', 'is_favorite', 'created_at']
    list_filter = ['difficulty', 'is_favorite', 'is_archived', 'category', 'created_at', 'user']
    search_fields = ['title', 'content', 'summary']
    readonly_fields = ['created_at', 'updated_at', 'last_reviewed']
    filter_horizontal = ['tags']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'summary', 'category')
        }),
        ('Classification', {
            'fields': ('tags', 'difficulty', 'source_url')
        }),
        ('Status', {
            'fields': ('is_favorite', 'is_archived')
        }),
        ('Metadata', {
            'fields': ('user', 'created_at', 'updated_at', 'last_reviewed'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'note', 'file_type', 'get_file_size_display', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['original_name', 'description', 'note__title']
    readonly_fields = ['uploaded_at', 'file_size']


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_notes', 'current_streak', 'longest_streak', 'last_activity_date']
    list_filter = ['last_activity_date']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['user__username']
