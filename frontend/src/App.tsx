import { useState, useEffect } from 'react';
import AppLayout from '@cloudscape-design/components/app-layout';
import TopNavigation from '@cloudscape-design/components/top-navigation';
import SideNavigation from '@cloudscape-design/components/side-navigation';
import '@cloudscape-design/global-styles/index.css';
import EventsView from './components/EventsView';
import UsersView from './components/UsersView';
import RegistrationsView from './components/RegistrationsView';

type View = 'events' | 'users' | 'registrations';

function App() {
  const [activeView, setActiveView] = useState<View>('events');
  const [navigationOpen, setNavigationOpen] = useState(true);

  return (
    <>
      <TopNavigation
        identity={{
          href: '#',
          title: 'Event Management',
        }}
        utilities={[
          {
            type: 'button',
            text: 'Documentation',
            href: '#',
            external: true,
            externalIconAriaLabel: ' (opens in a new tab)',
          },
        ]}
      />
      <AppLayout
        navigationOpen={navigationOpen}
        onNavigationChange={({ detail }) => setNavigationOpen(detail.open)}
        navigation={
          <SideNavigation
            header={{ text: 'Event Management', href: '#' }}
            activeHref={`#${activeView}`}
            onFollow={(event) => {
              event.preventDefault();
              const view = event.detail.href.replace('#', '') as View;
              setActiveView(view);
            }}
            items={[
              { type: 'link', text: 'Events', href: '#events' },
              { type: 'link', text: 'Users', href: '#users' },
              { type: 'link', text: 'Registrations', href: '#registrations' },
            ]}
          />
        }
        content={
          <>
            {activeView === 'events' && <EventsView />}
            {activeView === 'users' && <UsersView />}
            {activeView === 'registrations' && <RegistrationsView />}
          </>
        }
        toolsHide
      />
    </>
  );
}

export default App;
