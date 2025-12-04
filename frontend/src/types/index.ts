export interface Event {
  id: string;
  name: string;
  description: string;
  date: string;
  location: string;
  capacity: number;
  organizer: string;
  status: 'active' | 'completed' | 'cancelled';
  createdAt: string;
  updatedAt: string;
}

export interface EventCreate {
  name: string;
  description: string;
  date: string;
  location: string;
  capacity: number;
  organizer: string;
  status?: 'active' | 'completed' | 'cancelled';
}

export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: string;
}

export interface UserCreate {
  name: string;
  email: string;
}

export interface Registration {
  userId: string;
  eventId: string;
  status: 'registered' | 'waitlisted' | 'cancelled';
  registeredAt: string;
  waitlistPosition?: number;
}

export interface RegistrationStatus {
  eventId: string;
  totalRegistered: number;
  totalWaitlisted: number;
  registrations: Registration[];
}
