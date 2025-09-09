import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';
import { 
  AuthTokens, 
  LoginCredentials, 
  RegisterData, 
  User, 
  Category, 
  Tag, 
  Note, 
  NoteList, 
  DashboardStats,
  LearningProgress,
  PaginatedResponse
} from '@/types';

class ApiClient {
  private client: AxiosInstance;
  private baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

  constructor() {
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = Cookies.get('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          const refreshToken = Cookies.get('refresh_token');
          if (refreshToken) {
            try {
              const response = await axios.post(`${this.baseURL}/auth/refresh/`, {
                refresh: refreshToken,
              });
              
              const { access } = response.data;
              Cookies.set('access_token', access);
              originalRequest.headers.Authorization = `Bearer ${access}`;
              
              return this.client(originalRequest);
            } catch (refreshError) {
              // Refresh token is invalid, logout user
              Cookies.remove('access_token');
              Cookies.remove('refresh_token');
              Cookies.remove('user');
              window.location.href = '/auth/login';
              return Promise.reject(refreshError);
            }
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await this.client.post('/auth/login/', credentials);
    const tokens = response.data;
    
    // Store tokens in cookies
    Cookies.set('access_token', tokens.access);
    Cookies.set('refresh_token', tokens.refresh);
    Cookies.set('user', JSON.stringify(tokens.user));
    
    return tokens;
  }

  async register(userData: RegisterData): Promise<AuthTokens> {
    const response = await this.client.post('/auth/register/', userData);
    const tokens = response.data;
    
    // Store tokens in cookies
    Cookies.set('access_token', tokens.access);
    Cookies.set('refresh_token', tokens.refresh);
    Cookies.set('user', JSON.stringify(tokens.user));
    
    return tokens;
  }

  async logout(): Promise<void> {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    Cookies.remove('user');
  }

  async getProfile(): Promise<User> {
    const response = await this.client.get('/auth/profile/');
    return response.data;
  }

  // Categories
  async getCategories(): Promise<Category[]> {
    const response = await this.client.get('/categories/');
    return response.data.results || response.data;
  }

  async createCategory(category: Omit<Category, 'id' | 'created_at' | 'updated_at' | 'notes_count'>): Promise<Category> {
    const response = await this.client.post('/categories/', category);
    return response.data;
  }

  async updateCategory(id: number, category: Partial<Category>): Promise<Category> {
    const response = await this.client.put(`/categories/${id}/`, category);
    return response.data;
  }

  async deleteCategory(id: number): Promise<void> {
    await this.client.delete(`/categories/${id}/`);
  }

  // Tags
  async getTags(): Promise<Tag[]> {
    const response = await this.client.get('/tags/');
    return response.data.results || response.data;
  }

  async createTag(tag: Omit<Tag, 'id' | 'created_at' | 'notes_count'>): Promise<Tag> {
    const response = await this.client.post('/tags/', tag);
    return response.data;
  }

  async updateTag(id: number, tag: Partial<Tag>): Promise<Tag> {
    const response = await this.client.put(`/tags/${id}/`, tag);
    return response.data;
  }

  async deleteTag(id: number): Promise<void> {
    await this.client.delete(`/tags/${id}/`);
  }

  // Notes
  async getNotes(params?: { page?: number; search?: string; category?: number; difficulty?: string }): Promise<PaginatedResponse<NoteList>> {
    const response = await this.client.get('/notes/', { params });
    return response.data;
  }

  async getNote(id: number): Promise<Note> {
    const response = await this.client.get(`/notes/${id}/`);
    return response.data;
  }

  async createNote(note: Omit<Note, 'id' | 'created_at' | 'updated_at' | 'last_reviewed' | 'category_name' | 'tags' | 'attachments'>): Promise<Note> {
    const response = await this.client.post('/notes/', note);
    return response.data;
  }

  async updateNote(id: number, note: Partial<Note>): Promise<Note> {
    const response = await this.client.put(`/notes/${id}/`, note);
    return response.data;
  }

  async deleteNote(id: number): Promise<void> {
    await this.client.delete(`/notes/${id}/`);
  }

  async toggleFavorite(id: number): Promise<{ is_favorite: boolean }> {
    const response = await this.client.post(`/notes/${id}/toggle_favorite/`);
    return response.data;
  }

  async toggleArchive(id: number): Promise<{ is_archived: boolean }> {
    const response = await this.client.post(`/notes/${id}/toggle_archive/`);
    return response.data;
  }

  async markReviewed(id: number): Promise<{ status: string }> {
    const response = await this.client.post(`/notes/${id}/mark_reviewed/`);
    return response.data;
  }

  async getFavoriteNotes(): Promise<PaginatedResponse<NoteList>> {
    const response = await this.client.get('/notes/favorites/');
    return response.data;
  }

  async getRecentNotes(): Promise<NoteList[]> {
    const response = await this.client.get('/notes/recent/');
    return response.data;
  }

  async searchNotes(query: string, filters?: { category?: number; difficulty?: string; tags?: number[] }): Promise<PaginatedResponse<NoteList>> {
    const params = { q: query, ...filters };
    const response = await this.client.get('/notes/search/', { params });
    return response.data;
  }

  // Dashboard and Progress
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.client.get('/dashboard/');
    return response.data;
  }

  async getLearningProgress(): Promise<LearningProgress> {
    const response = await this.client.get('/progress/');
    return response.data;
  }

  // File uploads
  async uploadAttachment(noteId: number, file: File, description?: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('note_id', noteId.toString());
    if (description) {
      formData.append('description', description);
    }

    const response = await this.client.post('/attachments/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
