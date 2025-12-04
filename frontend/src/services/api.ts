import { Event, EventCreate, User, UserCreate, Registration, RegistrationStatus } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }
  return response.json();
}

// Events API
export const eventsApi = {
  list: async (statusFilter?: string): Promise<Event[]> => {
    const url = statusFilter 
      ? `${API_BASE_URL}/events?status=${statusFilter}`
      : `${API_BASE_URL}/events`;
    const response = await fetch(url);
    return handleResponse<Event[]>(response);
  },

  get: async (eventId: string): Promise<Event> => {
    const response = await fetch(`${API_BASE_URL}/events/${eventId}`);
    return handleResponse<Event>(response);
  },

  create: async (event: EventCreate): Promise<Event> => {
    const response = await fetch(`${API_BASE_URL}/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event),
    });
    return handleResponse<Event>(response);
  },

  update: async (eventId: string, event: Partial<EventCreate>): Promise<Event> => {
    const response = await fetch(`${API_BASE_URL}/events/${eventId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event),
    });
    return handleResponse<Event>(response);
  },

  delete: async (eventId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/events/${eventId}`, {
      method: 'DELETE',
    });
    await handleResponse<{ message: string }>(response);
  },
};

// Users API
export const usersApi = {
  create: async (user: UserCreate): Promise<User> => {
    const response = await fetch(`${API_BASE_URL}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(user),
    });
    return handleResponse<User>(response);
  },

  get: async (userId: string): Promise<User> => {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`);
    return handleResponse<User>(response);
  },

  getRegistrations: async (userId: string): Promise<Event[]> => {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/registrations`);
    return handleResponse<Event[]>(response);
  },
};

// Registrations API
export const registrationsApi = {
  register: async (eventId: string, userId: string): Promise<Registration> => {
    const response = await fetch(`${API_BASE_URL}/events/${eventId}/registrations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId }),
    });
    return handleResponse<Registration>(response);
  },

  unregister: async (eventId: string, userId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/events/${eventId}/registrations/${userId}`, {
      method: 'DELETE',
    });
    await handleResponse<{ message: string }>(response);
  },

  getEventRegistrations: async (eventId: string): Promise<RegistrationStatus> => {
    const response = await fetch(`${API_BASE_URL}/events/${eventId}/registrations`);
    return handleResponse<RegistrationStatus>(response);
  },
};
