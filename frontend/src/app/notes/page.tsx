'use client';

import React, { useEffect, useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import { apiClient } from '@/lib/api';
import { Category, NoteList, Tag } from '@/types';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';

export default function NotesPage() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  const [notes, setNotes] = useState<NoteList[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [summary, setSummary] = useState('');
  const [category, setCategory] = useState<number | ''>('');
  const [difficulty, setDifficulty] = useState('beginner');
  const [loadingData, setLoadingData] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, loading, router]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [notesRes, categoriesRes, tagsRes] = await Promise.all([
          apiClient.getNotes(),
          apiClient.getCategories(),
          apiClient.getTags(),
        ]);

        setNotes(notesRes.results || notesRes);
        setCategories(categoriesRes);
        setTags(tagsRes);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoadingData(false);
      }
    };

    if (isAuthenticated) {
      fetchData();
    }
  }, [isAuthenticated]);

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim() || !category) return;

    setSubmitting(true);
    try {
      await apiClient.createNote({
        title,
        content,
        summary,
        category: Number(category),
        tag_ids: [],
        difficulty: difficulty as any,
        is_favorite: false,
        is_archived: false,
        source_url: '',
      });

      const updatedNotes = await apiClient.getNotes();
      setNotes(updatedNotes.results || updatedNotes);

      // Reset form
      setTitle('');
      setContent('');
      setSummary('');
      setCategory('');
      setDifficulty('beginner');
    } catch (error) {
      console.error('Error creating note:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading || loadingData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <MainLayout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Create Note Form */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Create New Note</h2>
            <form className="space-y-4" onSubmit={handleCreateNote}>
              <Input
                label="Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
              <Textarea
                label="Content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={6}
                required
              />
              <Textarea
                label="Summary"
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                rows={3}
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={category}
                  onChange={(e) => setCategory(Number(e.target.value))}
                  required
                >
                  <option value="">Select a category</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Difficulty</label>
                <select
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <Button type="submit" loading={submitting} className="w-full">
                Create Note
              </Button>
            </form>
          </div>
        </div>

        {/* Notes List */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Your Notes</h2>
            {notes.length === 0 ? (
              <p className="text-gray-600">No notes yet. Create your first note!</p>
            ) : (
              <div className="space-y-4">
                {notes.map((note) => (
                  <div key={note.id} className="border border-gray-200 rounded-md p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">{note.title}</h3>
                        <p className="text-gray-600 text-sm">{note.summary || 'No summary'}</p>
                        <div className="mt-2 text-xs text-gray-500">
                          <span className="capitalize">{note.difficulty}</span>
                          <span className="mx-2">•</span>
                          <span>Category: {note.category_name}</span>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={async () => {
                            await apiClient.markReviewed(note.id);
                            const stats = await apiClient.getDashboardStats();
                            console.log('Updated progress:', stats.learning_progress);
                          }}
                        >
                          Mark Reviewed
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={async () => {
                            const res = await apiClient.toggleFavorite(note.id);
                            const updatedNotes = await apiClient.getNotes();
                            setNotes(updatedNotes.results || updatedNotes);
                          }}
                        >
                          Toggle Favorite
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}

