import { useState } from 'react';
import Container from '@cloudscape-design/components/container';
import Header from '@cloudscape-design/components/header';
import SpaceBetween from '@cloudscape-design/components/space-between';
import Button from '@cloudscape-design/components/button';
import Modal from '@cloudscape-design/components/modal';
import FormField from '@cloudscape-design/components/form-field';
import Input from '@cloudscape-design/components/input';
import Box from '@cloudscape-design/components/box';
import Flashbar from '@cloudscape-design/components/flashbar';
import { UserCreate } from '../types';
import { usersApi } from '../services/api';

export default function UsersView() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [formData, setFormData] = useState<UserCreate>({
    name: '',
    email: '',
  });

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

  const handleCreate = async () => {
    try {
      const user = await usersApi.create(formData);
      addNotification('success', 'User created successfully', `User ID: ${user.id}`);
      setShowCreateModal(false);
      resetForm();
    } catch (error: any) {
      addNotification('error', 'Failed to create user', error?.message);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
    });
  };

  return (
    <SpaceBetween size="l">
      <Flashbar items={notifications} />
      <Container
        header={
          <Header
            variant="h1"
            description="Create and manage users"
            actions={
              <Button onClick={() => setShowCreateModal(true)} variant="primary">
                Create user
              </Button>
            }
          >
            Users
          </Header>
        }
      >
        <Box textAlign="center" padding="xxl">
          <SpaceBetween size="m">
            <Box variant="p">
              Create users to register for events. Users can be registered for multiple events.
            </Box>
            <Button onClick={() => setShowCreateModal(true)} variant="primary">
              Create user
            </Button>
          </SpaceBetween>
        </Box>
      </Container>

      <Modal
        visible={showCreateModal}
        onDismiss={() => {
          setShowCreateModal(false);
          resetForm();
        }}
        header="Create user"
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
          <FormField label="Name">
            <Input
              value={formData.name}
              onChange={({ detail }) => setFormData({ ...formData, name: detail.value })}
              placeholder="Enter user name"
            />
          </FormField>
          <FormField label="Email">
            <Input
              type="email"
              value={formData.email}
              onChange={({ detail }) => setFormData({ ...formData, email: detail.value })}
              placeholder="user@example.com"
            />
          </FormField>
        </SpaceBetween>
      </Modal>
    </SpaceBetween>
  );
}
