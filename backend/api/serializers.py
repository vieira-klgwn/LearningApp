from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Category, Tag, Note, Attachment, LearningProgress


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # Create learning progress for new user
        LearningProgress.objects.create(user=user)
        return user


class CategorySerializer(serializers.ModelSerializer):
    notes_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'notes_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_notes_count(self, obj):
        return obj.notes.filter(is_archived=False).count()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TagSerializer(serializers.ModelSerializer):
    notes_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'notes_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_notes_count(self, obj):
        return obj.notes.filter(is_archived=False).count()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AttachmentSerializer(serializers.ModelSerializer):
    file_size_display = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'original_name', 'file_type', 'file_size', 
                 'file_size_display', 'description', 'uploaded_at']
        read_only_fields = ['id', 'file_size', 'uploaded_at']

    def get_file_size_display(self, obj):
        return obj.get_file_size_display()


class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    category_name = serializers.CharField(source='category.name', read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'summary', 'category', 'category_name', 
                 'tags', 'tag_ids', 'difficulty', 'is_favorite', 'is_archived', 
                 'source_url', 'attachments', 'created_at', 'updated_at', 'last_reviewed']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        validated_data['user'] = self.context['request'].user
        note = super().create(validated_data)
        
        if tag_ids:
            # Only add tags that belong to the current user
            tags = Tag.objects.filter(id__in=tag_ids, user=note.user)
            note.tags.set(tags)
        
        return note

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        note = super().update(instance, validated_data)
        
        if tag_ids is not None:
            # Only add tags that belong to the current user
            tags = Tag.objects.filter(id__in=tag_ids, user=note.user)
            note.tags.set(tags)
        
        return note

    def validate_category(self, value):
        """Ensure category belongs to the current user"""
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("Category must belong to the current user.")
        return value


class NoteListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for note lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags_count = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ['id', 'title', 'summary', 'category_name', 'difficulty', 
                 'is_favorite', 'is_archived', 'tags_count', 'created_at', 'updated_at']

    def get_tags_count(self, obj):
        return obj.tags.count()


class LearningProgressSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = LearningProgress
        fields = ['username', 'total_notes', 'notes_reviewed_today', 'current_streak', 
                 'longest_streak', 'last_activity_date', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AttachmentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['file', 'description']

    def create(self, validated_data):
        file = validated_data['file']
        validated_data['original_name'] = file.name
        validated_data['file_size'] = file.size
        
        # Determine file type based on extension
        file_extension = file.name.split('.')[-1].lower()
        file_type_mapping = {
            'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'svg': 'image',
            'pdf': 'document', 'doc': 'document', 'docx': 'document', 'txt': 'document',
            'mp4': 'video', 'avi': 'video', 'mov': 'video', 'wmv': 'video',
            'mp3': 'audio', 'wav': 'audio', 'flac': 'audio'
        }
        validated_data['file_type'] = file_type_mapping.get(file_extension, 'other')
        
        return super().create(validated_data)
