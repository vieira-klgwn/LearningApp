from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Tag, Note, Attachment, LearningProgress
from .serializers import (
    UserSerializer, UserRegistrationSerializer, CategorySerializer, 
    TagSerializer, NoteSerializer, NoteListSerializer, AttachmentSerializer,
    LearningProgressSerializer, AttachmentUploadSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    return Response(
        {'error': 'Username and password required'}, 
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
def profile(request):
    """Get user profile"""
    return Response(UserSerializer(request.user).data)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)


class NoteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'summary']
    filterset_fields = ['category', 'difficulty', 'is_favorite', 'is_archived']
    ordering_fields = ['created_at', 'updated_at', 'title', 'last_reviewed']
    ordering = ['-updated_at']

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user).select_related('category').prefetch_related('tags', 'attachments')

    def get_serializer_class(self):
        if self.action == 'list':
            return NoteListSerializer
        return NoteSerializer

    @action(detail=True, methods=['post'])
    def mark_reviewed(self, request, pk=None):
        """Mark note as reviewed"""
        note = self.get_object()
        note.mark_as_reviewed()
        
        # Update learning progress
        progress, created = LearningProgress.objects.get_or_create(user=request.user)
        progress.update_daily_progress()
        
        return Response({'status': 'marked as reviewed'})

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status of note"""
        note = self.get_object()
        note.is_favorite = not note.is_favorite
        note.save()
        return Response({'is_favorite': note.is_favorite})

    @action(detail=True, methods=['post'])
    def toggle_archive(self, request, pk=None):
        """Toggle archive status of note"""
        note = self.get_object()
        note.is_archived = not note.is_archived
        note.save()
        return Response({'is_archived': note.is_archived})

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """Get all favorite notes"""
        favorites = self.get_queryset().filter(is_favorite=True, is_archived=False)
        page = self.paginate_queryset(favorites)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recently updated notes"""
        recent_notes = self.get_queryset().filter(is_archived=False)[:10]
        serializer = self.get_serializer(recent_notes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search with filters"""
        queryset = self.get_queryset()
        query = request.query_params.get('q', '')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(summary__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(category__name__icontains=query)
            ).distinct()
        
        # Apply additional filters
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
            
        difficulty = request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
            
        tags = request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__id__in=tags).distinct()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Attachment.objects.filter(note__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return AttachmentUploadSerializer
        return AttachmentSerializer

    def create(self, request, *args, **kwargs):
        note_id = request.data.get('note_id')
        if not note_id:
            return Response(
                {'error': 'note_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            note = Note.objects.get(id=note_id, user=request.user)
        except Note.DoesNotExist:
            return Response(
                {'error': 'Note not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            attachment = serializer.save(note=note)
            return Response(
                AttachmentSerializer(attachment).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def learning_progress(request):
    """Get user's learning progress"""
    progress, created = LearningProgress.objects.get_or_create(user=request.user)
    
    # Update total notes count
    progress.total_notes = Note.objects.filter(user=request.user).count()
    progress.save()
    
    return Response(LearningProgressSerializer(progress).data)


@api_view(['GET'])
def dashboard_stats(request):
    """Get dashboard statistics"""
    user = request.user
    
    # Basic counts
    total_notes = Note.objects.filter(user=user).count()
    total_categories = Category.objects.filter(user=user).count()
    total_tags = Tag.objects.filter(user=user).count()
    favorite_notes = Note.objects.filter(user=user, is_favorite=True).count()
    
    # Notes by difficulty
    difficulty_stats = Note.objects.filter(user=user).values('difficulty').annotate(count=Count('id'))
    
    # Notes by category
    category_stats = Note.objects.filter(user=user).values('category__name', 'category__color').annotate(count=Count('id'))
    
    # Recent activity (last 7 days)
    from django.utils import timezone
    from datetime import timedelta
    
    week_ago = timezone.now() - timedelta(days=7)
    recent_notes = Note.objects.filter(user=user, created_at__gte=week_ago).count()
    
    # Learning progress
    progress, created = LearningProgress.objects.get_or_create(user=user)
    
    return Response({
        'total_notes': total_notes,
        'total_categories': total_categories,
        'total_tags': total_tags,
        'favorite_notes': favorite_notes,
        'recent_notes': recent_notes,
        'difficulty_distribution': list(difficulty_stats),
        'category_distribution': list(category_stats),
        'learning_progress': LearningProgressSerializer(progress).data
    })
