'use client';

import React, { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import { DashboardStats } from '@/types';

const DashboardStatsComponent: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiClient.getDashboardStats();
        setStats(data);
      } catch (err: any) {
        console.error('Error fetching dashboard stats:', err);
        setError('Failed to load dashboard statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow p-6">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!stats) return null;

  const statCards = [
    {
      title: 'Total Notes',
      value: stats.total_notes,
      icon: '📝',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Categories',
      value: stats.total_categories,
      icon: '📁',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Tags',
      value: stats.total_tags,
      icon: '🏷️',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      title: 'Favorites',
      value: stats.favorite_notes,
      icon: '⭐',
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <div
            key={card.title}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className={`flex-shrink-0 ${card.bgColor} rounded-md p-2`}>
                  <span className="text-2xl">{card.icon}</span>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {card.title}
                    </dt>
                    <dd className={`text-lg font-medium ${card.color}`}>
                      {card.value}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Learning Progress */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Learning Progress
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {stats.learning_progress.current_streak}
            </div>
            <div className="text-sm text-gray-500">Day Streak</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {stats.learning_progress.longest_streak}
            </div>
            <div className="text-sm text-gray-500">Longest Streak</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {stats.learning_progress.notes_reviewed_today}
            </div>
            <div className="text-sm text-gray-500">Reviewed Today</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      {stats.recent_notes > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Recent Activity
          </h3>
          <p className="text-gray-600">
            You've created {stats.recent_notes} notes in the last 7 days. Keep it up!
          </p>
        </div>
      )}

      {/* Difficulty Distribution */}
      {stats.difficulty_distribution.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Notes by Difficulty
          </h3>
          <div className="space-y-3">
            {stats.difficulty_distribution.map((item) => (
              <div key={item.difficulty} className="flex items-center">
                <div className="w-20 text-sm text-gray-600 capitalize">
                  {item.difficulty}
                </div>
                <div className="flex-1 bg-gray-200 rounded-full h-2 ml-4">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{
                      width: `${(item.count / stats.total_notes) * 100}%`,
                    }}
                  ></div>
                </div>
                <div className="w-12 text-sm text-gray-900 text-right ml-4">
                  {item.count}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardStatsComponent;
