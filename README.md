# Learning Management App

A comprehensive learning management system built with Django (backend) and Next.js (frontend) that allows you to organize, track, and manage your learning journey.

## Features

- **User Authentication**: Register and login with JWT authentication
- **Note Management**: Create, edit, and organize learning notes
- **Categories**: Organize notes by custom categories with color coding
- **Tags**: Tag notes for better organization and searching
- **Learning Progress**: Track your learning streaks and daily progress
- **Dashboard**: View statistics and progress overview
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

### Backend (Django)
- Django 5.2.6
- Django REST Framework
- JWT Authentication
- SQLite Database
- CORS Headers
- File Upload Support

### Frontend (Next.js)
- Next.js 14 with TypeScript
- Tailwind CSS for styling
- Axios for API calls
- Cookie-based authentication
- Responsive UI components

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

The Django backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The Next.js frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile

### Categories
- `GET /api/categories/` - List user's categories
- `POST /api/categories/` - Create a new category
- `PUT /api/categories/{id}/` - Update a category
- `DELETE /api/categories/{id}/` - Delete a category

### Tags
- `GET /api/tags/` - List user's tags
- `POST /api/tags/` - Create a new tag
- `PUT /api/tags/{id}/` - Update a tag
- `DELETE /api/tags/{id}/` - Delete a tag

### Notes
- `GET /api/notes/` - List user's notes (paginated)
- `POST /api/notes/` - Create a new note
- `GET /api/notes/{id}/` - Get a specific note
- `PUT /api/notes/{id}/` - Update a note
- `DELETE /api/notes/{id}/` - Delete a note
- `POST /api/notes/{id}/toggle_favorite/` - Toggle favorite status
- `POST /api/notes/{id}/toggle_archive/` - Toggle archive status
- `POST /api/notes/{id}/mark_reviewed/` - Mark note as reviewed
- `GET /api/notes/favorites/` - Get favorite notes
- `GET /api/notes/recent/` - Get recently created notes
- `GET /api/notes/search/` - Search notes

### Dashboard
- `GET /api/dashboard/` - Get dashboard statistics
- `GET /api/progress/` - Get learning progress

## Usage

1. **Register/Login**: Create an account or login with existing credentials
2. **Create Categories**: Organize your learning topics into categories
3. **Create Notes**: Add learning notes with content, summaries, and classifications
4. **Track Progress**: Mark notes as reviewed to track your learning progress
5. **Dashboard**: View your learning statistics and progress

## Development

### Backend Development
- The Django project uses REST Framework for API endpoints
- Models are defined in `api/models.py`
- API views are in `api/views.py`
- Serializers are in `api/serializers.py`

### Frontend Development
- React components are organized in `src/components/`
- API client is in `src/lib/api.ts`
- Type definitions are in `src/types/index.ts`
- Custom hooks are in `src/hooks/`

## Environment Variables

### Backend (.env)
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend
The frontend uses the default API URL `http://localhost:8000/api`. You can override this by setting:
```
NEXT_PUBLIC_API_URL=http://your-api-url.com/api
```

## Future Enhancements

- Rich text editor for note content
- File upload and attachment support
- Advanced search and filtering
- Note export functionality
- Learning goals and objectives
- Spaced repetition system
- Mobile app version
- Collaboration features

## License

This project is open source and available under the MIT License.
