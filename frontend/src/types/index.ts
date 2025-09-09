export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
}

export interface Category {
  id: number;
  name: string;
  description: string;
  color: string;
  notes_count: number;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: number;
  name: string;
  notes_count: number;
  created_at: string;
}

export interface Attachment {
  id: number;
  file: string;
  original_name: string;
  file_type: 'image' | 'document' | 'video' | 'audio' | 'other';
  file_size: number;
  file_size_display: string;
  description: string;
  uploaded_at: string;
}

export interface Note {
  id: number;
  title: string;
  content: string;
  summary: string;
  category: number;
  category_name: string;
  tags: Tag[];
  tag_ids: number[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  is_favorite: boolean;
  is_archived: boolean;
  source_url: string;
  attachments: Attachment[];
  created_at: string;
  updated_at: string;
  last_reviewed: string | null;
}

export interface NoteList {
  id: number;
  title: string;
  summary: string;
  category_name: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  is_favorite: boolean;
  is_archived: boolean;
  tags_count: number;
  created_at: string;
  updated_at: string;
}

export interface LearningProgress {
  username: string;
  total_notes: number;
  notes_reviewed_today: number;
  current_streak: number;
  longest_streak: number;
  last_activity_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total_notes: number;
  total_categories: number;
  total_tags: number;
  favorite_notes: number;
  recent_notes: number;
  difficulty_distribution: Array<{ difficulty: string; count: number }>;
  category_distribution: Array<{ category__name: string; category__color: string; count: number }>;
  learning_progress: LearningProgress;
}

export interface AuthTokens {
  access: string;
  refresh: string;
  user: User;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
