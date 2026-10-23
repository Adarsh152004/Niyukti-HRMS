import React from 'react';
import { RouterProvider, useRouter } from './context/RouterContext';
import { Navigation } from './components/Navigation';
import { Footer } from './components/Footer';
import { HomePage } from './pages/HomePage';
import { ServicesPage } from './pages/ServicesPage';
import { WorkPage } from './pages/WorkPage';
import { AboutPage } from './pages/AboutPage';
import { CareersPage } from './pages/CareersPage';
import { JobDetailPage } from './pages/JobDetailPage';
import { ContactPage } from './pages/ContactPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { AdminPage } from './pages/AdminPage';

function AppContent() {
  const { route, params, navigate } = useRouter();

  const handleOpenCaseStudy = (caseId: string) => {
    navigate(`/work`);
  };

  const handleOpenJobDetail = (jobId: string) => {
    navigate(`/careers/${jobId}`);
  };

  // Helper setter compatible with components expecting setActiveTab(tab)
  const handleSetActiveTab = (tab: string) => {
    navigate(tab);
  };

  // Admin route — full-screen, no nav/footer
  if (route === 'admin') {
    return <AdminPage />;
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#F8FAFC] text-[#0F172A]">
      
      {/* Top Header Navigation with URL Route Sync */}
      <Navigation 
        activeTab={route === 'job-detail' ? 'careers' : route} 
        setActiveTab={handleSetActiveTab}
        onOpenJobDetail={handleOpenJobDetail}
      />

      {/* Dynamic Routed Main View */}
      <main className="flex-1">
        {route === 'home' && (
          <HomePage 
            setActiveTab={handleSetActiveTab} 
            onOpenCaseStudy={handleOpenCaseStudy}
            onOpenJobDetail={handleOpenJobDetail}
          />
        )}
        
        {route === 'services' && (
          <ServicesPage 
            setActiveTab={handleSetActiveTab} 
          />
        )}

        {route === 'work' && (
          <WorkPage 
            setActiveTab={handleSetActiveTab}
            selectedCaseId={params.caseId || null}
            onClearSelectedCase={() => navigate('/work')}
          />
        )}

        {route === 'about' && (
          <AboutPage 
            setActiveTab={handleSetActiveTab} 
          />
        )}

        {route === 'careers' && (
          <CareersPage 
            setActiveTab={handleSetActiveTab}
            onOpenJobDetail={handleOpenJobDetail}
          />
        )}

        {route === 'job-detail' && (
          <JobDetailPage 
            jobId={params.jobId || 'senior-fullstack-web-architect'}
            setActiveTab={handleSetActiveTab}
          />
        )}

        {route === 'contact' && (
          <ContactPage 
            setActiveTab={handleSetActiveTab} 
          />
        )}

        {route === 'not-found' && (
          <NotFoundPage />
        )}
      </main>

      {/* Global Studio Footer */}
      <Footer setActiveTab={handleSetActiveTab} />

    </div>
  );
}

export function App() {
  return (
    <RouterProvider>
      <AppContent />
    </RouterProvider>
  );
}

export default App;
