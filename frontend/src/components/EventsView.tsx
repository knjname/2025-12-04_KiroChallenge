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
import Select from '@cloudscape-design/components/select';
import Textarea from '@cloudscape-design/components/textarea';
import Flashbar from '@cloudscape-design/components/flashbar';
import { Event, EventCreate } from '../types';
import { eventsApi } from '../services/api';

export default function EventsView() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedItems, setSelectedItems] = useState<Event[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [formData, setFormData] = useState<EventCreate>({
    name: '',
    description: '',
    date: '',
    location: '',
    capacity: 0,
    organizer: '',
    status: 'active',
  });

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    setLoading(true);
    try {
      const data = await eventsApi.list();
      setEvents(data);
    } catch (error) {
      addNotification('error', 'Failed to load events', error);
    } finally {
      setLoading(false);
    }
  };

  const addNotification = (type: string, header: string, error?: any) => {
    setNotifications([
      {
        type,
        header,
        content: error?.message || '',
        dismissible: true,
        onDismiss: () => setNotifications([]),
        id: Date.now().toString(),
      },
    ]);
  };

  const handleCreate = async () => {
    try {
      await eventsApi.create(formData);
      addNotification('success', 'Event created successfully');
      setShowCreateModal(false);
      resetForm();
      loadEvents();
    } catch (error) {
      addNotification('error', 'Failed to create event', error);
    }
  };

  const handleUpdate = async () => {
    if (selectedItems.length === 0) return;
    try {
      await eventsApi.update(selectedItems[0].id, formData);
      addNotification('success', 'Event updated successfully');
      setShowEditModal(false);
      resetForm();
      loadEvents();
    } catch (error) {
      addNotification('error', 'Failed to update event', error);
    }
  };

  const handleDelete = async () => {
    if (selectedItems.length === 0) return;
    try {
      await eventsApi.delete(selectedItems[0].id);
      addNotification('success', 'Event deleted successfully');
      setSelectedItems([]);
      loadEvents();
    } catch (error) {
      addNotification('error', 'Failed to delete event', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      date: '',
      location: '',
      capacity: 0,
      organizer: '',
      status: 'active',
    });
  };

  const openEditModal = () => {
    if (selectedItems.length > 0) {
      const event = selectedItems[0];
      setFormData({
        name: event.name,
        description: event.description,
        date: event.date,
        location: event.location,
        capacity: event.capacity,
        organizer: event.organizer,
        status: event.status,
      });
      setShowEditModal(true);
    }
  };

  return (
    <SpaceBetween size="l">
      <Flashbar items={notifications} />
      <Container
        header={
          <Header
            variant="h1"
            description="Manage events, users, and registrations"
            actions={
              <SpaceBetween direction="horizontal" size="xs">
                <Button onClick={loadEvents} iconName="refresh">
                  Refresh
                </Button>
                <Button onClick={() => setShowCreateModal(true)} variant="primary">
                  Create event
                </Button>
              </SpaceBetween>
            }
          >
            Event Management
          </Header>
        }
      >
        <Table
          columnDefinitions={[
            {
              id: 'name',
              header: 'Event name',
              cell: (item) => item.name,
              sortingField: 'name',
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
              id: 'date',
              header: 'Event date',
              cell: (item) => item.date,
              sortingField: 'date',
            },
            {
              id: 'capacity',
              header: 'Capacity',
              cell: (item) => item.capacity,
            },
            {
              id: 'location',
              header: 'Location',
              cell: (item) => item.location,
            },
            {
              id: 'organizer',
              header: 'Organizer',
              cell: (item) => item.organizer,
            },
          ]}
          items={events}
          loading={loading}
          loadingText="Loading events"
          selectionType="single"
          selectedItems={selectedItems}
          onSelectionChange={({ detail }) => setSelectedItems(detail.selectedItems)}
          empty={
            <Box textAlign="center" color="inherit">
              <b>No events</b>
              <Box padding={{ bottom: 's' }} variant="p" color="inherit">
                No events to display.
              </Box>
              <Button onClick={() => setShowCreateModal(true)}>Create event</Button>
            </Box>
          }
          header={
            <Header
              counter={`(${events.length})`}
              actions={
                <SpaceBetween direction="horizontal" size="xs">
                  <Button
                    disabled={selectedItems.length === 0}
                    onClick={openEditModal}
                  >
                    Edit
                  </Button>
                  <Button
                    disabled={selectedItems.length === 0}
                    onClick={handleDelete}
                  >
                    Delete
                  </Button>
                </SpaceBetween>
              }
            >
              Events
            </Header>
          }
        />
      </Container>

      <Modal
        visible={showCreateModal}
        onDismiss={() => {
          setShowCreateModal(false);
          resetForm();
        }}
        header="Create event"
        footer={
          <Box float="right">
            <SpaceBetween direction="horizontal" size="xs">
              <Button
                variant="link"
                onClick={() => {
                  setShowCreateModal(false);
                  resetForm();
                }}
              >
                Cancel
              </Button>
              <Button variant="primary" onClick={handleCreate}>
                Create
              </Button>
            </SpaceBetween>
          </Box>
        }
      >
        <SpaceBetween size="m">
          <FormField label="Event name">
            <Input
              value={formData.name}
              onChange={({ detail }) => setFormData({ ...formData, name: detail.value })}
            />
          </FormField>
          <FormField label="Description">
            <Textarea
              value={formData.description}
              onChange={({ detail }) => setFormData({ ...formData, description: detail.value })}
            />
          </FormField>
          <FormField label="Date">
            <Input
              type="date"
              value={formData.date}
              onChange={({ detail }) => setFormData({ ...formData, date: detail.value })}
            />
          </FormField>
          <FormField label="Location">
            <Input
              value={formData.location}
              onChange={({ detail }) => setFormData({ ...formData, location: detail.value })}
            />
          </FormField>
          <FormField label="Capacity">
            <Input
              type="number"
              value={formData.capacity.toString()}
              onChange={({ detail }) => setFormData({ ...formData, capacity: parseInt(detail.value) || 0 })}
            />
          </FormField>
          <FormField label="Organizer">
            <Input
              value={formData.organizer}
              onChange={({ detail }) => setFormData({ ...formData, organizer: detail.value })}
            />
          </FormField>
          <FormField label="Status">
            <Select
              selectedOption={{ label: formData.status || 'active', value: formData.status || 'active' }}
              onChange={({ detail }) =>
                setFormData({ ...formData, status: detail.selectedOption.value as any })
              }
              options={[
                { label: 'active', value: 'active' },
                { label: 'completed', value: 'completed' },
                { label: 'cancelled', value: 'cancelled' },
              ]}
            />
          </FormField>
        </SpaceBetween>
      </Modal>

      <Modal
        visible={showEditModal}
        onDismiss={() => {
          setShowEditModal(false);
          resetForm();
        }}
        header="Edit event"
        footer={
          <Box float="right">
            <SpaceBetween direction="horizontal" size="xs">
              <Button
                variant="link"
                onClick={() => {
                  setShowEditModal(false);
                  resetForm();
                }}
              >
                Cancel
              </Button>
              <Button variant="primary" onClick={handleUpdate}>
                Update
              </Button>
            </SpaceBetween>
          </Box>
        }
      >
        <SpaceBetween size="m">
          <FormField label="Event name">
            <Input
              value={formData.name}
              onChange={({ detail }) => setFormData({ ...formData, name: detail.value })}
            />
          </FormField>
          <FormField label="Description">
            <Textarea
              value={formData.description}
              onChange={({ detail }) => setFormData({ ...formData, description: detail.value })}
            />
          </FormField>
          <FormField label="Date">
            <Input
              type="date"
              value={formData.date}
              onChange={({ detail }) => setFormData({ ...formData, date: detail.value })}
            />
          </FormField>
          <FormField label="Location">
            <Input
              value={formData.location}
              onChange={({ detail }) => setFormData({ ...formData, location: detail.value })}
            />
          </FormField>
          <FormField label="Capacity">
            <Input
              type="number"
              value={formData.capacity.toString()}
              onChange={({ detail }) => setFormData({ ...formData, capacity: parseInt(detail.value) || 0 })}
            />
          </FormField>
          <FormField label="Organizer">
            <Input
              value={formData.organizer}
              onChange={({ detail }) => setFormData({ ...formData, organizer: detail.value })}
            />
          </FormField>
          <FormField label="Status">
            <Select
              selectedOption={{ label: formData.status || 'active', value: formData.status || 'active' }}
              onChange={({ detail }) =>
                setFormData({ ...formData, status: detail.selectedOption.value as any })
              }
              options={[
                { label: 'active', value: 'active' },
                { label: 'completed', value: 'completed' },
                { label: 'cancelled', value: 'cancelled' },
              ]}
            />
          </FormField>
        </SpaceBetween>
      </Modal>
    </SpaceBetween>
  );
}
