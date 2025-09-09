from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color code
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ('name', 'user')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Tag(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('name', 'user')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Note(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True, help_text="Brief summary of the note")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='notes')
    tags = models.ManyToManyField(Tag, blank=True, related_name='notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='beginner')
    is_favorite = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    source_url = models.URLField(blank=True, help_text="Source URL if learning from online")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def mark_as_reviewed(self):
        """Mark note as reviewed with current timestamp"""
        self.last_reviewed = timezone.now()
        self.save()


class Attachment(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]

    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='other')
    file_size = models.PositiveIntegerField()  # Size in bytes
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.original_name} ({self.note.title})"

    def get_file_size_display(self):
        """Return human readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class LearningProgress(models.Model):
    """Track learning progress and statistics"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_progress')
    total_notes = models.PositiveIntegerField(default=0)
    notes_reviewed_today = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)  # Days of continuous learning
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Progress for {self.user.username}"

    def update_daily_progress(self):
        """Update daily progress and streaks"""
        today = timezone.now().date()
        
        if self.last_activity_date != today:
            # Reset daily count for new day
            self.notes_reviewed_today = 0
            
            # Update streak logic
            if self.last_activity_date == today - timezone.timedelta(days=1):
                # Consecutive day
                self.current_streak += 1
            else:
                # Streak broken
                self.current_streak = 1
                
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
                
            self.last_activity_date = today
            
        self.notes_reviewed_today += 1
        self.save()
