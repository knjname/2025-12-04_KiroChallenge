import { useState, useEffect } from 'react';
import Container from '@cloudscape-design/components/container';
import Header from '@cloudscape-design/components/header';
import Table from '@cloudscape-design/components/table';
import Button from '@cloudscape-design/components/button';
import SpaceBetween from '@cloudscape-design/components/space-between';
import Box from '@cloudscape-design/components/box';
import Badge from '@cloudscape-design/components/badge';
import Modal from '@cloudscape-design/components/modal';
import FormField from '@cloudscape-design/components/form-field';
import Input from '@cloudscape-design/components/input';
import Flashbar from '@cloudscape-design/components/flashbar';
import { Event, Registration, RegistrationStatus } from '../types';
import { eventsApi, registrationsApi } from '../services/api';

interface RegistrationWithDetails extends Registration {
  eventName?: string;
}

export default function RegistrationsView() {
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [registrations, setRegistrations] = useState<RegistrationWithDetails[]>([]);
  const [loading, setLoading] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [userId, setUserId] = useState('');
  const [eventId, setEventId] = useState('');
  const [notifications, setNotifications] = useState<any[]>([]);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const data = await eventsApi.list();
      setEvents(data);
    } catch (error: any) {
      addNotification('error', 'Failed to load events', error?.message);
    }
  };

  const loadRegistrations = async (event: Event) => {
    setLoading(true);
    setSelectedEvent(event);
    try {
      const data = await registrationsApi.getEventRegistrations(event.id);
      const regsWithDetails = data.registrations.map(reg => ({
        ...reg,
        eventName: event.name,
      }));
      setRegistrations(regsWithDetails);
    } catch (error: any) {
      addNotification('error', 'Failed to load registrations', error?.message);
    } finally {
      setLoading(false);
    }
  };

  const addNotification = (type: string, header: string, content?: string) => {
    setNotifications([
      {
        type,
        header,
        content,
        dismissible: true,
        onDismiss: () => setNotifications([]),
        id: Date.now().toString(),
      },
    ]);
  };

  const handleRegister = async () => {
    try {
      await registrationsApi.register(eventId, userId);
      addNotification('success', 'User registered successfully');
      setShowRegisterModal(false);
      setUserId('');
      setEventId('');
      if (selectedEvent) {
        loadRegistrations(selectedEvent);
      }
    } catch (error: any) {
      addNotification('error', 'Failed to register user', error?.message);
    }
  };

  const handleUnregister = async (registration: Registration) => {
    try {
      await registrationsApi.unregister(registration.eventId, registration.userId);
      addNotification('success', 'User unregistered successfully');
      if (selectedEvent) {
        loadRegistrations(selectedEvent);
      }
    } catch (error: any) {
      addNotification('error', 'Failed to unregister user', error?.message);
    }
  };

  return (
    <SpaceBetween size="l">
      <Flashbar items={notifications} />
      <Container
        header={
          <Header
            variant="h1"
            description="Manage event registrations"
            actions={
              <Button onClick={() => setShowRegisterModal(true)} variant="primary">
                Register user
              </Button>
            }
          >
            Registrations
          </Header>
        }
      >
        <SpaceBetween size="l">
          <Table
            columnDefinitions={[
              {
                id: 'name',
                header: 'Event name',
                cell: (item) => item.name,
              },
              {
                id: 'date',
                header: 'Date',
                cell: (item) => item.date,
              },
              {
                id: 'status',
                header: 'Status',
                cell: (item) => (
                  <Badge
                    color={
                      item.status === 'active'
                        ? 'green'
                        : item.status === 'completed'
                        ? 'blue'
                        : 'red'
                    }
                  >
                    {item.status}
                  </Badge>
                ),
              },
              {
                id: 'actions',
                header: 'Actions',
                cell: (item) => (
                  <Button onClick={() => loadRegistrations(item)}>
                    View registrations
                  </Button>
                ),
              },
            ]}
            items={events}
            loading={loading}
            loadingText="Loading events"
            empty={
              <Box textAlign="center" color="inherit">
                <b>No events</b>
                <Box padding={{ bottom: 's' }} variant="p" color="inherit">
                  No events available.
                </Box>
              </Box>
            }
            header={<Header counter={`(${events.length})`}>Events</Header>}
          />

          {selectedEvent && (
            <Table
              columnDefinitions={[
                {
                  id: 'userId',
                  header: 'User ID',
                  cell: (item) => item.userId,
                },
                {
                  id: 'status',
                  header: 'Status',
                  cell: (item) => (
                    <Badge
                      color={
                        item.status === 'registered'
                          ? 'green'
                          : item.status === 'waitlisted'
                          ? 'blue'
                          : 'grey'
                      }
                    >
                      {item.status}
                    </Badge>
                  ),
                },
                {
                  id: 'registeredAt',
                  header: 'Registered at',
                  cell: (item) => new Date(item.registeredAt).toLocaleString(),
                },
                {
                  id: 'waitlistPosition',
                  header: 'Waitlist position',
                  cell: (item) => item.waitlistPosition || '-',
                },
                {
                  id: 'actions',
                  header: 'Actions',
                  cell: (item) => (
                    <Button onClick={() => handleUnregister(item)}>
                      Unregister
                    </Button>
                  ),
                },
              ]}
              items={registrations}
              loading={loading}
              loadingText="Loading registrations"
              empty={
                <Box textAlign="center" color="inherit">
                  <b>No registrations</b>
                  <Box padding={{ bottom: 's' }} variant="p" color="inherit">
                    No registrations for this event.
                  </Box>
                </Box>
              }
              header={
                <Header counter={`(${registrations.length})`}>
                  Registrations for {selectedEvent.name}
                </Header>
              }
            />
          )}
        </SpaceBetween>
      </Container>

      <Modal
        visible={showRegisterModal}
        onDismiss={() => {
          setShowRegisterModal(false);
          setUserId('');
          setEventId('');
        }}
        header="Register user for event"
        footer={
          <Box float="right">
            <SpaceBetween direction="horizontal" size="xs">
              <Button
                variant="link"
                onClick={() => {
                  setShowRegisterModal(false);
                  setUserId('');
                  setEventId('');
                }}
              >
                Cancel
              </Button>
              <Button variant="primary" onClick={handleRegister}>
                Register
              </Button>
            </SpaceBetween>
          </Box>
        }
      >
        <SpaceBetween size="m">
          <FormField label="User ID">
            <Input
              value={userId}
              onChange={({ detail }) => setUserId(detail.value)}
              placeholder="Enter user ID"
            />
          </FormField>
          <FormField label="Event ID">
            <Input
              value={eventId}
              onChange={({ detail }) => setEventId(detail.value)}
              placeholder="Enter event ID"
            />
          </FormField>
        </SpaceBetween>
      </Modal>
    </SpaceBetween>
  );
}
