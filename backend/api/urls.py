from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

# Create router for viewsets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'notes', views.NoteViewSet, basename='note')
router.register(r'attachments', views.AttachmentViewSet, basename='attachment')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', views.profile, name='profile'),
    
    # Learning progress and stats
    path('progress/', views.learning_progress, name='learning_progress'),
    path('dashboard/', views.dashboard_stats, name='dashboard_stats'),
    
    # Include router URLs
    path('', include(router.urls)),
]
