# Event Management Frontend

A React TypeScript application built with Vite and AWS Cloudscape Design System for managing events, users, and registrations.

## Features

- **Events Management**: Create, view, edit, and delete events
- **User Management**: Create users for event registration
- **Registration Management**: Register users for events, view registrations, and manage waitlists
- **AWS Cloudscape Design**: Professional UI components following AWS design patterns

## Prerequisites

- Node.js 18+ and npm
- Backend API running (see `../backend/README.md`)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure the API endpoint:
```bash
cp .env.example .env
```

Edit `.env` and set your backend API URL:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Build

Create a production build:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── EventsView.tsx   # Events management view
│   │   ├── UsersView.tsx    # Users management view
│   │   └── RegistrationsView.tsx  # Registrations view
│   ├── services/            # API service layer
│   │   └── api.ts           # Backend API client
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts         # Shared types
│   ├── App.tsx              # Main application component
│   └── main.tsx             # Application entry point
├── .env                     # Environment variables
└── package.json             # Dependencies and scripts
```

## Backend Integration

The frontend integrates with the following backend endpoints:

### Events API
- `GET /events` - List all events (with optional status filter)
- `GET /events/{event_id}` - Get event details
- `POST /events` - Create new event
- `PUT /events/{event_id}` - Update event
- `DELETE /events/{event_id}` - Delete event

### Users API
- `POST /users` - Create new user
- `GET /users/{user_id}` - Get user details
- `GET /users/{user_id}/registrations` - Get user's registrations

### Registrations API
- `POST /events/{event_id}/registrations` - Register user for event
- `DELETE /events/{event_id}/registrations/{user_id}` - Unregister user
- `GET /events/{event_id}/registrations` - Get event registrations

## Usage

### Creating an Event
1. Navigate to the Events view
2. Click "Create event"
3. Fill in event details (name, description, date, location, capacity, organizer)
4. Click "Create"

### Creating a User
1. Navigate to the Users view
2. Click "Create user"
3. Enter user name and email
4. Click "Create"
5. Copy the generated User ID for registration

### Registering a User for an Event
1. Navigate to the Registrations view
2. Click "Register user"
3. Enter the User ID and Event ID
4. Click "Register"

### Viewing Event Registrations
1. Navigate to the Registrations view
2. Find the event in the list
3. Click "View registrations"
4. See all registered and waitlisted users

## Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **AWS Cloudscape Design System** - UI components
- **Fetch API** - HTTP client

## Environment Variables

- `VITE_API_BASE_URL` - Backend API base URL (default: `http://localhost:8000`)

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure your backend has CORS properly configured. The backend should allow requests from `http://localhost:5173` during development.

### API Connection Failed
- Verify the backend is running
- Check the `VITE_API_BASE_URL` in `.env` matches your backend URL
- Ensure there are no firewall or network issues

### Build Errors
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`
